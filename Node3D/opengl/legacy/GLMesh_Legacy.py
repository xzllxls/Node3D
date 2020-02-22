import pyqtgraph.opengl as gl
import numpy as np
from Framework.vendor.NodeGraphQt import QtGui, QtCore
from pyqtgraph import functions as fn
from Framework.opengl.legacy.OBJLoader import OBJLoader
from pyqtgraph.opengl.shaders import ShaderProgram, VertexShader, FragmentShader
from OpenGL.GL import *
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

def _vertexNormalFromFace(vts, faceNorms, vertFaces):
    result = np.empty(vts.shape, dtype=np.float32)
    for idx in range(vts.shape[0]):
        faces = vertFaces[idx]
        if len(faces) == 0:
            result[idx] = (0, 0, 0)
            continue
        norms = faceNorms[faces]  ## get all face normals
        norm = norms.sum(axis=0)  ## sum normals
        norm /= np.sqrt((norm ** 2).sum())  ## and re-normalize
        result[idx] = norm
    return result


class MeshData(object):
    def __init__(self, mesh=None):
        self.mesh = mesh

    # ------functions used when attribute is not expanded-----

    def vertexByFace(self):
        """
        Return an array (Nf*3, 3) of vertex positions
        """
        vts = self.mesh.getVertexes()
        fcs = self.mesh.getFaces()
        if vts is None or fcs is None:
            return None
        return vts[fcs.flatten()]

    def colorByFace(self):
        """
        Return an array (Nf*3, 3) of vertex colors
        """
        vts = self.mesh.getColors()
        fcs = self.mesh.getFaces()
        if vts is None or fcs is None:
            return None
        return vts[fcs.flatten()]

    def normalByFace(self):
        """
        Return an array (Nf*3, 3) of vertex normals
        """
        vts = self.mesh.getNormals()
        fcs = self.mesh.getFaces()
        if vts is None or fcs is None:
            return None
        return vts[fcs.flatten()]

    def vertexAttribByFace(self, level, name):
        """
        Return an array (Nf*3, dim) of vertex attributes
        """
        vts = self.mesh.getAttributeData(level, name)
        fcs = self.mesh.getFaces()
        if vts is None or fcs is None:
            return None
        return vts[fcs.flatten()]

    # ------functions used when attribute has been expanded-----

    def vertexFaces(self):
        """
        return: dict of (Nv):
            {vertex_index: [face_index1,face_index2,...]}
        """
        fcs = self.mesh.getFaces()
        if fcs is None:
            return None

        result = {}
        for idx, face in enumerate(fcs):
            for vt in face:
                if vt in result.keys():
                    result[vt].append(idx)
                else:
                    result[vt] = [idx]

        return result

    def vertexEdges(self):
        """
        return: dict of (Nv):
            {vertex_index: [edge_index1,edge_index2,...]}
        """
        fcs = self.mesh.getEdges()
        if fcs is None:
            return None

        result = {}
        for idx, edge in enumerate(fcs):
            for vt in edge:
                if vt in result.keys():
                    result[vt].append(idx)
                else:
                    result[vt] = [idx]

        return result

    def getEdges(self):
        """
        Return an array (Nf*3, 2) of edges,
        the two values are the index of vertices
        """
        fcs = self.mesh.getFaces()
        if fcs is None:
            return None
        edges = []
        for face in fcs:
            num = len(face)
            for idx in range(num):
                if idx == num - 1:
                    edges.append([face[idx], face[0]])
                else:
                    edges.append([face[idx], face[idx + 1]])
        return np.array(edges, dtype=np.uint32)

    def faceNormals(self, apply=False):
        """
        Return an array (Nf, 3) of face normals
        """
        vts = self.mesh.getVertexes()
        fcs = self.mesh.getFaces()
        if vts is None or fcs is None:
            return None
        faceVertices = vts[fcs.flatten()]
        v = faceVertices.reshape(fcs.shape[0], 3, 3)
        normals = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
        n = np.linalg.norm(normals, axis=1)
        normals[..., 0] /= n
        normals[..., 1] /= n
        normals[..., 2] /= n
        if apply:
            self.mesh.setAttributeData("face", "normal", normals)
        else:
            return normals

    def vertexNormalFromFace(self, apply=False):
        """
        Return an array (Nv,3) of normal vectors.
        """
        vts = self.mesh.getVertexes()
        faceNorms = self.mesh.getFaceNormals()
        if faceNorms is None:
            faceNorms = self.faceNormals()
        vertFaces = self.vertexFaces()

        if vts is None or faceNorms is None or vertFaces is None:
            return None

        result = _vertexNormalFromFace(vts, faceNorms, vertFaces)

        if apply:
            self.mesh.setAttributeData("vertex", "normal", result)
        else:
            return result

    # attribute promote

    def faceColorFromVertex(self, apply=False):
        """
        Return an array (Nf, 4) of face colors.
        """
        if apply:
            return self.faceAttribFromVertex("color", "color")
        else:
            return self.faceAttribFromVertex("color")

    def faceAttribFromVertex(self, name, targetName=None):
        """
        Return an array (Nf, dim).
        """
        vts = self.mesh.getAttributeData("vertex", name)
        fcs = self.mesh.getFaces()
        if vts is None or fcs is None:
            return None

        data = vts[fcs.flatten()]
        data = data.reshape(fcs.shape[0], 3, vts.shape[1])
        result = np.average(data, axis=1)
        if targetName:
            self.mesh.setAttributeData("face", targetName, result)
        else:
            return result

    def vertexAttribFromFace(self, name, targetName=None):
        """
        Return an array (Nv, dim).
        """
        vts = self.mesh.getAttributeData("face", name)
        fcs = self.mesh.getFaces()
        if vts is None or fcs is None:
            return None

        result = np.empty((self.mesh.getNumVertexes(), vts.shape[1]), dtype=vts.dtype)
        idxArray = np.arange(0, fcs.shape[0], 1, dtype=np.uint32)
        idxArray = np.repeat(idxArray, 3, axis=0)
        result[fcs.flatten()] = vts[idxArray]

        if targetName:
            self.mesh.setAttributeData("vertex", targetName, result)
        else:
            return result

    def vertexAttribFromEdge(self, name, targetName=None):
        """
        Return an array (Nv, dim).
        """
        vts = self.mesh.getAttributeData("edge", name)
        fcs = self.mesh.getEdges()
        if vts is None or fcs is None:
            return None

        result = np.empty((self.mesh.getNumVertexes(), vts.shape[1]), dtype=vts.dtype)
        idxArray = np.arange(0, fcs.shape[0], 1, dtype=np.uint32)
        idxArray = np.repeat(idxArray, 2, axis=0)
        result[fcs.flatten()] = vts[idxArray]

        if targetName:
            self.mesh.setAttributeData("vertex", targetName, result)
        else:
            return result

    def edgeAttribFromVertex(self, name, targetName=None):
        """
        Return an array (Ne, dim).
        """
        vts = self.mesh.getAttributeData("vertex", name)
        fcs = self.mesh.getEdges()
        if vts is None or fcs is None:
            return None

        data = vts[fcs.flatten()]
        data = data.reshape(fcs.shape[0], 2, vts.shape[1])
        result = np.average(data, axis=1)
        if targetName:
            self.mesh.setAttributeData("edge", targetName, result)
        else:
            return result

    # Framework functions

    def _joinVertex(self):
        # Given (Nv, 3, 3) array of vertexes-indexed-by-face, convert backward to unindexed vertexes

        vts = self.mesh.getVertexes()
        fcs = self.mesh.getFaces()
        if vts is None or fcs is None:
            return None

        faces = vts[fcs.flatten()]
        faces = faces.reshape(fcs.shape[0], 3, vts.shape[1])

        verts = {}  # used to remember the index of each vertex position
        new_faces = np.empty(faces.shape[:2], dtype=np.uint32)
        new_vertexes = []
        new_vertexFaces = []
        point_vertex = {}
        for i in range(faces.shape[0]):
            face = faces[i]  # [[x,y,z], [x,y,z], [x,y,z]]
            for j in range(face.shape[0]):
                pt = face[j]  # [x,y,z]
                pt2 = tuple(
                    [round(x * 1e14) for x in pt])  # quantize to be sure that nearly-identical points will be merged
                index = verts.get(pt2, None)
                if index is None:
                    new_vertexes.append(pt)
                    new_vertexFaces.append([])
                    index = len(new_vertexes) - 1
                    verts[pt2] = index
                new_vertexFaces[index].append(i)  # keep track of which vertexes belong to which faces
                new_faces[i, j] = index

                if index in point_vertex.keys():
                    point_vertex[index].append(fcs[i, j])
                else:
                    point_vertex[index] = [fcs[i, j]]

        new_vertexes = np.array(new_vertexes, dtype=np.float32)
        return new_vertexes, point_vertex, new_faces, new_vertexFaces

    def _sVertFromFace(self, name, vts, pointVertex, faces, vertexFaces, expand=False):
        attrib = self.mesh.getAttributeData("face", name)
        if attrib is None:
            return None

        result = np.zeros((vts.shape[0], attrib.shape[1]), dtype=attrib.dtype)
        for idx in range(vts.shape[0]):
            faces = vertexFaces[idx]
            if len(faces) == 0:
                continue
            at = attrib[faces]
            result[idx] = np.average(at, axis=0)

        if expand:
            expanded = np.empty((self.mesh.getNumVertexes(), result.shape[1]), dtype=attrib.dtype)
            for idx, vertexes in pointVertex.items():
                expanded[vertexes] = result[idx]
            return expanded
        else:
            return result

    def sVertexAttribFromFace(self, name, expand=False):
        vts, pointVertex, faces, vertexFaces = self._joinVertex()
        return self._sVertFromFace(name, vts, pointVertex, faces, vertexFaces, expand)

    def joinAllVertex(self):
        vts, pointVertex, faces, vertexFaces = self._joinVertex()

        attrib = {"vertex": {"pos": vts},
                  "face": {"face": faces}}

        for name, data in self.mesh.attribute["vertex"].items():
            if name == "pos":
                continue
            result = np.empty((vts.shape[0], data.shape[1]), dtype=data.dtype)
            for idx, vertexes in pointVertex.items():
                result[idx] = np.average(data[vertexes], axis=0)
            attrib["vertex"][name] = result
        self.mesh.attribute.update(attrib)
        self.mesh.vertexAttribute.update(attrib["vertex"])
        self.mesh.faceAttribute.update(attrib["face"])
        self.mesh.setAttributeData("edge", "edge", self.getEdges())

    def reverseNormals(self, level, apply=False):
        """
        Reverses the direction of all normal vectors.
        """
        normal = self.mesh.getAttributeData(level, "normal")
        if normal is None:
            return None

        if apply:
            normal *= -1
        else:
            return normal * -1

    @staticmethod
    def sphere(rows, cols, radius=1.0, offset=True):
        """
        Return a MeshData instance with vertexes and faces computed
        for a spherical surface.
        """
        verts = np.empty((rows + 1, cols, 3), dtype=np.float64)

        # compute vertexes
        phi = (np.arange(rows + 1) * np.pi / rows).reshape(rows + 1, 1)
        s = radius * np.sin(phi)
        verts[..., 2] = radius * np.cos(phi)
        th = ((np.arange(cols) * 2 * np.pi / cols).reshape(1, cols))
        if offset:
            th = th + ((np.pi / cols) * np.arange(rows + 1).reshape(rows + 1, 1))  ## rotate each row by 1/2 column
        verts[..., 0] = s * np.cos(th)
        verts[..., 1] = s * np.sin(th)
        verts = verts.reshape((rows + 1) * cols, 3)[
                cols - 1:-(cols - 1)]  ## remove redundant vertexes from top and bottom

        # compute faces
        faces = np.empty((rows * cols * 2, 3), dtype=np.uint32)
        rowtemplate1 = ((np.arange(cols).reshape(cols, 1) + np.array([[0, 1, 0]])) % cols) + np.array([[0, 0, cols]])
        rowtemplate2 = ((np.arange(cols).reshape(cols, 1) + np.array([[0, 1, 1]])) % cols) + np.array([[cols, 0, cols]])
        for row in range(rows):
            start = row * cols * 2
            faces[start:start + cols] = rowtemplate1 + row * cols
            faces[start + cols:start + (cols * 2)] = rowtemplate2 + row * cols
        faces = faces[cols:-cols]  ## cut off zero-area triangles at top and bottom

        # adjust for redundant vertexes that were removed from top and bottom
        vmin = cols - 1
        faces[faces < vmin] = vmin
        faces -= vmin
        vmax = verts.shape[0] - 1
        faces[faces > vmax] = vmax

        return verts, faces

    @staticmethod
    def cylinder(rows, cols, radius=[1.0, 1.0], length=1.0, offset=False):
        """
        Return a MeshData instance with vertexes and faces computed
        for a cylindrical surface.
        The cylinder may be tapered with different radii at each end (truncated cone)
        """
        verts = np.empty((rows + 1, cols, 3), dtype=np.float64)
        if isinstance(radius, int):
            radius = [radius, radius]  # convert to list
        # compute vertexes
        th = np.linspace(2 * np.pi, (2 * np.pi) / cols, cols).reshape(1, cols)
        r = np.linspace(radius[0], radius[1], num=rows + 1, endpoint=True).reshape(rows + 1,
                                                                                   1)  # radius as a function of z
        verts[..., 2] = np.linspace(0, length, num=rows + 1, endpoint=True).reshape(rows + 1, 1)  # z
        if offset:
            th = th + ((np.pi / cols) * np.arange(rows + 1).reshape(rows + 1, 1))  # rotate each row by 1/2 column
        verts[..., 0] = r * np.cos(th)  # x = r cos(th)
        verts[..., 1] = r * np.sin(th)  # y = r sin(th)
        verts = verts.reshape((rows + 1) * cols, 3)  # just reshape: no redundant vertices...
        # compute faces
        faces = np.empty((rows * cols * 2, 3), dtype=np.uint32)
        rowtemplate1 = ((np.arange(cols).reshape(cols, 1) + np.array([[0, 1, 0]])) % cols) + np.array([[0, 0, cols]])
        rowtemplate2 = ((np.arange(cols).reshape(cols, 1) + np.array([[0, 1, 1]])) % cols) + np.array([[cols, 0, cols]])
        for row in range(rows):
            start = row * cols * 2
            faces[start:start + cols] = rowtemplate1 + row * cols
            faces[start + cols:start + (cols * 2)] = rowtemplate2 + row * cols

        return verts, faces


