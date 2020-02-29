from Node3D.base.node import GeometryNode
import numpy as np


class Get_Attribute_Data(GeometryNode):
    __identifier__ = 'Attribute'
    NODE_NAME = 'Get_Attribute_Data'

    def __init__(self):
        super(Get_Attribute_Data, self).__init__(False)
        self.create_property("out data", None)
        self.add_input("geo", GeometryNode)
        self.add_output("out data", np.ndarray)
        self.set_parameters([{'name': 'Attribute Class', 'type': 'list', 'value': 'vertex',
                              'limits': ['vertex', 'edge', 'face', 'detail']},
                             {'name': 'Attribute Name', 'type': 'listText'}])

    def getData(self, port):
        try:
            return self.get_property('out data')
        except:
            return None

    def run(self):
        geo = self.getInputGeometryRef(0)
        if geo is None:
            self.set_property("out data", None)
            self.error("Please input a geometry")
            return

        attrib_class = self.get_property('Attribute Class')
        self.update_list_text_param('Attribute Name', geo.getAttribNames()[attrib_class])

        attrib_name = self.get_property('Attribute Name')
        if not geo.hasAttribute(attrib_class, attrib_name):
            self.set_property("out data", None)
            return

        if attrib_class == 'vertex':
            data = geo.getVertexAttribData(attrib_name)
        elif attrib_class == 'edge':
            data = geo.getEdgeAttribData(attrib_name)
        elif attrib_class == 'face':
            data = geo.getFaceAttribData(attrib_name)
        elif attrib_class == 'detail':
            data = geo.getDetailAttrib(attrib_name)

        self.set_property("out data", data)


class Set_Attribute_Data(GeometryNode):
    __identifier__ = 'Attribute'
    NODE_NAME = 'Set_Attribute_Data'

    def __init__(self):
        super(Set_Attribute_Data, self).__init__()
        self.create_property("out data", None)
        self.add_input("geo", GeometryNode)
        self.add_input("in data", np.ndarray)

        self.set_parameters([{'name': 'Attribute Class', 'type': 'list', 'value': 'vertex',
                              'limits': ['vertex', 'edge', 'face', 'detail']},
                             {'name': 'Attribute Name', 'type': 'listText'}])

    def run(self):
        if not self.copyData():
            return

        attrib_class = self.get_property('Attribute Class')
        self.update_list_text_param('Attribute Name', self.geo.getAttribNames()[attrib_class])

        attrib_name = self.get_property('Attribute Name')
        if not self.geo.hasAttribute(attrib_class, attrib_name):
            return

        data = self.getInputData(1)
        if data is None:
            return

        if attrib_class == 'detail':
            self.geo.setDetailAttrib(attrib_name, data)
            return

        if not isinstance(data, np.ndarray):
            self.error("data type not match")
            return

        if attrib_class == 'vertex':
            if data.shape[0] != self.geo.getNumVertexes():
                self.error("data size not match")
                return
            self.geo.setVertexAttribData(attrib_name, data)
        elif attrib_class == 'edge':
            if data.shape[0] != self.geo.getNumEdges():
                self.error("data size not match")
                return
            self.geo.setEdgeAttribData(attrib_name, data)
        elif attrib_class == 'face':
            if data.shape[0] != self.geo.getNumFaces():
                self.error("data size not match")
                return
            self.geo.setFaceAttribData(attrib_name, data)


class Attribute_Delete(GeometryNode):
    __identifier__ = 'Attribute'
    NODE_NAME = 'Attribute_Delete'

    def __init__(self):
        super(Attribute_Delete, self).__init__()
        self.set_parameters([{'name': 'Attribute Class', 'type': 'list', 'value': 'vertex',
                              'limits': ['vertex', 'edge', 'face', 'detail']},
                             {'name': 'Attribute Name', 'type': 'listText'}])
        self.add_input("geo", GeometryNode)

    def run(self):
        if not self.copyData():
            return

        attrib_class = self.get_property('Attribute Class')
        self.update_list_text_param('Attribute Name', self.geo.getAttribNames()[attrib_class])
        attrib_name = self.get_property('Attribute Name')
        if not self.geo.hasAttribute(attrib_class, attrib_name):
            return
        self.geo.removeAttribute(attrib_class, attrib_name)


