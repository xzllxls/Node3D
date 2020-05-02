from Node3D.base.node import GeometryNode
from Node3D.opengl import Mesh, DATA_SHAPE_MAP, get_shape
from Node3D.base.data import matrix44
from Node3D.vendor.NodeGraphQt.constants import *
import numpy as np
import copy


class Point(GeometryNode):
    __identifier__ = 'OpenGL'
    NODE_NAME = 'Point'

    def __init__(self):
        super(Point, self).__init__()
        self.create_property("Color", (1.0, 1.0, 1.0), widget_type=NODE_PROP_COLORPICKER)
        self.create_property("Size", 0.1, widget_type=NODE_PROP_FLOAT)
        self.create_property("Pos", [0.0, 0.0, 0.0], widget_type=NODE_PROP_VECTOR3)
        self.cook()

    def run(self):
        self.geo = Mesh()
        self.geo.addVertex(self.get_property("Pos"))
        self.geo.createAttribute('vertex', 'color', 'vector3', [1,1,1], applyValue=True)
        self.geo.setVertexAttrib("color", 0, list(self.get_property("Color")))
        self.geo.createAttribute('vertex', 'pscale', 'float', 1.0, applyValue=True)
        self.geo.setVertexAttrib("pscale", 0, self.get_property("Size"))


class Face(GeometryNode):
    __identifier__ = 'OpenGL'
    NODE_NAME = 'Face'

    def __init__(self):
        super(Face, self).__init__()
        self.add_input("Points", multi_input=True)

    def run(self):
        self.geo = Mesh()
        geos = [port.node().get_data(port) for port in self.get_port(0).connected_ports()]
        points = []
        pscales = []
        colors = []
        for geo in geos:
            points.append(geo.getVertexAttrib('pos', 0))
            pscales.append(geo.getVertexAttrib('pscale', 0))
            colors.append(geo.getVertexAttrib('color', 0))
        self.geo.addVertices(points)
        self.geo.setVertexAttribData('color', colors, attribType='vector3', defaultValue=[1, 1, 1])
        self.geo.setVertexAttribData('pscale', pscales, attribType='float', defaultValue=1.0)
        if self.geo.getNumVertexes() > 2:
            self.geo.addFace(list(range(self.geo.getNumVertexes())))


def update_dict(a, b):
    for key, value in b.items():
        if isinstance(value, dict) and key in a.keys():
            update_dict(a[key], value)
        else:
            a[key] = copy.deepcopy(value)


