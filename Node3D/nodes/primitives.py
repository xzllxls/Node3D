from Node3D.base.node import GeometryNode
from Node3D.opengl import Mesh
from Node3D.vendor.NodeGraphQt.constants import *
import numpy as np



class Sphere(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Sphere'

    def __init__(self):
        super(Sphere, self).__init__()
        self.add_int_input('rows', 'Rows', value=10, range=(3, 20))
        self.add_int_input('cols', 'Cols', value=10, range=(3, 20))
        self.add_float_input('radius', 'radius', value=1.0, range=(0, 20))
        self.add_checkbox("offset", "Offset")
        self.geo = Mesh()
        self.cook()

    def run(self):
        self.geo.meshFuncs.createSphere(self.get_property("rows"),
                                        self.get_property("cols"),
                                        self.get_property("radius"),
                                        self.get_property("offset"))


class Tube(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Tube'

    def __init__(self):
        super(Tube, self).__init__()
        self.add_int_input('rows', 'Rows', value=10, range=(3, 20))
        self.add_int_input('cols', 'Cols', value=10, range=(3, 20))
        self.add_float_input('length', 'length', value=2.0, range=(0, 20))
        self.add_checkbox("offset", "Offset")
        self.create_property(
            "radius", [1.0, 1.0], widget_type=NODE_PROP_VECTOR2)
        self.geo = Mesh()
        self.cook()

    def run(self):
        self.geo.meshFuncs.createCylinder(self.get_property("rows"),
                                          self.get_property("cols"),
                                          self.get_property("radius"),
                                          self.get_property("length"),
                                          self.get_property("offset"))


class Box(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Box'

    def __init__(self):
        super(Box, self).__init__()
        self.create_property("Size", value=[1, 1, 1], widget_type=NODE_PROP_VECTOR3)
        self.cook()

    def run(self):
        size = self.get_property("Size")
        x = size[0] * 0.5
        y = size[1] * 0.5
        z = size[2] * 0.5
        self.geo = Mesh()
        v1 = self.geo.addVertex([x, -y, -z])
        v2 = self.geo.addVertex([x, -y, z])
        v3 = self.geo.addVertex([x, y, z])
        v4 = self.geo.addVertex([x, y, -z])
        v5 = self.geo.addVertex([-x, -y, -z])
        v6 = self.geo.addVertex([-x, -y, z])
        v7 = self.geo.addVertex([-x, y, z])
        v8 = self.geo.addVertex([-x, y, -z])

        self.geo.addFace([v1, v2, v3, v4])
        self.geo.addFace([v2, v6, v7, v3])
        self.geo.addFace([v6, v5, v8, v7])
        self.geo.addFace([v5, v1, v4, v8])
        self.geo.addFace([v4, v3, v7, v8])
        self.geo.addFace([v5, v6, v2, v1])
        self.geo.mesh.update_normals()


class Grid(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Grid'

    def __init__(self):
        super(Grid, self).__init__()
        self.create_property("Size", value=[10, 10], widget_type=NODE_PROP_VECTOR2)
        self.create_property("Frequency", value=[10, 11], widget_type=NODE_PROP_VECTOR2)
        self.cook()

    def run(self):
        size = self.get_property("Size")
        frequency = self.get_property("Frequency")
        x = size[0] * 0.5
        z = size[1] * 0.5
        fx = int(frequency[0])
        fz = int(frequency[1])

        self.geo = Mesh()
        # vts = np.empty((fx * fz, 3), dtype=np.float64)
        # vx = np.linspace(-x, x, fx, dtype=np.float64)
        # vz = np.linspace(-z, z, fz, dtype=np.float64)
        #
        # xx, zz = np.meshgrid(vx, vz)
        # xx = xx.flatten()
        # zz = zz.flatten()
        # vts[..., 0] = xx
        # vts[..., 2] = zz
        # self.geo.addVertices(vts)
        #
        # fcs = []
        # for i in range(vts.shape[0] - fz):
        #     fcs.append([i, i + 1, i + fx, i + fx + 1])
        # self.geo.addFaces(fcs)

        v1 = self.geo.addVertex([x, 0, -z])
        v2 = self.geo.addVertex([x, 0, z])
        v3 = self.geo.addVertex([-x, 0, z])
        v4 = self.geo.addVertex([-x, 0, -z])

        self.geo.addFace([v1, v2, v3, v4])
        self.geo.mesh.update_normals()