standShader = ShaderProgram('shaded', [
    VertexShader("""
        varying vec3 normal;
        varying vec2 texCoord;
        void main() {
            // compute here for use in fragment shader
            normal = normalize(gl_NormalMatrix * gl_Normal);
            gl_FrontColor = gl_Color;
            gl_BackColor = gl_Color;
            gl_Position = ftransform();
            texCoord = gl_MultiTexCoord0.xy;
        }
    """),
    FragmentShader("""
        varying vec3 normal;
        varying vec2 texCoord;
        void main() {
            float p = dot(normal, normalize(vec3(1.0, -1.0, -1.0)));
            p = p < 0. ? 0. : p * 0.8;
            vec4 color = gl_Color;
            //color.x = color.x * (0.2 + p);
            //color.y = color.y * (0.2 + p);
            //color.z = color.z * (0.2 + p);
            gl_FragColor = color;
        }
    """)])

IDColorShader = ShaderProgram('IDColor', [
    VertexShader("""
        void main() {
            gl_FrontColor = gl_Color;
            gl_BackColor = gl_Color;
            gl_Position = ftransform();
        }
    """),
    FragmentShader("""
        void main() {
            gl_FragColor = gl_Color;
        }
    """)])


class _signals(QtCore.QObject):
    attribChanged = QtCore.Signal()

    def __init__(self):
        super().__init__()

    def emit_attribChanged(self):
        self.attribChanged.emit


