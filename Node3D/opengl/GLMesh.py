import numpy as np
from OpenGL.arrays import vbo
from ..vendor.pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from .Mesh_utils import MeshFuncs, mesh_signals, bbox
import openmesh
import copy
from .Shader import *

orig_set_vertex_property_array = openmesh.PolyMesh.set_vertex_property_array


def svpa(self, prop_name, array=None, element_shape=None, element_value=None):
    if array is not None:
        try:
            orig_set_vertex_property_array(self, prop_name, array)
        except Exception as e:
            print('error when set attribute', prop_name, type(array), array.shape, self.n_vertices())
            raise e
        return
    if element_shape is None:
        if element_value is None:
            element_shape = ()
        else:
            element_shape = np.shape(element_value)

    if element_value is None:
        orig_set_vertex_property_array(self, prop_name, np.empty(element_shape))
    else:
        orig_set_vertex_property_array(self, prop_name, np.array(
            np.broadcast_to(element_value, element_shape)))


openmesh.PolyMesh.set_vertex_property_array = svpa

orig_set_face_property_array = openmesh.PolyMesh.set_face_property_array


def sfpa(self, prop_name, array=None, element_shape=None, element_value=None):
    if array is not None:
        try:
            orig_set_face_property_array(self, prop_name, array)
        except Exception as e:
            print('error when set attribute', prop_name, type(array), array.shape, self.n_faces())
            raise e
        return
    if element_shape is None:
        if element_value is None:
            element_shape = ()
        else:
            element_shape = np.shape(element_value)

    if element_value is None:
        orig_set_face_property_array(self, prop_name, np.empty(element_shape))
    else:
        orig_set_face_property_array(self, prop_name, np.array(
            np.broadcast_to(element_value, element_shape)))


openmesh.PolyMesh.set_face_property_array = sfpa

orig_set_edge_property_array = openmesh.PolyMesh.set_edge_property_array


def sepa(self, prop_name, array=None, element_shape=None, element_value=None):
    if array is not None:
        try:
            orig_set_edge_property_array(self, prop_name, array)
        except Exception as e:
            print('error when set attribute', prop_name, type(array), array.shape, self.n_faces())
            raise e
        return
    if element_shape is None:
        if element_value is None:
            element_shape = ()
        else:
            element_shape = np.shape(element_value)

    if element_value is None:
        orig_set_edge_property_array(self, prop_name, np.empty(element_shape))
    else:
        orig_set_edge_property_array(self, prop_name, np.array(
            np.broadcast_to(element_value, element_shape)))


openmesh.PolyMesh.set_edge_property_array = sepa

DATA_TYPE_MAP = {
    float: "float",
    int: "int",
    bool: "bool",
    str: "str",
    np.ndarray: "vector",
    list: "list",
}


