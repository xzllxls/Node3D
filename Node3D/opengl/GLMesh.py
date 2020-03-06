import numpy as np
from OpenGL.arrays import vbo
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
    float: 'float',
    int: 'int',
    bool: 'bool',
    str: 'str',
    list: 'list',
    tuple: 'tuple',
}

DEFAULT_VALUE_MAP = {
    "float": 0.0,
    "int": 0,
    "vector2": [0, 0],
    "vector3": [0, 0, 0],
    "vector4": [0, 0, 0, 0],
    "matrix3": np.identity(3, dtype=np.float64),
    "matrix4": np.identity(4, dtype=np.float64),
    "bool": False,
    "list": [],
    "tuple": {},
    "custom": None,
    "str": '',
}

DATA_IS_ARRAY_MAP = {
    "float": True,
    "int": True,
    "vector2": True,
    "vector3": True,
    "vector4": True,
    "matrix3": True,
    "matrix4": True,
    "bool": False,
    "list": False,
    "tuple": False,
    "custom": False,
    "str": False,
}

DATA_SHAPE_MAP = {
    "float": None,
    "int": None,
    "vector2": [0, 2],
    "vector3": [0, 3],
    "vector4": [0, 4],
    "matrix3": [0, 3, 3],
    "matrix4": [0, 4, 4],
    "bool": None,
    "list": None,
    "tuple": None,
    "custom": None,
    "str": None,
}


def get_shape(element_num, base_shape):
    if base_shape is None:
        shape = (element_num,)
    else:
        base_shape[0] = element_num
        shape = tuple(base_shape)
    return shape


