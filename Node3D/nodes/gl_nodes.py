from Node3D.base.node import GeometryNode
from Node3D.opengl import Mesh
from Node3D.base.data import matrix4x4
from Node3D.vendor.NodeGraphQt.constants import *
import numpy as np
import copy
import collections


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
        self.geo.mesh.vertex_property_array("color")
        self.geo.setVertexAttrib("color", 0, list(self.get_property("Color")))
        self.geo.mesh.vertex_property_array("pscale")
        self.geo.setVertexAttrib("pscale", 0, self.get_property("Size"))


def create_data(element_num, data, attrib_name):
    if type(data) is np.ndarray:
        shape = data.shape
        default = 0
        if len(shape) == 1:
            shape = (element_num,)
            if type(data[0]) is str:
                default = ''
            elif type(data[0]) is bool:
                default = False
        else:
            shape = list(shape)
            shape[0] = element_num
            shape = tuple(shape)

        if attrib_name == 'color':
            default = 1.0
        data = np.broadcast_to(default, shape)
        return data
    else:
        tp = type(data[0])
        try:
            default = tp('')
        except:
            default = 0.0
            if tp is int:
                default = 0
        data = [default for i in range(element_num)]
        return data


def update_dict(a, b):
    for key, value in b.items():
        if key not in a.keys() or (not isinstance(value, dict)):
            a[key] = value
        else:
            a[key].update(value)


class Merge(GeometryNode):
    __identifier__ = 'OpenGL'
    NODE_NAME = 'Merge'

    def __init__(self):
        super(Merge, self).__init__()
        self.add_input("geo1", GeometryNode)
        self.create_property(
            "Recompute Normals", True, widget_type=NODE_PROP_QCHECKBOX)
        self.index = 1

    def run(self):
        self.geo = None

        num = 0
        geos = []
        for i in range(self.index):
            geo = self.getInputGeometryRef(i)
            if geo is None:
                continue
            if geo.getNumVertexes() == 0:
                continue
            num += 1
            geos.append(geo)

        if num == self.index:
            self.index += 1
            self.add_input("geo" + str(self.index), GeometryNode)

        if len(geos) == 0:
            return
        self.geo = self.copy_geo(geos.pop(0))
        if len(geos) == 0:
            return

        geo_attribs = collections.OrderedDict()
        attrib_data = copy.deepcopy(self.geo.detailAttribute)
        for g in geos:
            geo_attribs[g] = g.getAttribNames(with_group=True)
            update_dict(attrib_data, g.detailAttribute)
        attrib_data['vertex'].pop('pos')

        a = self.geo.getNumVertexes()
        b = self.geo.getNumFaces()
        c = self.geo.getNumEdges()
        for geo, attrib in geo_attribs.items():
            m_attrib = self.geo.getAttribNames(with_group=True)

            vn = [i for i in attrib['vertex'] if i not in m_attrib['vertex']]
            for v in vn:
                data = create_data(a, geo.getVertexAttribData(v), v)
                self.geo.setVertexAttribData(v, data)

            fn = [i for i in attrib['face'] if i not in m_attrib['face']]
            for f in fn:
                data = create_data(b, geo.getFaceAttribData(f), f)
                self.geo.setFaeAttribData(f, data)

            en = [i for i in attrib['edge'] if i not in m_attrib['edge']]
            for e in en:
                data = create_data(c, geo.getEdgeAttribData(e), e)
                self.geo.setVertexAttribData(e, data)

        self.geo.detailAttribute.update(copy.deepcopy(attrib_data))
        to_remove = [i for i in attrib_data.keys() if i not in ['vertex', 'face', 'edge']]
        [attrib_data.pop(i) for i in to_remove]

        for g, attribs in geo_attribs.items():
            for vname in attrib_data['vertex'].keys():
                if vname in attribs['vertex']:
                    data = g.getVertexAttribData(vname)
                else:
                    a = g.getNumVertexes()
                    data = create_data(a, self.geo.getVertexAttribData(vname), vname)

                v = attrib_data['vertex'][vname]
                if v is None:
                    attrib_data['vertex'][vname] = self.geo.getVertexAttribData(vname)

                if type(data) is np.ndarray:
                    if len(data.shape) > 1:
                        attrib_data['vertex'][vname] = np.append(attrib_data['vertex'][vname], data, axis=0)
                    else:
                        attrib_data['vertex'][vname] = np.append(attrib_data['vertex'][vname], data)
                else:
                    attrib_data['vertex'][vname].extend(data)

            for fname in attrib_data['face'].keys():
                if fname in attribs['face']:
                    data = g.getFaceAttribData(fname)
                else:
                    a = g.getNumFaces()
                    data = create_data(a, self.geo.getFaceAttribData(fname), fname)

                v = attrib_data['face'][fname]
                if v is None:
                    attrib_data['face'][fname] = self.geo.getFaceAttribData(fname)

                if type(data) is np.ndarray:
                    if len(data.shape) > 1:
                        attrib_data['face'][fname] = np.append(attrib_data['face'][fname], data, axis=0)
                    else:
                        attrib_data['face'][fname] = np.append(attrib_data['face'][fname], data)
                else:
                    attrib_data['face'][fname].extend(data)

            for ename in attrib_data['edge'].keys():
                if ename in attribs['face']:
                    data = g.getEdgeAttribData(ename)
                else:
                    a = g.getNumFaces()
                    data = create_data(a, self.geo.getEdgeAttribData(ename), ename)

                v = attrib_data['edge'][ename]
                if v is None:
                    attrib_data['edge'][ename] = self.geo.getEdgeAttribData(ename)

                if type(data) is np.ndarray:
                    if len(data.shape) > 1:
                        attrib_data['edge'][ename] = np.append(attrib_data['edge'][ename], data, axis=0)
                    else:
                        attrib_data['edge'][ename] = np.append(attrib_data['edge'][ename], data)
                else:
                    attrib_data['edge'][ename].extend(data)

        for g in geo_attribs.keys():
            offset = self.geo.getNumVertexes()
            self.geo.addVertices(g.getVertexes())
            self.geo.addFaces(g.getFaces() + offset)

        for l, attribs in attrib_data.items():
            for name, data in attribs.items():
                if type(data) is np.ndarray:
                    if len(data.shape) == 1:
                        data = data.reshape(data.shape[0], 1)
                if l == 'vertex':
                    self.geo.setVertexAttribData(name, data)
                elif l == 'face':
                    self.geo.setFaceAttribData(name, data)
                elif l == 'edge':
                    self.geo.setEdgeAttribData(name, data)

        if self.get_property("Recompute Normals"):
            self.geo.mesh.update_normals()