class Mesh(GLGraphicsItem):
    def __init__(self, mesh=None):
        self.opts = {
            'color': (1., 1., 1.),
            'edgeColor': (0.5, 0.5, 0.5),
            'pointColor': (1.0, 1.0, 0.0),
            'shader': standShader,
            'smooth': True,
            'computeNormals': False,
        }

        super(Mesh, self).__init__()

        self._detailAttribute = {
            "vertex": {
                "pos": None,
                "normal": None,
            },
            "face": {
                "normal": None
            },
            "edge": {},
        }

        self.signals = mesh_signals()
        self.bbox = bbox()
        self._bbox_min = []
        self._bbox_max = []
        self._bbox_center = []
        self._selected = False

        self.edge_colors = {
            True: (1.0, 1.0, 0.0, 1.0),
            False: (0.15, 0.15, 0.15, 1.0)
        }

        self.idx = 0

        if mesh is None:
            self._mesh = openmesh.PolyMesh()
            self._mesh.is_triangles()
        else:
            self._mesh = mesh
        self._mesh.release_vertex_texcoords1D()
        self._mesh.release_vertex_texcoords2D()
        self._mesh.release_vertex_texcoords3D()
        self._mesh.release_vertex_colors()
        self._mesh.release_halfedge_texcoords1D()
        self._mesh.release_halfedge_texcoords2D()
        self._mesh.release_halfedge_texcoords3D()
        self._mesh.release_halfedge_normals()
        self._mesh.release_halfedge_colors()
        self._mesh.release_face_colors()
        self._mesh.release_face_texture_index()
        self._mesh.release_edge_colors()

        # self._mesh = openmesh.PolyMesh()

        self.meshFuncs = MeshFuncs(self)
        self._build_dict()
        self._GLFaces = None
        self._flatColor = 0

    @property
    def mesh(self):
        return self._mesh

    @property
    def bbox_min(self):
        vts = self.getVertexes()
        if vts is None:
            return [0, 0, 0]
        self._bbox_min = list(np.min(vts, axis=0))
        return self._bbox_min

    @property
    def bbox_max(self):
        vts = self.getVertexes()
        if vts is None:
            return [0, 0, 0]
        self._bbox_max = list(np.max(vts, axis=0))
        return self._bbox_max

    @property
    def bbox_center(self):
        _, __, self._bbox_center = self.get_bbox_info()
        return self._bbox_center

    def get_bbox_info(self):
        _min = self.bbox_min
        _max = self.bbox_max
        _center = [(_min[0] + _max[0]) / 2.0,
                   (_min[1] + _max[1]) / 2.0,
                   (_min[2] + _max[2]) / 2.0]
        return _min, _max, _center

    @property
    def detailAttribute(self):
        return self._detailAttribute

    def getAttribNames(self, allInOne=False):
        # v = [i for i in self._detailAttribute["vertex"].keys() if ":" not in i]
        # f = [i for i in self._detailAttribute["face"].keys() if ":" not in i]
        # e = [i for i in self._detailAttribute["edge"].keys() if ":" not in i]
        v = [i for i in self._detailAttribute["vertex"].keys()]
        f = [i for i in self._detailAttribute["face"].keys()]
        e = [i for i in self._detailAttribute["edge"].keys()]
        d = [i for i in self._detailAttribute.keys() if i not in ["vertex", "face", "edge"]]
        if allInOne:
            result = []
            result.extend(v)
            result.extend(f)
            result.extend(e)
        else:
            result = {'vertex': v,
                      'face': f,
                      'edge': e,
                      'detail': d}
        return result

    def getAttribType(self, attrLevel, attribName):
        # get the type of a given attribute
        checkType = None
        if attrLevel == "vertex":
            checkType = type(self.getVertexAttrib(attribName, 0))
        elif attrLevel == "edge":
            checkType = type(self.getEdgeAttrib(attribName, 0))
        elif attrLevel == "face":
            checkType = type(self.getFaceAttrib(attribName, 0))
        elif attrLevel == "detail":
            checkType = type(self.getDetailAttrib(attribName))

        return DATA_TYPE_MAP.get(checkType, 'none')

    def _build_dict(self):
        self._mapGetData = {
            # "color": [self._mesh.vertex_colors, self._mesh.face_colors, self._mesh.edge_colors],
            "pos": [self._mesh.points, None, None],
            "normal": [self.getNormals, self.getFaceNormals, None],
        }
        self._mapGetValue = {
            # "color": [self._mesh.color, self._mesh.color, self._mesh.color],
            "pos": [self._mesh.point, None, None],
            "normal": [self._mesh.normal, self._mesh.normal, None],
        }
        self._mapSetValue = {
            # "color": [self._mesh.set_color, self._mesh.set_color, self._mesh.set_color],
            "pos": [self._mesh.set_point, None, None],
            "normal": [self._mesh.set_normal, self._mesh.set_normal, None],
        }

    def update_GLFace(self):
        b = self.getTriangulateMesh()
        self._GLFaces = b.face_vertex_indices()

    def getTriangulateMesh(self):
        b = copy.deepcopy(self._mesh)
        b.triangulate()
        return b

    def setFlatColor(self, mode):
        if mode is True:
            self._flatColor = 1
        else:
            self._flatColor = 0

    def moveToCenter(self):
        cent = self.bbox_center
        self.translate(-1.0 * cent[0],
                       -1.0 * cent[1],
                       -1.0 * cent[2])

    def setSelected(self, sel):
        self._selected = sel
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
        if self._GLFaces is None:
            self.update_GLFace()
        try:
            with IDColorShader:
                faces = self._GLFaces
                verts = self.getVertexes()
                if verts is None:
                    return
                glEnableClientState(GL_VERTEX_ARRAY)
                try:
                    glVertexPointerf(verts)
                    glColor3f(*(self.idx, 0, 0))
                    if faces is None:
                        glDrawArrays(GL_TRIANGLES, 0, np.product(verts.shape[:-1]))
                    else:
                        faces = faces.astype(np.uint).flatten()
                        glDrawElements(GL_TRIANGLES, faces.shape[0], GL_UNSIGNED_INT, faces)
                finally:
                    glDisableClientState(GL_VERTEX_ARRAY)
        except:
            pass

    def paint(self):
        # self.setupGLState()
        if self._GLFaces is None:
            self.update_GLFace()

        verts = self.getVertexes()
        if verts is None:
            return
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointerf(verts)

        color = self.getColors()
        hasColor = color is not None
        if not hasColor:
            glColor3f(*self.opts['color'])
        else:
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointerf(color)

        if self.view().opts['drawFaces'] and self.getNumFaces() > 0:
            with self.shader():
                self.shader().setUniform1i("flatColor", self._flatColor)
                norms = self.getNormals()
                faces = self._GLFaces
                uvs = self.getUVs()
                try:
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
                    glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        if self.view().opts['drawPoints']:
            pscale = self.getVertexAttribData("pscale", True)
            if not hasColor:
                glColor3f(*self.opts['pointColor'])
            with PointShader:
                camPos = self.view().cameraPosition()
                if camPos is not None:
                    PointShader.setUniform3f("camPos", camPos)
                    PointShader.setUniform1i("pixmode", 0)
                else:
                    PointShader.setUniform1i("pixmode", 1)
                if pscale is None:
                    PointShader.setUniform1f("unifrom_scale", 0.5)
                    glDrawArrays(GL_POINTS, 0, self.getNumVertexes())
                else:
                    PointShader.setUniform1f("unifrom_scale", -1)
                    pscaleAttrib = PointShader.getAttribLocation("pscale")
                    vertexScales = vbo.VBO(pscale.flatten())
                    vertexScales.bind()
                    glEnableVertexAttribArray(pscaleAttrib)
                    glVertexAttribPointer(pscaleAttrib, 1, GL_FLOAT, False, 0, None)
                    glDrawArrays(GL_POINTS, 0, self.getNumVertexes())
                    vertexScales.unbind()

        glDisableClientState(GL_COLOR_ARRAY)

        if self.view().opts['drawEdges'] and self.getNumEdges() > 0:
            edges = self.getEdges()
            # color = self.getEdgesColors()
            try:
                # if color is None:
                glColor3f(*self.opts['edgeColor'])
                # else:
                # glEnableClientState(GL_COLOR_ARRAY)
                # glColorPointerf(color)
                edges = edges.flatten()
                glDrawElements(GL_LINES, edges.shape[0], GL_UNSIGNED_INT, edges)
            finally:
                pass
                # glDisableClientState(GL_COLOR_ARRAY)

        glDisableClientState(GL_VERTEX_ARRAY)

        if self._selected:
            self.drawBBox()

    def getVertexes(self):
        p = self._mesh.points()
        if p.shape[0] == 0:
            return None
        return p

    def getFaces(self):
        f = self._mesh.face_vertex_indices()
        if f.shape[0] == 0:
            return None
        return f

    def getColors(self):
        return self.getVertexAttribData("color", True)

    def getUVs(self):
        return self.getVertexAttribData('uv', True)

    def getNormals(self):
        if not self._mesh.has_vertex_normals():
            if self.getNumFaces() == 0:
                return None
            self._mesh.update_vertex_normals()
        return self._mesh.vertex_normals()

    def getFaceNormals(self):
        if not self._mesh.has_face_normals():
            if self.getNumFaces() == 0:
                return None
            self._mesh.update_face_normals()
        return self._mesh.face_normals()

    def getVertexFaces(self):
        return self._mesh.vertex_face_indices()

    def getEdges(self):
        e = self._mesh.edge_vertex_indices()
        if e.shape[0] == 0:
            return None
        return e

    def getNumVertexes(self):
        return self._mesh.n_vertices()

    def getNumFaces(self):
        return self._mesh.n_faces()

    def getNumEdges(self):
        return self._mesh.n_edges()

    def removeAttribute(self, level, name):
        if level == "vertex":
            if name == 'pos':
                return
            if self._mesh.has_vertex_property(name):
                self._mesh.remove_vertex_property(name)
                self._detailAttribute["vertex"].pop(name)
        elif level == "face":
            if self._mesh.has_face_property(name):
                self._mesh.remove_face_property(name)
                self._detailAttribute["face"].pop(name)
        elif level == "edge":
            if self._mesh.has_edge_property(name):
                self._mesh.remove_edge_property(name)
                self._detailAttribute["edge"].pop(name)
        elif level == "detail":
            if name in self._detailAttribute.keys():
                self._detailAttribute.pop(name)

    def renameAttribute(self, level, name, new_name):
        if level == "vertex":
            if name == 'pos':
                return
            if self._mesh.has_vertex_property(name):
                a = self.getVertexAttribData(name)
                self.setVertexAttribData(new_name, a)
                self.removeAttribute(level, name)
        elif level == "face":
            if self._mesh.has_face_property(name):
                a = self.getFaceAttribData(name)
                self.setFaceAttribData(new_name, a)
                self.removeAttribute(level, name)
        elif level == "edge":
            if self._mesh.has_edge_property(name):
                a = self.getEdgeAttribData(name)
                self.setEdgeAttribData(new_name, a)
                self.removeAttribute(level, name)
        elif level == "detail":
            if name in self._detailAttribute.keys():
                self._detailAttribute[new_name] = self._detailAttribute.pop(name)

    def hasAttribute(self, level, name):
        if level == "vertex":
            if self._mesh.has_vertex_property(name):
                return True
        elif level == "face":
            if self._mesh.has_face_property(name):
                return True
        elif level == "edge":
            if self._mesh.has_edge_property(name):
                return True
        if level in self.detailAttribute.keys():
            if name in self.detailAttribute[level].keys():
                return True
        return False

    def addVertex(self, pos):
        if type(pos) is list:
            return self._mesh.add_vertex(np.array(pos))
        elif type(pos) is np.ndarray:
            return self._mesh.add_vertex(pos)
        elif type(pos) is tuple:
            return self._mesh.add_vertex(np.array([pos[0], pos[1], pos[2]]))

    def addFace(self, vts):
        self._GLFaces = None
        if type(vts[0]) is openmesh.VertexHandle:
            return self._mesh.add_face(vts)
        else:
            return self._mesh.add_face([self._mesh.vertex_handle(i) for i in vts])

    def addVertices(self, vts):
        self._GLFaces = None
        return self._mesh.add_vertices(vts)

    def addFaces(self, fcs):
        self._GLFaces = None
        return self._mesh.add_faces(fcs)

    def removeVertex(self, vt, isolate=False, clean=True):
        if type(vt) is not openmesh.VertexHandle:
            vt = self._mesh.vertex_handle(vt)
        if vt.idx() < self.getNumVertexes():
            self._mesh.delete_vertex(vt, isolate)
            if clean:
                self._mesh.garbage_collection()
            self._GLFaces = None

    def removeFace(self, fc, isolate=False, clean=True):
        if type(fc) is not openmesh.FaceHandle:
            fc = self._mesh.face_handle(fc)
        if fc.idx() < self.getNumFaces():
            self._mesh.delete_face(fc, isolate)
            if clean:
                self._mesh.garbage_collection()
            self._GLFaces = None

    def removeEdge(self, eg, isolate=False, clean=True):
        if type(eg) is not openmesh.EdgeHandle:
            eg = self._mesh.edge_handle(eg)
        if eg.idx() < self.getNumEdges():
            self._mesh.delete_edge(eg, isolate)
            if clean:
                self._mesh.garbage_collection()
            self._GLFaces = None

    def removeVertices(self, vts, isolate=False):
        for vt in vts:
            self.removeVertex(vt, isolate, False)
        self._mesh.garbage_collection()

    def removeFaces(self, fcs, isolate=False):
        for fc in fcs:
            self.removeFace(fc, isolate, False)
        self._mesh.garbage_collection()

    def removeEdges(self, egs, isolate=False):
        for eg in egs:
            self.removeEdge(eg, isolate, False)
        self._mesh.garbage_collection()

    def clear(self):
        self._mesh.clear()
        self._detailAttribute = {}
        self.signals.emit_attribChanged()
        self.update()

    def _processBuildinAttrib(self, _dict, idx, name, args=(), emit=False, data=None):
        if emit and name == "pos":
            self._GLFaces = None
        if name in _dict.keys():
            func = _dict[name][idx]
            if func is not None:
                if data is not None:
                    ori = func()
                    if ori.shape == data.shape:
                        ori[..., [0, 1, 2]] = data
                        self.signals.emit_attribChanged()
                        return [None, True]
                    else:
                        return [None, False]
                elif emit:
                    func(*args)
                    self.signals.emit_attribChanged()
                    return [None, True]
                else:
                    if len(args) == 1:
                        return [func(args[0]), True]
                    else:
                        return [func(), True]

        return [None, False]

    def getVertexAttribData(self, name, array=True):
        if self._mesh.has_vertex_property(name):
            if array:
                try:
                    return self._mesh.vertex_property_array(name)
                except Exception as e:
                    pass
            return self._mesh.vertex_property(name)
        return self._processBuildinAttrib(self._mapGetData, 0, name)[0]

    def getFaceAttribData(self, name, array=True):
        if self._mesh.has_face_property(name):
            if array:
                try:
                    return self._mesh.face_property_array(name)
                except:
                    pass
            return self._mesh.face_property(name)
        return self._processBuildinAttrib(self._mapGetData, 1, name)[0]

    def getEdgeAttribData(self, name, array=False):
        if self._mesh.has_edge_property(name):
            if array:
                try:
                    return self._mesh.edge_property_array(name)
                except:
                    pass
            return self._mesh.edge_property(name)
        return self._processBuildinAttrib(self._mapGetData, 2, name)[0]

    def setVertexAttribData(self, name, data, array=True):
        if self._processBuildinAttrib(self._mapGetData, 0, name, emit=True, data=data)[1]:
            return True
        hasAttrib = self._mesh.has_vertex_property(name)
        if array and type(data) is np.ndarray:
            if not hasAttrib:
                self._mesh.vertex_property_array(name)
                self._detailAttribute["vertex"][name] = None
            try:
                if len(data.shape) == 2 and data.shape[1] == 1:
                    data = data.reshape((data.shape[0],))
                self._mesh.set_vertex_property_array(name, data)
                self.signals.emit_attribChanged()
                return True
            except:
                self._mesh.remove_vertex_property(name)
                self._detailAttribute["vertex"].pop(name)

        try:
            if not hasAttrib:
                self._mesh.vertex_property(name)
                self._detailAttribute["vertex"][name] = None
            if type(data) is np.ndarray:
                data = data.tolist()
            self._mesh.set_vertex_property(name, data)
            self.signals.emit_attribChanged()
            return True
        except:
            self._mesh.remove_vertex_property(name)
            self._detailAttribute["vertex"].pop(name)
            return False

    def setFaceAttribData(self, name, data, array=True):
        if self._processBuildinAttrib(self._mapGetData, 1, name, emit=True, data=data)[1]:
            return True
        hasAttrib = self._mesh.has_face_property(name)
        if array and type(data) is np.ndarray:
            if not hasAttrib:
                self._mesh.face_property_array(name)
                self._detailAttribute["face"][name] = None
            try:
                if len(data.shape) == 2 and data.shape[1] == 1:
                    data = data.reshape((data.shape[0],))
                self._mesh.set_face_property_array(name, data)
                self.signals.emit_attribChanged()
                return True
            except:
                self._mesh.remove_face_property(name)
                self._detailAttribute["face"].pop(name)

        try:
            if not hasAttrib:
                self._mesh.face_property(name)
                self._detailAttribute["face"][name] = None
            if type(data) is np.ndarray:
                data = data.tolist()
            self._mesh.set_face_property(name, data)
            self.signals.emit_attribChanged()
            return True
        except:
            self._mesh.remove_face_property(name)
            self._detailAttribute["face"].pop(name)
            return False

    def setEdgeAttribData(self, name, data, array=True):
        if self._processBuildinAttrib(self._mapGetData, 2, name, emit=True, data=data)[1]:
            return True
        hasAttrib = self._mesh.has_edge_property(name)
        if array and type(data) is np.ndarray:
            if not hasAttrib:
                self._mesh.edge_property_array(name)
                self._detailAttribute["edge"][name] = None
            try:
                if len(data.shape) == 2 and data.shape[1] == 1:
                    data = data.reshape((data.shape[0],))
                self._mesh.set_edge_property_array(name, data)
                self.signals.emit_attribChanged()
                return True
            except:
                self._mesh.remove_edge_property(name)
                self._detailAttribute["edge"].pop(name)
        try:
            if not hasAttrib:
                self._mesh.edge_property(name)
                self._detailAttribute["edge"][name] = None
            if type(data) is np.ndarray:
                data = data.tolist()
            self._mesh.set_edge_property(name, data)
            self.signals.emit_attribChanged()
            return True
        except:
            self._mesh.remove_edge_property(name)
            self._detailAttribute["edge"].pop(name)
            return False

    def getVertexAttrib(self, name, index):
        vh = self._mesh.vertex_handle(index)
        if self._mesh.has_vertex_property(name):
            return self._mesh.vertex_property(name, vh)

        return self._processBuildinAttrib(self._mapGetValue, 0, name, [vh])[0]

    def getFaceAttrib(self, name, index):
        fh = self._mesh.face_handle(index)
        if self._mesh.has_face_property(name):
            return self._mesh.face_property(name, fh)
        return self._processBuildinAttrib(self._mapGetValue, 1, name, [fh])[0]

    def getEdgeAttrib(self, name, index):
        eh = self._mesh.edge_handle(index)
        if self._mesh.has_edge_property(name):
            return self._mesh.edge_property(name, eh)
        return self._processBuildinAttrib(self._mapGetValue, 2, name, [eh])[0]

    def setVertexAttrib(self, name, index, value):
        vh = self._mesh.vertex_handle(index)
        if self._mesh.has_vertex_property(name):
            self._mesh.set_vertex_property(name, vh, value)
            self.signals.emit_attribChanged()
            return True
        return self._processBuildinAttrib(self._mapSetValue, 0, name, (vh, value), True)[1]

    def setFaceAttrib(self, name, index, value):
        fh = self._mesh.face_handle(index)
        if self._mesh.has_face_property(name):
            self._mesh.set_face_property(name, fh, value)
            self.signals.emit_attribChanged()
            return True
        return self._processBuildinAttrib(self._mapSetValue, 1, name, (fh, value), True)[1]

    def setEdgeAttrib(self, name, index, value):
        eh = self._mesh.edge_handle(index)
        if self._mesh.has_edge_property(name):
            self._mesh.set_edge_property(name, eh, value)
            self.signals.emit_attribChanged()
            return True
        return self._processBuildinAttrib(self._mapSetValue, 2, name, (eh, value), True)[1]

    def getDetailAttrib(self, name):
        if name in self._detailAttribute.keys():
            return self._detailAttribute[name]
        return None

    def setDetailAttrib(self, name, value):
        self._detailAttribute[name] = value
        self.signals.emit_attribChanged()

    def getAllVertexAttributes(self):
        data = {}
        for attrib_name in self._detailAttribute["vertex"].keys():
            try:
                d = self.getVertexAttribData(attrib_name, True)
            except:
                d = self.getVertexAttribData(attrib_name)
            data[attrib_name] = d
        return data

    def createGroup(self, level, name, default=False):
        if level == 'vertex':
            name = "v:" + name
            self._mesh.vertex_property(name)
            self._mesh.set_vertex_property(name, np.broadcast_to(default, (self.getNumVertexes(),)).tolist())
            self._detailAttribute['vertex'][name] = None
        elif level == 'face':
            name = "f:" + name
            self._mesh.face_property(name)
            self._mesh.set_face_property(name, np.broadcast_to(default, (self.getNumFaces(),)).tolist())
            self._detailAttribute['face'][name] = None
        elif level == 'edge':
            name = "e:" + name
            self._mesh.edge_property(name)
            self._mesh.set_edge_property(name, np.broadcast_to(default, (self.getNumEdges(),)).tolist())
            self._detailAttribute['edge'][name] = None

    def getGroupData(self, level, name):
        if level == 'vertex':
            name = "v:" + name
            if self._mesh.has_vertex_property(name):
                return self._mesh.vertex_property(name)
        elif level == 'face':
            name = "f:" + name
            if self._mesh.has_face_property(name):
                return self._mesh.face_property(name)
        elif level == 'edge':
            name = "e:" + name
            if self._mesh.has_edge_property(name):
                return self._mesh.edge_property(name)

    def setGroupData(self, level, name, data):
        if level == 'vertex':
            name = "v:" + name
            self.setVertexAttribData(name, data, False)
        elif level == 'face':
            name = "f:" + name
            self.setFaceAttribData(name, data, False)
        elif level == 'edge':
            name = "e:" + name
            self.setEdgeAttribData(name, data, False)

    def getGroup(self, level, name, index):
        if level == 'vertex':
            name = "v:" + name
            if self._mesh.has_vertex_property(name):
                vh = self._mesh.vertex_handle(index)
                return self._mesh.vertex_property(name, vh)
        elif level == 'face':
            name = "f:" + name
            if self._mesh.has_face_property(name):
                fh = self._mesh.face_handle(index)
                return self._mesh.face_property(name, fh)
        elif level == 'edge':
            name = "e:" + name
            if self._mesh.has_edge_property(name):
                eh = self._mesh.edge_handle(index)
                return self._mesh.edge_property(name, eh)

    def getGroupNames(self, allInOne=False):
        v = [i[2:] for i in self._detailAttribute["vertex"].keys() if ":" in i]
        f = [i[2:] for i in self._detailAttribute["face"].keys() if ":" in i]
        e = [i[2:] for i in self._detailAttribute["edge"].keys() if ":" in i]
        if allInOne:
            result = []
            result.extend(v)
            result.extend(f)
            result.extend(e)
        else:
            result = {'vertex': v,
                      'face': f,
                      'edge': e}
        return result

    def removeGroup(self, level, name):
        if level == 'vertex':
            name = "v:" + name
        elif level == 'face':
            name = "f:" + name
        elif level == 'edge':
            name = "e:" + name

        if ":" in name:
            self.removeAttribute(level, name)