class bbox(GLGraphicsItem):
    def __init__(self):
        super(bbox, self).__init__()
        self.size = [1, 1, 1]
        self.setColor((255, 255, 0, 200))
        self.setGLOptions('translucent')

    def set(self, pos, size):
        pos[0] -= size[0] * 0.5
        pos[1] -= size[1] * 0.5
        pos[2] -= size[2] * 0.5

        self.size = size
        tr = QtGui.QMatrix4x4()
        tr.translate(pos[0], pos[1], pos[2])
        return tr

    def setColor(self, *args):
        self.__color = fn.Color(*args)

    def color(self):
        return self.__color

    def paint(self):
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # glEnable( GL_BLEND )
        # glEnable( GL_ALPHA_TEST )
        ##glAlphaFunc( GL_ALWAYS,0.5 )
        # glEnable( GL_POINT_SMOOTH )
        # glDisable( GL_DEPTH_TEST )
        self.setupGLState()

        glBegin(GL_LINES)

        glColor4f(*self.color().glColor())
        x, y, z = self.size
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, z)
        glVertex3f(x, 0, 0)
        glVertex3f(x, 0, z)
        glVertex3f(0, y, 0)
        glVertex3f(0, y, z)
        glVertex3f(x, y, 0)
        glVertex3f(x, y, z)

        glVertex3f(0, 0, 0)
        glVertex3f(0, y, 0)
        glVertex3f(x, 0, 0)
        glVertex3f(x, y, 0)
        glVertex3f(0, 0, z)
        glVertex3f(0, y, z)
        glVertex3f(x, 0, z)
        glVertex3f(x, y, z)

        glVertex3f(0, 0, 0)
        glVertex3f(x, 0, 0)
        glVertex3f(0, y, 0)
        glVertex3f(x, y, 0)
        glVertex3f(0, 0, z)
        glVertex3f(x, 0, z)
        glVertex3f(0, y, z)
        glVertex3f(x, y, z)

        glEnd()