class Merge(GeometryNode):
    __identifier__ = 'OpenGL'
    NODE_NAME = 'Merge'

    def __init__(self):
        super(Merge, self).__init__()
        self.set_dynamic_port(True)
        self.add_input("geo0", multi_input=True)
        self.create_property(
            "Recompute Normals", True, widget_type=NODE_PROP_QCHECKBOX)

    @staticmethod
    def createAttributeData(count, attribType, defaultValue, array_mode):
        shape = DATA_SHAPE_MAP.get(attribType, None)
        if attribType == 'list':
            shape = [0, len(defaultValue)]
        data = np.broadcast_to(defaultValue, get_shape(count, shape))
        if not array_mode:
            data = list(data)
        return data

    def run(self):
        self.geo = None
        idx = 0
        geos = []
        for port in self.input_ports():
            geo = self.get_input_geometry_ref(port)
            if geo:
                geos.append(geo)
                idx += 1
        if idx == len(self.input_ports()):
            self.add_input('geo'+str(idx))

        if len(geos) == 0:
            return
        self.geo = self.copy_geo(geos[0])
        if len(geos) == 1:
            return

        attrib_data = {}
        [update_dict(attrib_data, g.attributeMap) for g in geos]
        update_dict(self.geo.attributeMap, attrib_data)
        attrib_data['vertex'].pop('pos')

        for geo in geos:
            nv = geo.getNumVertexes()
            nf = geo.getNumFaces()
            ne = geo.getNumEdges()

            # vertex
            for v_name, v_data in attrib_data['vertex'].items():
                is_array = v_data['is_array']

                if geo.hasAttribute('vertex', v_name):
                    data = geo.getVertexAttribData(v_name)
                else:
                    data = self.createAttributeData(nv, v_data['type'], v_data['default_value'], is_array)
                if 'data' in attrib_data['vertex'][v_name].keys():
                    if is_array:
                        attrib_data['vertex'][v_name]['data'] = np.append(attrib_data['vertex'][v_name]['data'], data, axis=0)
                    else:
                        attrib_data['vertex'][v_name]['data'].extend(data)
                else:
                    attrib_data['vertex'][v_name]['data'] = data

            # face
            for f_name, f_data in attrib_data['face'].items():
                is_array = f_data['is_array']

                if geo.hasAttribute('face', f_name):
                    data = geo.getFaceAttribData(f_name)
                else:
                    data = self.createAttributeData(nf, f_data['type'], f_data['default_value'], is_array)
                if 'data' in attrib_data['face'][f_name].keys():
                    if is_array:
                        attrib_data['face'][f_name]['data'] = np.append(attrib_data['face'][f_name]['data'], data, axis=0)
                    else:
                        attrib_data['face'][f_name]['data'].extend(data)
                else:
                    attrib_data['face'][f_name]['data'] = data

            # edge
            for e_name, e_data in attrib_data['edge'].items():
                is_array = e_data['is_array']

                if geo.hasAttribute('edge', e_name):
                    data = geo.getEdgeAttribData(e_name)
                else:
                    data = self.createAttributeData(ne, e_data['type'], e_data['default_value'], is_array)
                if 'data' in attrib_data['edge'][e_name].keys():
                    if is_array:
                        attrib_data['edge'][e_name]['data'] = np.append(attrib_data['edge'][e_name]['data'], data, axis=0)
                    else:
                        attrib_data['edge'][e_name]['data'].extend(data)
                else:
                    attrib_data['edge'][e_name]['data'] = data

        for geo in geos[1:]:
            offset = self.geo.getNumVertexes()
            self.geo.addVertices(geo.getVertexes())
            [self.geo.addFace(face+offset) for face in geo.getFaces()]

        for name, data in attrib_data['vertex'].items():
            self.geo.setVertexAttribData(name, data['data'], attribType=data['type'], defaultValue=data['default_value'])
        for name, data in attrib_data['face'].items():
            self.geo.setFaceAttribData(name, data['data'], attribType=data['type'], defaultValue=data['default_value'])
        for name, data in attrib_data['edge'].items():
            self.geo.setEdgeAttribData(name, data['data'], attribType=data['type'], defaultValue=data['default_value'])

        if self.get_property("Recompute Normals"):
            self.geo.mesh.update_normals()


def moveToOrigin(node):
    in_geo = node.get_input_geometry_ref(0)
    if in_geo is not None:
        c = in_geo.bbox_center
        node.set_property("Translate", [-c[0], -c[1], -c[2]])


class Transform(GeometryNode):
    __identifier__ = 'OpenGL'
    NODE_NAME = 'Transform'

    def __init__(self):
        super(Transform, self).__init__()
        self.create_property(
            "Translate", [0.0, 0.0, 0.0], widget_type=NODE_PROP_VECTOR3)
        self.create_property(
            "Scale", [1.0, 1.0, 1.0], widget_type=NODE_PROP_VECTOR3)
        self.create_property(
            "Rotate", [0.0, 0.0, 0.0], widget_type=NODE_PROP_VECTOR3)
        self.create_property(
            "Shear", [0.0, 0.0, 0.0], widget_type=NODE_PROP_VECTOR3)
        self.create_property(
            "Uniform Scale", 1.0, widget_type=NODE_PROP_FLOAT)
        self.create_property(
            "Invert", False, widget_type=NODE_PROP_QCHECKBOX)
        self.create_property(
            "Move Centroid to Origin", None, widget_type=NODE_PROP_BUTTON, funcs=[moveToOrigin])
        self.create_property(
            "Recompute Normals", True, widget_type=NODE_PROP_QCHECKBOX)
        self.create_property(
            "Output Matrix", False, widget_type=NODE_PROP_QCHECKBOX)
        self.create_property(
            "Transform by Exist Matrix", False, widget_type=NODE_PROP_QCHECKBOX)
        self.add_input("geo", GeometryNode)

    def run(self):
        if not self.copyData():
            return

        if self.get_property("Transform by Exist Matrix"):
            mat = self.geo.getDetailAttrib("transform")
            if mat is None:
                return
        else:
            us = self.get_property("Uniform Scale")
            trans = np.array(self.get_property("Translate"))
            scale = np.array(self.get_property("Scale")) * us
            rot = np.radians(self.get_property("Rotate"))
            shear = np.radians(self.get_property("Shear"))

            mat = matrix44.create_from_compose(scale, shear, rot, trans)

        if self.get_property("Invert"):
            mat = matrix44.inverse(mat)

        self.geo.meshFuncs.transform(mat)

        if self.get_property("Output Matrix"):
            self.geo.setDetailAttrib("transform", mat, attribType='matrix4')

        if self.get_property("Recompute Normals"):
            self.geo.mesh.update_normals()