class Attribute_Create(GeometryNode):
    __identifier__ = 'Attribute'
    NODE_NAME = 'Attribute_Create'

    def __init__(self):
        super(Attribute_Create, self).__init__()
        self.set_parameters([{'name': 'Attribute Class', 'type': 'list', 'value': 'vertex',
                              'limits': ['vertex', 'edge', 'face', 'detail']},
                             {'name': 'Attribute Name', 'type': 'str'},
                             {'name': 'Attribute Type', 'type': 'list', 'value': 'float',
                              'limits': ['float', 'int', 'vector2', 'vector3', 'vector4', 'boolean', 'string']},
                             {'name': 'Attribute Value', 'type': 'str', 'value': '0.0'}])
        self.add_input("geo", GeometryNode)

    def run(self):
        if not self.copyData():
            return
        attrib_name = self.get_property('Attribute Name')
        if not attrib_name:
            return

        attrib_type = self.get_property('Attribute Type')

        try:
            value = self.get_property('Attribute Value')
            if attrib_type != 'string':
                value = eval(value)
        except:
            self.error('please input a valid value')
            return

        dtype = np.float64
        dim = 1
        array = True
        if attrib_type == 'float':
            value = float(value)
        elif attrib_type == 'int':
            array = False
            dtype = np.int32
            value = int(value)
        elif attrib_type == 'boolean':
            array = False
            dtype = np.bool_
            value = bool(value)
        elif attrib_type == 'string':
            array = False
            dtype = np.str_
            value = str(value)
        else:
            if type(value) is not list:
                self.error('please input a list value')
                return
            if attrib_type == 'vector3':
                if len(value) != 3:
                    self.error('please input a list with 3 values')
                    return
                dim = 3
            elif attrib_type == 'vector2':
                if len(value) != 2:
                    self.error('please input a list with 2 values')
                    return
                dim = 2
            elif attrib_type == 'vector4':
                if len(value) != 4:
                    self.error('please input a list with 4 values')
                    return
                dim = 4
            else:
                return

        attrib_class = self.get_property('Attribute Class')

        if attrib_class == 'vertex':
            if dim == 1:
                data = np.broadcast_to(value, (self.geo.getNumVertexes(),)).astype(dtype)
            else:
                data = np.broadcast_to(value, (self.geo.getNumVertexes(), dim)).astype(dtype)
            self.geo.setVertexAttribData(attrib_name, data, array)
        elif attrib_class == 'face':
            if dim == 1:
                data = np.broadcast_to(value, (self.geo.getNumFaces(),)).astype(dtype)
            else:
                data = np.broadcast_to(value, (self.geo.getNumFaces(), dim)).astype(dtype)
            self.geo.setFaceAttribData(attrib_name, data, array)
        elif attrib_class == 'edge':
            if dim == 1:
                data = np.broadcast_to(value, (self.geo.getNumEdges(),)).astype(dtype)
            else:
                data = np.broadcast_to(value, (self.geo.getNumEdges(), dim)).astype(dtype)
            self.geo.setEdgeAttribData(attrib_name, data, array)
        elif attrib_class == 'detail':
            self.geo.detailAttribute[attrib_name] = value


class Attribute_Promote(GeometryNode):
    __identifier__ = 'Attribute'
    NODE_NAME = 'Attribute_Promote'

    def __init__(self):
        super(Attribute_Promote, self).__init__()
        self.set_parameters(
            [{'name': 'From', 'type': 'list', 'value': 'vertex', 'limits': ['vertex', 'edge', 'face', 'detail']},
             {'name': 'To', 'type': 'list', 'value': 'vertex', 'limits': ['vertex', 'edge', 'face', 'detail']},
             {'name': 'Attribute Name', 'type': 'listText'},
             {'name': 'New Attribute Name', 'type': 'str'},
             {'name': 'Delete Origin', 'type': 'bool', 'value': True}])

        self.add_input("geo", GeometryNode)

    def run(self):
        if not self.copyData():
            return

        from_class = self.get_property('From')
        to_class = self.get_property('To')

        self.update_list_text_param('Attribute Name', self.geo.getAttribNames()[from_class])
        attrib_name = self.get_property('Attribute Name')
        if not self.geo.hasAttribute(from_class, attrib_name):
            return

        new_name = self.get_property('New Attribute Name')

        if new_name == "":
            return

        if from_class == 'vertex':
            if to_class == 'face':
                self.geo.meshFuncs.VertexToFace(attrib_name, new_name)
            elif to_class == 'edge':
                self.geo.meshFuncs.VertexToEdge(attrib_name, new_name)
            elif to_class == 'vertex':
                if attrib_name != new_name:
                    self.geo.meshFuncs.attribCopy('vertex', attrib_name, new_name)
        elif from_class == 'face':
            if to_class == 'vertex':
                self.geo.meshFuncs.FaceToVertex(attrib_name, new_name)
            elif to_class == 'face':
                if attrib_name != new_name:
                    self.geo.meshFuncs.attribCopy('face', attrib_name, new_name)
        elif from_class == 'edge':
            if to_class == 'vertex':
                self.geo.meshFuncs.EdgeToVertex(attrib_name, new_name)
            elif to_class == 'edge':
                if attrib_name != new_name:
                    self.geo.meshFuncs.attribCopy('edge', attrib_name, new_name)

        if self.get_property("Delete Origin"):
            self.geo.removeAttribute(from_class, attrib_name)


class Attribute_Rename(GeometryNode):
    __identifier__ = 'Attribute'
    NODE_NAME = 'Attribute_Rename'

    def __init__(self):
        super(Attribute_Rename, self).__init__()
        self.set_parameters([{'name': 'Attribute Class', 'type': 'list', 'value': 'vertex',
                              'limits': ['vertex', 'edge', 'face', 'detail']},
                             {'name': 'Attribute Name', 'type': 'listText'},
                             {'name': 'New Attribute Name', 'type': 'str'}])
        self.add_input("geo", GeometryNode)

    def run(self):
        if not self.copyData():
            return

        attrib_class = self.get_property('Attribute Class')
        self.update_list_text_param('Attribute Name', self.geo.getAttribNames()[attrib_class])
        attrib_name = self.get_property('Attribute Name')
        if not self.geo.hasAttribute(attrib_class, attrib_name):
            return

        new_name = self.get_property('New Attribute Name')

        if new_name == "":
            return

        self.geo.renameAttribute(attrib_class, attrib_name, new_name)