class Mesh(GLGraphicsItem):
    def __init__(self, **kwds):
        self.opts = {
            'meshdata': None,
            'color': (1., 1., 1., 1.),
            'drawEdges': False,
            'drawFaces': True,
            'edgeColor': (0.5, 0.5, 0.5, 1.0),
            'shader': standShader,
            'smooth': True,
            'computeNormals': False,
        }

        super(Mesh, self).__init__()
        self.setGLOptions('opaque')

        self._attribute = {}
        self._vertexAttribute = {}
        self._faceAttribute = {}
        self._edgeAttribute = {}
        self._detailAttribute = None

        self.signals = _signals()
        self.bbox = bbox()
        self.meshData = MeshData(self)

        self._bbox_min = []
        self._bbox_max = []
        self._bbox_center = []
        self._selected = False

        self.edge_colors = {
            True: (1.0, 1.0, 0.0, 1.0),
            False: (0.15, 0.15, 0.15, 1.0)
        }

        self.idx = 0
        # self.attribute
        # self.edges = None
        # self.edgeVerts = None

    @property
    def bbox_min(self):
        vts = self.getVertexes()
        if vts is None or vts.shape[0] == 0:
            return [0, 0, 0]
        self._bbox_min = list(np.min(vts, axis=0))
        return self._bbox_min

    @property
    def bbox_max(self):
        vts = self.getVertexes()
        if vts is None or vts.shape[0] == 0:
            return [0, 0, 0]
        self._bbox_max = list(np.max(vts, axis=0))
        return self._bbox_max

    @property
    def bbox_center(self):
        _min = self.bbox_min
        _max = self.bbox_max
        self._bbox_center = [(_min[0] + _max[0]) / 2.0,
                             (_min[1] + _max[1]) / 2.0,
                             (_min[2] + _max[2]) / 2.0]
        return self._bbox_center

    @property
    def vertexAttribute(self):
        return self._vertexAttribute

    @property
    def faceAttribute(self):
        return self._faceAttribute

    @property
    def edgeAttribute(self):
        return self._edgeAttribute

    @property
    def detailAttribute(self):
        __detailAttribute = {
            "bbox_min": self.bbox_min,
            "bbox_max": self.bbox_max,
            "bbox_center": self.bbox_center
        }
        if self._detailAttribute is None:
            self._detailAttribute = __detailAttribute
        else:
            self._detailAttribute.update(__detailAttribute)

        self.cleanup_attribute(self._detailAttribute)
        return self._detailAttribute

    @property
    def attribute(self):
        if self._attribute:
            return self._attribute

        self._attribute = {
            "vertex": self.vertexAttribute,
            "edge": self.edgeAttribute,
            "face": self.faceAttribute,
            "detail": self.detailAttribute
        }
        self.signals.emit_attribChanged()
        return self._attribute

    def cleanup_attribute(self, attribObject=None):
        if attribObject:
            to_remove = [key for key, at in attribObject.items() if at is None]
            [attribObject.pop(key) for key in to_remove]
        else:
            for attrib in self._attribute.values():
                to_remove = [key for key, at in attrib.items() if at is None]
                [attrib.pop(key) for key in to_remove]

    def moveToCenter(self):
        cent = self.bbox_center
        self.translate(-1.0 * cent[0],
                       -1.0 * cent[1],
                       -1.0 * cent[2])

    def setSelected(self, sel):
        self._selected = sel
        self.opts["drawEdges"] = sel
        # self.opts['edgeColor'] = self.edge_colors[False]
        self.update()

    def getSelected(self):
        return self._selected

    def drawBBox(self):
        _min = self.bbox_min
        _max = self.bbox_max
        center = [(_min[0] + _max[0]) / 2.0,
                  (_min[1] + _max[1]) / 2.0,
                  (_min[2] + _max[2]) / 2.0]

        size = [abs(_min[0] - _max[0]),
                abs(_min[1] - _max[1]),
                abs(_min[2] - _max[2])]

        tr = self.bbox.set(center, size)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        try:
            a = np.array(tr.copyDataTo()).reshape((4, 4))
            glMultMatrixf(a.transpose())
            self.bbox.paint()
        finally:
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()

    def parseMeshData(self):
        if self.opts['drawEdges']:
            if self.getAttributeData("edge","edge") is None:
                self.setAttributeData("edge","edge",self.meshData.getEdges())

        return

    def meshDataChanged(self):
        # self.parseMeshData()
        self.signals.emit_attribChanged()
        self.update()

    def setShader(self, shader):
        self.opts['shader'] = shader
        self.update()

    def shader(self):
        return self.opts['shader']

    def setColor(self, c):
        self.opts['color'] = c
        self.update()

    def setID(self, idx):
        self.idx = idx

    def drawID(self):
        with IDColorShader:
            faces = self.getAttributeData("face", "face")
            verts = self.getAttributeData("vertex", "pos")
            if verts is None:
                return
            glEnableClientState(GL_VERTEX_ARRAY)
            try:
                glVertexPointerf(verts)
                glColor4f(*(self.idx, 0, 0, 1))
                if faces is None:
                    glDrawArrays(GL_TRIANGLES, 0, np.product(verts.shape[:-1]))
                else:
                    faces = faces.astype(np.uint).flatten()
                    glDrawElements(GL_TRIANGLES, faces.shape[0], GL_UNSIGNED_INT, faces)
            finally:
                glDisableClientState(GL_VERTEX_ARRAY)

    def paint(self):
        self.setupGLState()
        self.parseMeshData()

        verts = self.getAttributeData("vertex", "pos")

        if self.opts['drawFaces']:
            with self.shader():
                norms = self.getAttributeData("vertex", "normal")
                color = self.getAttributeData("vertex", "color")
                faces = self.getAttributeData("face", "face")
                uvs = self.getAttributeData("vertex", "uv")

                # print("verts",verts.shape[0])
                # print("norms", norms.shape[0])
                # print("color", color.shape[0])
                # print("faces", faces.shape[0])
                # print("uvs", uvs.shape[0])

                if verts is None:
                    return
                glEnableClientState(GL_VERTEX_ARRAY)
                try:
                    glVertexPointerf(verts)

                    if color is None:
                        color = self.opts['color']
                        if isinstance(color, QtGui.QColor):
                            glColor4f(*fn.glColor(color))
                        else:
                            glColor4f(*color)
                    else:
                        glEnableClientState(GL_COLOR_ARRAY)
                        glColorPointerf(color)

                    if norms is not None:
                        glEnableClientState(GL_NORMAL_ARRAY)
                        glNormalPointerf(norms)

                    if uvs is not None:
                        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
                        glTexCoordPointerf(uvs)

                    if faces is None:
                        glDrawArrays(GL_TRIANGLES, 0, np.product(verts.shape[:-1]))
                    else:
                        faces = faces.astype(np.uint).flatten()
                        glDrawElements(GL_TRIANGLES, faces.shape[0], GL_UNSIGNED_INT, faces)
                finally:
                    glDisableClientState(GL_NORMAL_ARRAY)
                    glDisableClientState(GL_VERTEX_ARRAY)
                    glDisableClientState(GL_COLOR_ARRAY)
                    glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        if self._selected:
            self.drawBBox()

        if self.opts['drawEdges']:
            edges = self.getAttributeData("edge", "edge")
            color = self.getAttributeData("edge", "color")
            if verts is None or edges is None:
                return
            glEnableClientState(GL_VERTEX_ARRAY)
            try:
                glVertexPointerf(verts)

                if color is None:
                    color = self.opts['edgeColor']
                    if isinstance(color, QtGui.QColor):
                        glColor4f(*fn.glColor(color))
                    else:
                        glColor4f(*color)
                else:
                    glEnableClientState(GL_COLOR_ARRAY)
                    glColorPointerf(color)
                edges = edges.flatten()
                glDrawElements(GL_LINES, edges.shape[0], GL_UNSIGNED_INT, edges)
            finally:
                glDisableClientState(GL_VERTEX_ARRAY)
                glDisableClientState(GL_COLOR_ARRAY)

    def getVertexes(self):
        if "pos" in self.vertexAttribute.keys():
            return self.vertexAttribute["pos"]
        else:
            return None

    def getFaces(self):
        if "face" in self.faceAttribute.keys():
            return self.faceAttribute["face"]
        else:
            return None

    def getColors(self):
        if "color" in self.vertexAttribute.keys():
            return self.vertexAttribute["color"]
        else:
            return None

    def getFaceColors(self):
        if "color" in self.faceAttribute.keys():
            return self.faceAttribute["color"]
        else:
            return None

    def getNormals(self):
        if "normal" in self.vertexAttribute.keys():
            return self.vertexAttribute["normal"]
        else:
            return None

    def getFaceNormals(self):
        if "normal" in self.faceAttribute.keys():
            return self.faceAttribute["normal"]
        else:
            return None

    def getVertexFaces(self):
        if self.opts['meshdata'] is None:
            return None
        return self.opts['meshdata'].vertexFaces()

    def getEdges(self):
        if "edge" in self.edgeAttribute.keys():
            return self.edgeAttribute["edge"]
        else:
            return None
        #
        # if self.edges is None:
        #     if self.opts['meshdata'] is None:
        #         return None
        #     self.edges = self.opts['meshdata'].edges()
        #
        # return self.edges

    def getMeshData(self):
        return self.opts['meshdata']

    def getNumVertexes(self):
        vt = self.getVertexes()
        if vt is None:
            return 0
        return vt.shape[0]

    def getNumFaces(self):
        fc = self.getFaces()
        if fc is None:
            return 0
        return fc.shape[0]

    def getNumEdges(self):
        eg = self.getEdges()
        if eg is None:
            return 0
        return eg.shape[0]

    def getEdgesColors(self):
        if "color" in self.edgeAttribute.keys():
            return self.edgeAttribute["color"]
        else:
            return None
        #
        # if self.opts['meshdata'] is None:
        #     return None
        # return self.opts['meshdata'].edgeColors()

    def getAttribute(self, level, name, index):
        attrib = self.attribute
        if level in attrib.keys():
            target_level = attrib[level]
            if name in target_level.keys():
                try:
                    value = target_level[name][index]
                    return value
                except:
                    return None
        return None

    def setAttribute(self, level, name, index, value):
        attrib = self.attribute
        if level in attrib.keys():
            target_level = attrib[level]
            if name in target_level.keys():
                try:
                    target_level[name][index] = value
                    self.signals.emit_attribChanged()
                    return True
                except:
                    return False

        return False

    def createAttribute(self, level, name, attrib_type=float, size=1):
        attrib = self.attribute
        if level in attrib.keys():
            target_level = attrib[level]
            if name in target_level.keys():
                return False
            else:
                tp = np.float32 if attrib_type is float else np.int32
                if level == "vertex":
                    new = np.zeros((self.getNumVertexes(), size), dtype=tp)
                elif level == "face":
                    new = np.zeros((self.getNumFaces(), size), dtype=tp)
                elif level == "edge":
                    new = np.zeros((self.getNumEdges(), size), dtype=tp)
                target_level[name] = new
                self.signals.emit_attribChanged()
                return True
        return False

    def deleteAttribute(self, level, name):
        attrib = self.attribute
        if level in attrib.keys():
            target_level = attrib[level]
            if name in target_level.keys():
                target_level.pop(name)
                self.signals.emit_attribChanged()

    def getAttributeData(self, level, name):
        attrib = self.attribute
        if level in attrib.keys():
            target_level = attrib[level]
            if name in target_level.keys():
                return target_level[name]
        return None

    def setAttributeData(self, level, name, value):
        self.attribute[level][name] = value
        self.signals.emit_attribChanged()

    def hasAttribute(self, level, name, value):
        attrib = self.attribute
        if level in attrib.keys():
            target_level = attrib[level]
            if name in target_level.keys():
                return True
        return False

    def addVertex(self, pos):
        v = np.zeros((1, 3), dtype=np.float32)
        v[0] = pos
        if self.getAttributeData("vertex", "pos") is None:
            self.vertexAttribute["pos"] = v
        else:
            self.vertexAttribute["pos"] = np.append(self.vertexAttribute["pos"], v, 0)

    def clear(self):
        self.opts['meshdata'] = None
        self._vertexAttribute = {}
        self._faceAttribute = {}
        self._edgeAttribute = {}
        self._detailAttribute = {}
        self.attribute
        self.signals.emit_attribChanged()
        self.update()

    def setMeshData(self, **kwds):
        md = kwds.get('meshdata', None)
        changed = False
        if md is None:
            opts = {}
            for k in ['vertexes', 'faces', 'edges', 'vertexColors', 'faceColors']:
                try:
                    opts[k] = kwds.pop(k)
                    changed = True
                except KeyError:
                    pass
            if changed:
                md = gl.MeshData(**opts)
                self.opts['meshdata'] = md
        self.opts.update(kwds)
        if changed:
            self.meshDataChanged()

    @staticmethod
    def load_from_obj(file):
        obj = OBJLoader.Load(file)

        m = Mesh()
        m.vertexAttribute["pos"] = obj.vertices
        m.faceAttribute["face"] = obj.faces
        if obj.normals is not None:
            m.vertexAttribute["normal"] = obj.normals
        if obj.uvs is not None:
            m.vertexAttribute["uv"] = obj.uvs

        # print(obj.vertices.shape[0])
        # print(obj.faces.shape[0])
        # print(obj.normals.shape[0])
        # print(obj.uvs.shape[0])
        return m

    @staticmethod
    def from_attribute(attrib):
        m = Mesh()
        m.attribute.update(attrib)
        m.vertexAttribute.update(attrib["vertex"])
        m.faceAttribute.update(attrib["face"])
        m.edgeAttribute.update(attrib["edge"])
        m.detailAttribute.update(attrib["detail"])

        return m