class Mesh(object):
    def __init__(self, mesh=None):

        self.opts = {
            'color': (1., 1., 1.),
            'edgeColor': (0.5, 0.5, 0.5),
            'pointColor': (1.0, 1.0, 0.0),
            'shader': standShader,
            'smooth': True,
            'computeNormals': False,
        }

        self._attributeMap = {
            "vertex": {
                "pos": {'default_value': [0, 0, 0], 'type': 'vector3', 'is_array': True}
            },
            "face": {},
            "edge": {},
            "detail": {}
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

        self._GLFaces = None
        self._flatColor = 0
        self.__view = None

    @property
    def meshFuncs(self):
        """
        get a object which contains some utility mesh functions
        @return: MeshFuncs object
        """
        return MeshFuncs(self)

    @property
    def mesh(self):
        """
        get the real mesh object
        @return: openmesh.PolyMesh
        """
        return self._mesh

    @property
    def bbox_min(self):
        """
        get bounding box min value
        @return: list
        """
        vts = self.getVertexes()
        if vts is None:
            return [0, 0, 0]
        self._bbox_min = list(np.min(vts, axis=0))
        return self._bbox_min

    @property
    def bbox_max(self):
        """
        get bounding box max value
        @return: list
        """
        vts = self.getVertexes()
        if vts is None:
            return [0, 0, 0]
        self._bbox_max = list(np.max(vts, axis=0))
        return self._bbox_max

    @property
    def bbox_center(self):
        """
        get bounding box center value
        @return: list
        """
        _, __, self._bbox_center = self.get_bbox_info()
        return self._bbox_center

    def get_bbox_info(self):
        """
        get bounding box min, max, center
        @return: min->list, max->list, center->list
        """
        _min = self.bbox_min
        _max = self.bbox_max
        _center = [(_min[0] + _max[0]) / 2.0,
                   (_min[1] + _max[1]) / 2.0,
                   (_min[2] + _max[2]) / 2.0]
        return _min, _max, _center

    def visible(self):
        return True

    def _setView(self, v):
        self.__view = v

    def view(self):
        return self.__view

    def update(self):
        v = self.view()
        if v is None:
            return
        v.update()

    def update_GLFace(self):
        """
        prepare the mesh data for OpenGL
        """
        b = self.getTriangulateMesh()
        self._GLFaces = b.face_vertex_indices()

    def getTriangulateMesh(self):
        """
        triangulate all faces and return a new mesh
        @return: openmesh.PolyMesh
        """
        b = copy.deepcopy(self._mesh)
        b.triangulate()
        return b

    def setFlatColor(self, mode):
        """
        set if use flat color for render
        @param mode: True means use flat color
        """
        if mode is True:
            self._flatColor = 1
        else:
            self._flatColor = 0

    def setSelected(self, sel):
        self._selected = sel
        # self.opts['edgeColor'] = self.edge_colors[False]
        self.update()

    def getSelected(self):
        return self._selected

    def drawBBox(self):
        _min, _max, _center = self.get_bbox_info()
        size = [abs(_min[0] - _max[0]),
                abs(_min[1] - _max[1]),
                abs(_min[2] - _max[2])]

        tr = self.bbox.set(_center, size)
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
            if self._mesh.has_vertex_property("pscale"):
                pscale = self.getVertexAttribData("pscale")
            else:
                pscale = None
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
        """
        get mesh vertex positions
        @return: np.ndarray, shape = (nv,3)
        """
        p = self._mesh.points()
        if p.shape[0] == 0:
            return None
        return p

    def getFaces(self):
        """
        get mesh faces-vertex indices
        @return: list of np.ndarray or None
        """
        f = self._mesh.face_vertex_indices()
        if f.shape[0] == 0:
            return None
        return [face[face >= 0] for face in f]

    def getColors(self):
        """
        get mesh vertex colors
        @return: np.ndarray, shape = (nv,3) or None
        """
        if self.hasAttribute('vertex', 'color'):
            return self.getVertexAttribData("color")
        else:
            return None

    def getUVs(self):
        """
        get mesh vertex texcoords
        @return: np.ndarray, shape = (nv,3) or None
        """
        if self.hasAttribute('vertex', 'uv'):
            uv = self.getVertexAttribData("uv")
            return uv
        return None

    def getNormals(self):
        """
        get mesh vertex normals
        @return: np.ndarray, shape = (nv,3) or None
        """
        if not self.hasAttribute('vertex', 'normal'):
            if self.getNumFaces() == 0:
                return None
            self.createAttribute('vertex', 'normal', attribType='vector3', defaultValue=[0, 0, 0], applyValue=False)
            self._mesh.update_vertex_normals()
        return self._mesh.vertex_normals()

    def getFaceNormals(self):
        """
        get mesh face normals
        @return: np.ndarray, shape = (nf,3) or None
        """
        if not self.hasAttribute('face', 'normal'):
            if self.getNumFaces() == 0:
                return None
            self.createAttribute('face', 'normal', attribType='vector3', defaultValue=[0, 0, 0], applyValue=False)
            self._mesh.update_face_normals()
        return self._mesh.face_normals()

    def getVertexFaces(self):
        """
        get mesh vertex-face indices
        @return: list of np.ndarray
        """
        vf = self._mesh.vertex_face_indices()
        return [face[face >= 0] for face in vf]

    def getEdges(self):
        """
        get mesh edge-vertex indices
        @return: np.ndarray or None
        """
        e = self._mesh.edge_vertex_indices()
        if e.shape[0] == 0:
            return None
        return e

    def getNumVertexes(self):
        """
        get mesh vertices count
        @return: int
        """
        return self._mesh.n_vertices()

    def getNumFaces(self):
        """
        get mesh faces count
        @return: int
        """
        return self._mesh.n_faces()

    def getNumEdges(self):
        """
        get mesh edges count
        @return: int
        """
        return self._mesh.n_edges()

    @property
    def attributeMap(self):
        """
        @return: dict
        """
        return self._attributeMap

    def getAttribNames(self, allInOne=False, with_group=False):
        """
        get attribute names of the mesh
        @param allInOne: return all names in one list
        @param with_group: return names with group names
        @return:  dict or list
        """
        if with_group:
            v = list(self._attributeMap["vertex"].keys())
            f = list(self._attributeMap["face"].keys())
            e = list(self._attributeMap["edge"].keys())
        else:
            v = [i for i in self._attributeMap["vertex"].keys() if ":" not in i]
            f = [i for i in self._attributeMap["face"].keys() if ":" not in i]
            e = [i for i in self._attributeMap["edge"].keys() if ":" not in i]
        d = list(self._attributeMap["detail"].keys())
        if allInOne:
            result = []
            result.extend(v)
            result.extend(f)
            result.extend(e)
            result.extend(d)
        else:
            result = {'vertex': v,
                      'face': f,
                      'edge': e,
                      'detail': d}
        return result

    def _getAttribType(self, attribClass, name):
        """
        get attribute value type
        @param attribClass: one of ['vertex', 'edge', 'face', 'detail']
        @param name: specific attribute name
        @return: str
        """
        if attribClass == "vertex":
            value = self.getVertexAttrib(name, 0)
        elif attribClass == "edge":
            value = self.getEdgeAttrib(name, 0)
        elif attribClass == "face":
            value = self.getFaceAttrib(name, 0)
        elif attribClass == "detail":
            value = self.getDetailAttrib(name)
        else:
            return 'none'
        checkType = type(value)
        if checkType is np.ndarray or checkType is list:
            if checkType is np.ndarray:
                size = value.size
            else:
                size = len(value)
            if size == 2:
                return 'vector2'
            elif size == 3:
                return 'vector3'
            elif size == 4:
                return 'vector4'
            elif size == 9:
                return 'matrix3'
            elif size == 16:
                return 'matrix4'
        return DATA_TYPE_MAP.get(checkType, 'none')

    def getAttribType(self, attribClass, name):
        """
        get attribute type
        @param attribClass: one of ['vertex', 'edge', 'face', 'detail']
        @param name: specific attribute name
        @return: attribute type -> str
        """
        if not self.hasAttribute(attribClass, name):
            raise AttributeError("the attribute does't exist!")
        return self._attributeMap[attribClass][name]['type']

    def getAttribDefaultValue(self, attribClass, name):
        """
        get attribute default value
        @param attribClass: one of ['vertex', 'edge', 'face', 'detail']
        @param name: specific attribute name
        @return: default attribute value
        """
        if not self.hasAttribute(attribClass, name):
            raise AttributeError("the attribute does't exist!")
        return self._attributeMap[attribClass][name]['default_value']

    def getAttribIsArray(self, attribClass, name):
        """
        get if attribute is array
        @param attribClass: one of ['vertex', 'edge', 'face', 'detail']
        @param name: specific attribute name
        @return: bool
        """
        if not self.hasAttribute(attribClass, name):
            raise AttributeError("the attribute does't exist!")
        return self._attributeMap[attribClass][name]['is_array']

    def getAttribInfo(self, attribClass, name):
        return self._attributeMap[attribClass][name]

    def setAttribInfo(self, attribClass, name, info):
        self._attributeMap[attribClass][name] = info

    def createAttribute(self, attribClass, name, attribType=None, defaultValue=None, applyValue=True):
        """
        create a new attribute
        @param attribClass: one of ['vertex', 'edge', 'face', 'detail']
        @param name: specific attribute name
        @param attribType: type of the attribute value->[float, int, vector2, vector3, vector4, matrix3, matrix4 , bool, list, tuple, custom]
        @defaultValue: default value of the attribute
        @applyValue: apply the default value
        """
        if attribType is None:
            attribType = self._getAttribType(attribClass, name)
        if defaultValue is None:
            defaultValue = DEFAULT_VALUE_MAP.get(attribType, None)

        array_mode = DATA_IS_ARRAY_MAP.get(attribType, False)
        shape = DATA_SHAPE_MAP.get(attribType, None)
        if attribType == 'list':
            shape = [0, len(defaultValue)]

        if attribClass == "vertex":
            if name == 'pos':
                return
            if array_mode:
                self._mesh.vertex_property_array(name)
            else:
                self._mesh.vertex_property(name)
            if applyValue:
                data = np.broadcast_to(defaultValue, get_shape(self.getNumVertexes(), shape))
                if array_mode:
                    self._mesh.set_vertex_property_array(name, data)
                else:
                    self._mesh.set_vertex_property(name, list(data))
        elif attribClass == "face":
            if array_mode:
                self._mesh.face_property_array(name)
            else:
                self._mesh.face_property(name)
            if applyValue:
                data = np.broadcast_to(defaultValue, get_shape(self.getNumFaces(), shape))
                if array_mode:
                    self._mesh.set_face_property_array(name, data)
                else:
                    self._mesh.set_face_property(name, list(data))
        elif attribClass == "edge":
            if array_mode:
                self._mesh.edge_property_array(name)
            else:
                self._mesh.edge_property(name)
            if applyValue:
                data = np.broadcast_to(defaultValue, get_shape(self.getNumEdges(), shape))
                if array_mode:
                    self._mesh.set_edge_property_array(name, data)
                else:
                    self._mesh.set_edge_property(name, list(data))
        elif attribClass == "detail":
            array_mode = False
        else:
            raise AttributeError("please input attribute class in ['vertex', 'edge', 'face', 'detail']")

        self._attributeMap[attribClass][name] = {'default_value': defaultValue, 'type': attribType,
                                                 'is_array': array_mode}

    def removeAttribute(self, attribClass, name):
        """
        remove a attribute
        @param attribClass: one of ['vertex', 'edge', 'face', 'detail']
        @param name: specific attribute name
        """
        if attribClass == "vertex":
            if name == 'pos':
                return
            if self._mesh.has_vertex_property(name):
                self._mesh.remove_vertex_property(name)
                self._attributeMap["vertex"].pop(name)
        elif attribClass == "face":
            if self._mesh.has_face_property(name):
                self._mesh.remove_face_property(name)
                self._attributeMap["face"].pop(name)
        elif attribClass == "edge":
            if self._mesh.has_edge_property(name):
                self._mesh.remove_edge_property(name)
                self._attributeMap["edge"].pop(name)
        elif attribClass == "detail":
            if name in self._attributeMap["detail"].keys():
                self._attributeMap["detail"].pop(name)

    def renameAttribute(self, attribClass, name, new_name):
        """
        rename a attribute
        @param attribClass: one of ['vertex', 'edge', 'face', 'detail']
        @param name: specific attribute name
        @param new_name: new attribute name
        """
        self.copyAttribute(attribClass, name, new_name, True)

    def copyAttribute(self, attribClass, from_name, to_name, remove=False):
        """
        copy attribute data to a new attribute
        @param attribClass: one of ['vertex', 'edge', 'face', 'detail']
        @param from_name: specific attribute name
        @param to_name: new attribute name
        @param remove: remove the from attribute
        """
        if not self.hasAttribute(attribClass, from_name):
            raise AttributeError("attribute {} of {} not exist".format(from_name, attribClass))
        if from_name == to_name:
            return

        attrib_type = self.getAttribType(attribClass, from_name)
        default_value = self.getAttribDefaultValue(attribClass, from_name)

        if attribClass == "vertex":
            a = self.getVertexAttribData(from_name)
            self.setVertexAttribData(to_name, a, attrib_type, default_value)
        elif attribClass == "face":
            a = self.getFaceAttribData(from_name)
            self.setFaceAttribData(to_name, a, attrib_type, default_value)
        elif attribClass == "edge":
            a = self.getEdgeAttribData(from_name)
            self.setEdgeAttribData(to_name, a, attrib_type, default_value)
        elif attribClass == "detail":
            self.createAttribute("detail", to_name, attrib_type, default_value)

        if remove:
            self.removeAttribute(attribClass, from_name)

    def hasAttribute(self, attribClass, name):
        """
        if the mesh contains a specific attribute
        @param attribClass: one of ['vertex', 'edge', 'face', 'detail']
        @param name: specific attribute name
        @return: True or False
        """
        if attribClass in self._attributeMap.keys():
            if name in self._attributeMap[attribClass].keys():
                return True
        return False

    def addVertex(self, pos):
        """
        add a vertex to the mesh
        @param pos: position of the new vertex, type can be: [list,ndarray,tuple]
        @return: openmesh.VertexHandle
        """
        if type(pos) is list:
            return self._mesh.add_vertex(np.array(pos))
        elif type(pos) is np.ndarray:
            return self._mesh.add_vertex(pos)
        elif type(pos) is tuple:
            return self._mesh.add_vertex(np.array([pos[0], pos[1], pos[2]]))

    def addFace(self, vts):
        """
        add a face to the mesh
        @param vts: vertices of the new face, type can be: list of [openmesh.VertexHandle, int]
        @return: openmesh.FaceHandle
        """
        self._GLFaces = None
        if type(vts[0]) is openmesh.VertexHandle:
            return self._mesh.add_face(vts)
        else:
            return self._mesh.add_face([self._mesh.vertex_handle(i) for i in vts])

    def addVertices(self, vts):
        """
        add vertices to the mesh
        @param vts: new vertices , np.ndarray or list, shape = (n,3)
        """
        self._GLFaces = None
        self._mesh.add_vertices(vts)

    def addFaces(self, fcs):
        """
        add faces to the mesh
        @param fcs: new faces , np.ndarray or list of ndarray
        """
        self._GLFaces = None
        self._mesh.add_faces(fcs)

    def removeVertex(self, vt, isolate=False, clean=True):
        """
        remove a vertex
        @param vt: vertex index or vertex handle
        @param isolate: if True, delete the connected elements
        @param clean: if True, garbage collection after delete
        """
        if type(vt) is not openmesh.VertexHandle:
            vt = self._mesh.vertex_handle(vt)
        if vt.idx() < self.getNumVertexes():
            self._mesh.delete_vertex(vt, isolate)
            if clean:
                self._mesh.garbage_collection()
            self._GLFaces = None

    def removeFace(self, fc, isolate=False, clean=True):
        """
        remove a face
        @param fc: face index or face handle
        @param isolate: if True, delete the connected elements
        @param clean: if True, garbage collection after delete
        """
        if type(fc) is not openmesh.FaceHandle:
            fc = self._mesh.face_handle(fc)
        if fc.idx() < self.getNumFaces():
            self._mesh.delete_face(fc, isolate)
            if clean:
                self._mesh.garbage_collection()
            self._GLFaces = None

    def removeEdge(self, eg, isolate=False, clean=True):
        """
        remove a edge
        @param eg: edge index or edge handle
        @param isolate: if True, delete the connected elements
        @param clean: if True, garbage collection after delete
        """
        if type(eg) is not openmesh.EdgeHandle:
            eg = self._mesh.edge_handle(eg)
        if eg.idx() < self.getNumEdges():
            self._mesh.delete_edge(eg, isolate)
            if clean:
                self._mesh.garbage_collection()
            self._GLFaces = None

    def removeVertices(self, vts, isolate=False):
        """
        remove vertices
        @param vts: list of vertex index or list of vertex handle
        @param isolate: if True, delete the connected elements
        """
        for vt in vts:
            self.removeVertex(vt, isolate, False)
        self._mesh.garbage_collection()

    def removeFaces(self, fcs, isolate=False):
        """
        remove faces
        @param fcs: list of face index or list of face handle
        @param isolate: if True, delete the connected elements
        """
        for fc in fcs:
            self.removeFace(fc, isolate, False)
        self._mesh.garbage_collection()

    def removeEdges(self, egs, isolate=False):
        """
        remove edges
        @param egs: list of edge index or list of edge handle
        @param isolate: if True, delete the connected elements
        """
        for eg in egs:
            self.removeEdge(eg, isolate, False)
        self._mesh.garbage_collection()

    def clear(self):
        """
        clear all mesh data
        """
        self._mesh.clear()
        self._attributeMap = {}
        self.signals.emit_attribChanged()
        self.update()

    def getVertexAttribData(self, name):
        """
        get vertex attribute data
        @param name: specific attribute name
        """
        if name == 'pos':
            return self._mesh.points()
        elif name == 'normal':
            return self.getNormals()
        else:
            if not self.hasAttribute('vertex', name):
                raise AttributeError("Attribute {} does't exist!".format(name))
            if self.getAttribIsArray('vertex', name):
                return self._mesh.vertex_property_array(name)
            else:
                return self._mesh.vertex_property(name)

    def getFaceAttribData(self, name):
        """
        get face attribute data
        @param name: specific attribute name
        """
        if name == 'normal':
            return self.getFaceNormals()
        else:
            if not self._mesh.has_face_property(name):
                raise AttributeError("Attribute {} does't exist!".format(name))
            if self.getAttribIsArray('face', name):
                return self._mesh.face_property_array(name)
            else:
                return self._mesh.face_property(name)

    def getEdgeAttribData(self, name):
        """
        get edge attribute data
        @param name: specific attribute name
        """
        if not self._mesh.has_edge_property(name):
            raise AttributeError("Attribute {} does't exist!".format(name))
        if self.getAttribIsArray('edge', name):
            return self._mesh.edge_property_array(name)
        else:
            return self._mesh.edge_property(name)

    def setVertexAttribData(self, name, data, attribType=None, defaultValue=None):
        """
        set vertex attribute data , if the attribute not exist, create and set it
        @param name: specific attribute name
        @param data: attribute data
        @param attribType: if the attribute is not exist, we need attribType to create the attribute
        @param defaultValue: if the attribute is not exist, we need defaultValue to create the attribute
        """
        if name == 'pos':
            self._mesh.points()[..., [0, 1, 2]] = data
        elif name == 'normal':
            self.getNormals()[..., [0, 1, 2]] = data
        else:
            if not self._mesh.has_vertex_property(name):
                if defaultValue is None:
                    defaultValue = data[0]
                self.createAttribute('vertex', name, attribType, defaultValue=defaultValue, applyValue=False)
            is_array = self.getAttribIsArray('vertex', name)

            if is_array:
                self._mesh.set_vertex_property_array(name, data)
            else:
                self._mesh.set_vertex_property(name, data)
        self.signals.emit_attribChanged()

    def setFaceAttribData(self, name, data, attribType=None, defaultValue=None):
        """
        set face attribute data , if the attribute not exist, create and set it
        @param name: specific attribute name
        @param data: attribute data
        @param attribType: if the attribute is not exist, we need attribType to create the attribute
        @param defaultValue: if the attribute is not exist, we need defaultValue to create the attribute
        """
        if name == 'normal':
            self.getFaceNormals()[..., [0, 1, 2]] = data
        else:
            if not self._mesh.has_face_property(name):
                if defaultValue is None:
                    defaultValue = data[0]
                self.createAttribute('face', name, attribType, defaultValue=defaultValue, applyValue=False)
            is_array = self.getAttribIsArray('face', name)

            if is_array:
                self._mesh.set_face_property_array(name, data)
            else:
                self._mesh.set_face_property(name, data)
        self.signals.emit_attribChanged()

    def setEdgeAttribData(self, name, data, attribType=None, defaultValue=None):
        """
        set edge attribute data , if the attribute not exist, create and set it
        @param name: specific attribute name
        @param data: attribute data
        @param attribType: if the attribute is not exist, we need attribType to create the attribute
        @param defaultValue: if the attribute is not exist, we need defaultValue to create the attribute
        """
        if not self._mesh.has_edge_property(name):
            if defaultValue is None:
                defaultValue = data[0]
            self.createAttribute('edge', name, attribType, defaultValue=defaultValue, applyValue=False)
        is_array = self.getAttribIsArray('edge', name)

        if is_array:
            self._mesh.set_edge_property_array(name, data)
        else:
            self._mesh.set_edge_property(name, data)

        self.signals.emit_attribChanged()

    def getVertexAttrib(self, name, index):
        """
        get a vertex attribute value
        @param name: specific attribute name
        @param index: vertex index
        """
        vh = self._mesh.vertex_handle(index)
        if self._mesh.has_vertex_property(name):
            return self._mesh.vertex_property(name, vh)
        if name == 'pos':
            return self._mesh.point(vh)
        elif name == 'normal':
            return self._mesh.normal(vh)

    def getFaceAttrib(self, name, index):
        """
        get a face attribute value
        @param name: specific attribute name
        @param index: face index
        """
        fh = self._mesh.face_handle(index)
        if self._mesh.has_face_property(name):
            return self._mesh.face_property(name, fh)
        if name == 'normal':
            return self._mesh.normal(fh)

    def getEdgeAttrib(self, name, index):
        """
        get a edge attribute value
        @param name: specific attribute name
        @param index: edge index
        """
        eh = self._mesh.edge_handle(index)
        if self._mesh.has_edge_property(name):
            return self._mesh.edge_property(name, eh)
        return None

    def setVertexAttrib(self, name, index, value):
        """
        set a vertex attribute value
        @param name: specific attribute name
        @param index: vertex index
        @param value: attribute value
        """
        vh = self._mesh.vertex_handle(index)
        if self._mesh.has_vertex_property(name):
            self._mesh.set_vertex_property(name, vh, value)
            self.signals.emit_attribChanged()
            return True
        if name == 'pos':
            self._mesh.set_point(vh, value)
            return True
        elif name == 'normal':
            self._mesh.set_normal(vh, value)
            return True
        return False

    def setFaceAttrib(self, name, index, value):
        """
        set a face attribute value
        @param name: specific attribute name
        @param index: face index
        @param value: attribute value
        """
        fh = self._mesh.face_handle(index)
        if self._mesh.has_face_property(name):
            self._mesh.set_face_property(name, fh, value)
            self.signals.emit_attribChanged()
            return True
        if name == 'normal':
            self._mesh.set_normal(fh, value)
            return True
        return False

    def setEdgeAttrib(self, name, index, value):
        """
        set a edge attribute value
        @param name: specific attribute name
        @param index: edge index
        @param value: attribute value
        """
        eh = self._mesh.edge_handle(index)
        if self._mesh.has_edge_property(name):
            self._mesh.set_edge_property(name, eh, value)
            self.signals.emit_attribChanged()
            return True
        return False

    def getDetailAttrib(self, name):
        """
        get a detail attribute value
        @param name: specific attribute name
        """
        if name in self._attributeMap['detail'].keys():
            return self._attributeMap['detail'][name]['default_value']
        return None

    def setDetailAttrib(self, name, value, attribType=None):
        """
        set a detail attribute value
        @param name: specific attribute name
        @param value: attribute value
        @param attribType: if the attribute is not exist, we need attribType to create the attribute
        """
        if name in self._attributeMap['detail'].keys():
            self._attributeMap['detail'][name]['default_value'] = value
        else:
            if attribType is None:
                raise AttributeError("detail attribute {} not exist, please create it or input attribType".format(name))
            self.createAttribute('detail', name, attribType, value)
        self.signals.emit_attribChanged()

    def getAllVertexAttributes(self):
        """
        get all vertex attribute data
        @return: dict {attribute name: attribute data}
        """
        data = {}
        for attrib_name in self._attributeMap["vertex"].keys():
            data[attrib_name] = self.getVertexAttribData(attrib_name)
        return data

    def createGroup(self, attribClass, name, default=False):
        """
        create a group
        @param attribClass: one of ['vertex', 'edge', 'face']
        @param name: specific group name
        @param default: if True, all elements will in the group
        """
        if attribClass == 'vertex':
            name = "v:" + name
        elif attribClass == 'face':
            name = "f:" + name
        elif attribClass == 'edge':
            name = "e:" + name

        self.createAttribute(attribClass, name, 'bool', default)

    def getGroupData(self, attribClass, name):
        """
        get group data
        @param attribClass: one of ['vertex', 'edge', 'face']
        @param name: specific group name
        @return: list of bool
        """
        if attribClass == 'vertex':
            name = "v:" + name
            if self._mesh.has_vertex_property(name):
                return self._mesh.vertex_property_array(name).astype(np.bool)
        elif attribClass == 'face':
            name = "f:" + name
            if self._mesh.has_face_property(name):
                return self._mesh.face_property_array(name).astype(np.bool)
        elif attribClass == 'edge':
            name = "e:" + name
            if self._mesh.has_edge_property(name):
                return self._mesh.edge_property_array(name).astype(np.bool)
        else:
            raise AttributeError("class {} does not support group".format(attribClass))

        raise AttributeError("Group {} does not exist".format(name))

    def setGroupData(self, attribClass, name, data):
        """
        set group data
        @param attribClass: one of ['vertex', 'edge', 'face']
        @param name: specific group name
        @data: list of bool
        """
        if attribClass == 'vertex':
            name = "v:" + name
            self.setVertexAttribData(name, data, 'bool', False)
        elif attribClass == 'face':
            name = "f:" + name
            self.setFaceAttribData(name, data, 'bool', False)
        elif attribClass == 'edge':
            name = "e:" + name
            self.setEdgeAttribData(name, data, 'bool', False)

    def getGroup(self, attribClass, name, index):
        """
        get if a specific element is in the group
        @param attribClass: one of ['vertex', 'edge', 'face']
        @param name: specific group name
        @index: element index
        @return: bool
        """
        if attribClass == 'vertex':
            name = "v:" + name
            if self._mesh.has_vertex_property(name):
                vh = self._mesh.vertex_handle(index)
                return bool(self._mesh.vertex_property(name, vh))
        elif attribClass == 'face':
            name = "f:" + name
            if self._mesh.has_face_property(name):
                fh = self._mesh.face_handle(index)
                return bool(self._mesh.face_property(name, fh))
        elif attribClass == 'edge':
            name = "e:" + name
            if self._mesh.has_edge_property(name):
                eh = self._mesh.edge_handle(index)
                return bool(self._mesh.edge_property(name, eh))

    def setGroup(self, attribClass, name, index, value):
        """
        set if a specific element is in the group
        @param attribClass: one of ['vertex', 'edge', 'face']
        @param name: specific group name
        @index: element index
        @value: bool
        """
        assert type(value) is bool
        if attribClass == 'vertex':
            self.setVertexAttrib("v:" + name, index, value)
        elif attribClass == 'face':
            self.setFaceAttrib("f:" + name, index, value)
        elif attribClass == 'edge':
            self.setEdgeAttrib("e:" + name, index, value)

    def getGroupNames(self, allInOne=False):
        """
        get all group names of the mesh
        @param allInOne: put all names in one list
        @return: dict or list
        """
        v = [i[2:] for i in self._attributeMap["vertex"].keys() if ":" in i]
        f = [i[2:] for i in self._attributeMap["face"].keys() if ":" in i]
        e = [i[2:] for i in self._attributeMap["edge"].keys() if ":" in i]
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

    def removeGroup(self, attribClass, name):
        """
        remove a group
        @param attribClass: one of ['vertex', 'edge', 'face']
        @param name: specific group name
        """
        if attribClass == 'vertex':
            name = "v:" + name
        elif attribClass == 'face':
            name = "f:" + name
        elif attribClass == 'edge':
            name = "e:" + name

        if ":" in name:
            self.removeAttribute(attribClass, name)

    def hasGroup(self, attribClass, name):
        """
        get if the mesh have a specific group
        @param attribClass: one of ['vertex', 'edge', 'face']
        @param name: specific group name
        """
        if attribClass == 'vertex':
            name = "v:" + name
        elif attribClass == 'face':
            name = "f:" + name
        elif attribClass == 'edge':
            name = "e:" + name

        if ":" in name:
            return self.hasAttribute(attribClass, name)
        else:
            return False