class Color(GeometryNode):
    __identifier__ = 'OpenGL'
    NODE_NAME = 'Color'

    def __init__(self):
        super(Color, self).__init__()
        self.create_property(
            "Color", (1.0, 1.0, 1.0), widget_type=NODE_PROP_COLORPICKER)
        self.create_property(
            "Random", False, widget_type=NODE_PROP_QCHECKBOX)

        self.add_input("geo", GeometryNode)

    def run(self):
        if not self.copyData():
            return
        if self.get_property("Random"):
            cols = np.random.random((self.geo.getNumVertexes(), 3))
        else:
            cols = np.ones((self.geo.getNumVertexes(), 3), dtype=np.float64)
            cols[...] = list(self.get_property("Color"))

        self.geo.setVertexAttribData("color", cols, attribType='vector3', defaultValue=[1, 1, 1])


class Visualize(GeometryNode):
    __identifier__ = 'OpenGL'
    NODE_NAME = 'Visualize'

    def __init__(self):
        super(Visualize, self).__init__()
        self.add_input("geo", GeometryNode)
        self.set_parameters([{'name': 'Attribute', 'type': 'list', 'limits': ['No Attribute']},
                             {'name': 'Flat Color', 'type': 'bool'},
                             {'name': 'Spacer', 'type': 'spacer'},
                             {'name': 'Ramp', 'type': 'group', 'children': [
                                 {'name': 'Use Ramp', 'type': 'bool'},
                                 {'name': 'Auto Normalize', 'type': 'bool'},
                                 {'name': 'Range', 'type': 'vector2', "value": [0.0, 1.0]},
                                 {'name': 'ColorRamp', 'type': 'colorRamp'}]}
                             ])

    def run(self):
        if not self.copyData():
            return

        items = ['No Attribute']
        items.extend(self.geo.getAttribNames()['vertex'])
        self.update_list_param('Attribute', items)

        attrib_name = self.get_property('Attribute')
        if not self.geo.hasAttribute('vertex', attrib_name):
            return
        try:
            data = self.geo.getVertexAttribData(attrib_name)
            if data is None:
                return
        except:
            self.error("can not vis this attribute")
            return

        shape = data.shape
        type_match = False

        d = None
        if len(shape) == 2:
            for nm in ["int", "float"]:
                if nm in type(data[0][0]).__name__:
                    type_match = True
                    break
            if not type_match:
                return
            if shape[1] >= 3:
                d = data[..., [0, 1, 2]]
                d = np.hstack([d, np.ones((shape[0], 1))])
            elif shape[1] == 2:
                d = np.hstack([data, np.zeros((shape[0], 1)), np.ones((shape[0], 1))])
            elif shape[1] == 1:
                d = np.repeat(data, 3, axis=1)
                d = np.hstack([d, np.ones((shape[0], 1))])
        elif len(shape) == 1:
            d = data.reshape(shape[0], 1)
            d = np.repeat(d, 3, axis=1)
            d = np.hstack([d, np.ones((shape[0], 1))])

        if d is not None:
            if self.get_property("Use Ramp"):
                d0 = np.average(d, axis=1)
                if self.get_property('Auto Normalize'):
                    _min = np.min(d0)
                    _max = np.max(d0)
                    d0 = (d0 - _min) / (_max - _min)
                else:
                    _range = self.get_property("Range")
                    d0 = np.clip(d0, _range[0], _range[1])
                    d0 = (d0 - _range[0]) / (_range[1] - _range[0])
                d = self.get_ramp_colors('ColorRamp', d0)
            self.geo.setVertexAttribData("color", d, attribType='vector3', defaultValue=[1, 1, 1])

        if self.get_property("Flat Color"):
            self.geo.setFlatColor(True)


class Normal(GeometryNode):
    __identifier__ = 'OpenGL'
    NODE_NAME = 'Normal'

    def __init__(self):
        super(Normal, self).__init__()
        self.set_parameters([{'name': 'Attribute Class', 'type': 'list', 'limits': ['vertex', 'face']}])

        self.add_input("geo", GeometryNode)

    def run(self):
        if not self.copyData():
            return
        attrib_class = self.get_property('Attribute Class')
        if not self.geo.hasAttribute(attrib_class, 'normal'):
            self.geo.createAttribute(attrib_class, 'normal', attribType='vector3', defaultValue=[0, 0, 0], applyValue=False)

        if attrib_class == 'vertex':
            self.geo.mesh.update_vertex_normals()
        else:
            self.geo.mesh.update_face_normals()