def moveToOrigin(node):
    in_geo = node.getInputGeometryRef(0)
    if in_geo is not None:
        c = in_geo.bbox_center
        node.set_property("Translate", [-c[0], -c[1], -c[2]])


class Transfrom(GeometryNode):
    __identifier__ = 'OpenGL'
    NODE_NAME = 'Transfrom'

    def __init__(self):
        super(Transfrom, self).__init__()
        self.create_property(
            "Translate", [0.0, 0.0, 0.0], widget_type=NODE_PROP_VECTOR3)
        self.create_property(
            "Scale", [1.0, 1.0, 1.0], widget_type=NODE_PROP_VECTOR3)
        self.create_property(
            "Rotate", [0.0, 0.0, 0.0], widget_type=NODE_PROP_VECTOR3)
        self.create_property(
            "Shear", [0.0, 0.0, 0.0], widget_type=NODE_PROP_VECTOR3)
        self.create_property(
            "Unifrom Scale", 1.0, widget_type=NODE_PROP_FLOAT)
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
            us = self.get_property("Unifrom Scale")
            trans = np.array(self.get_property("Translate"))
            scale = np.array(self.get_property("Scale")) * us
            rot = np.radians(self.get_property("Rotate"))
            shear = np.radians(self.get_property("Shear"))

            mat = matrix4x4.from_compose(scale, shear, rot, trans)

        if self.get_property("Invert"):
            mat.invert()

        self.geo.meshFuncs.transformVertex(mat.data())

        if self.get_property("Output Matrix"):
            self.geo.setDetailAttrib("transform", mat)

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
            cd = list(self.get_property("Color"))
            cols[...] = cd

        self.geo.setVertexAttribData("color", cols, True)


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
        self.update_combo_menu('Attribute', items)

        try:
            data = self.geo.getVertexAttribData(self.get_property('Attribute'), True)
            if data is None:
                return
        except:
            self.error("can not vis this attribute")
            return

        shape = data.shape
        typematch = False

        d = None
        if len(shape) == 2:
            for nm in ["int", "float"]:
                if nm in type(data[0][0]).__name__:
                    typematch = True
                    break
            if not typematch:
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
            self.geo.setVertexAttribData("color", d, True)

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
        if attrib_class == 'vertex':
            self.geo.mesh.update_vertex_normals()
        else:
            self.geo.mesh.update_face_normals()
