from Node3D.base.node import GeometryNode
from Node3D.opengl import Mesh
from Node3D.vendor.NodeGraphQt.constants import *
import numpy as np
from Node3D.base.mesh.base_primitives import generate_tube, generate_sphere, \
    generate_cylinder, generate_cone, generate_torus
import open3d as o3d


class Tube(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Tube'

    def __init__(self):
        super(Tube, self).__init__()
        params = [{'name': 'Bottom center', 'type': 'vector3', 'value': [0, 0, 0]},
                  {'name': 'Top center', 'type': 'vector3', 'value': [0, 1, 0]},
                  {'name': 'Outer radius', 'type': 'vector2', 'value': [0.5, 0.5]},
                  {'name': 'Inner radius', 'type': 'vector2', 'value': [0.3, 0.3]},
                  {'name': 'Segments', 'type': 'int', 'value': 10, 'limits': (3, 30)},
                  {'name': 'Quad', 'type': 'bool', 'value': True}]
        self.set_parameters(params)

        self.cook()

    def run(self):
        outer = self.get_property("Outer radius")
        inner = self.get_property("Inner radius")
        s = self.get_property("Segments")
        if s < 3:
            self.geo = None
            return
        vertices, faces = generate_tube(self.get_property("Bottom center"), self.get_property("Top center"),
                                        outer[0], outer[1], inner[0], inner[1], s,
                                        self.get_property("Quad"))
        self.geo = Mesh()
        self.geo.addVertices(vertices)
        self.geo.addFaces(faces)


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
        params = [{'name': 'Size', 'type': 'vector2', 'value': [10, 10]},
                  {'name': 'Resolution', 'type': 'vector2i', 'value': [10, 10]}]
        self.set_parameters(params)
        self.cook()

    def run(self):
        size = self.get_property("Size")
        resolution = self.get_property("Resolution")
        x = size[0] * 0.5
        z = size[1] * 0.5
        fx = resolution[0]
        fz = resolution[1]

        if fx < 2 or fz < 2:
            self.geo = None
            return

        x_range = np.linspace(-x, x, fx)
        z_range = np.linspace(-z, z, fz)
        vertices = np.dstack(np.meshgrid(x_range, z_range, np.array([0.0]))).reshape(-1, 3)
        a = np.add.outer(np.array(range(fx - 1)), fx * np.array(range(fz - 1)))
        faces = np.dstack([a, a + 1, a + fx + 1, a + fx]).reshape(-1, 4)

        nms = np.zeros((vertices.shape[0], 3), dtype=float)
        nms[..., 1] = 1
        self.geo = Mesh()
        self.geo.addVertices(vertices[:, [0, 2, 1]])
        self.geo.addFaces(faces)
        self.geo.setVertexAttribData('normal', nms, attribType='vector3', defaultValue=[0, 0, 0])


class Arrow(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Arrow'

    def __init__(self):
        super(Arrow, self).__init__()
        params = [{'name': 'Radius', 'type': 'vector2', 'value': [1, 1.5]},
                  {'name': 'Height', 'type': 'vector2', 'value': [2, 4]},
                  {'name': 'Cylinder split', 'type': 'int', 'value': 1, 'limits': (1, 10)},
                  {'name': 'Cone split', 'type': 'int', 'value': 1, 'limits': (1, 10)},
                  {'name': 'Resolution', 'type': 'int', 'value': 20, 'limits': (3, 30)}]
        self.set_parameters(params)

        self.cook()

    def run(self):
        radius = self.get_property("Radius")
        height = self.get_property("Height")

        tri = o3d.geometry.TriangleMesh.create_arrow(radius[0], radius[1], height[0], height[1],
                                                     self.get_property("Resolution"),
                                                     self.get_property("Cylinder split"),
                                                     self.get_property("Cone split"))

        self.geo = Mesh()
        self.geo.addVertices(np.array(tri.vertices)[:, [0, 2, 1]])
        self.geo.addFaces(np.array(tri.triangles))


class Cone(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Cone'

    def __init__(self):
        super(Cone, self).__init__()
        params = [{'name': 'Radius', 'type': 'float', 'value': 1.0},
                  {'name': 'Height', 'type': 'float', 'value': 2.0},
                  {'name': 'Split', 'type': 'int', 'value': 1, 'limits': (1, 10)},
                  {'name': 'Resolution', 'type': 'int', 'value': 20, 'limits': (3, 30)},
                  {'name': 'Cap', 'type': 'bool', 'value': True}]
        self.set_parameters(params)

        self.cook()

    def run(self):
        s = self.get_property("Resolution")
        if s < 3:
            self.geo = None
            return

        tri, quad, vt = generate_cone(self.get_property("Radius"),
                                      self.get_property("Height"),
                                      s,
                                      self.get_property("Split"))

        self.geo = Mesh()
        self.geo.addVertices(vt)
        self.geo.addFaces(quad)
        self.geo.addFaces(tri)
        if not self.get_property("Cap"):
            self.geo.removeVertex(0, True)


class CoordinateFrame(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Coordinate Frame'

    def __init__(self):
        super(CoordinateFrame, self).__init__()
        params = [{'name': 'Size', 'type': 'float', 'value': 1.0},
                  {'name': 'Origin', 'type': 'vector3', 'value': [0, 0, 0]}]
        self.set_parameters(params)

        self.cook()

    def run(self):
        size = self.get_property("Size")
        if size == 0:
            size = 0.0001
        tri = o3d.geometry.TriangleMesh.create_coordinate_frame(size, self.get_property("Origin"))

        self.geo = Mesh()
        self.geo.addVertices(np.array(tri.vertices)[:, [0, 2, 1]])
        self.geo.addFaces(np.array(tri.triangles))


class Cylinder(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Cylinder'

    def __init__(self):
        super(Cylinder, self).__init__()
        params = [{'name': 'Radius', 'type': 'float', 'value': 1.0},
                  {'name': 'Height', 'type': 'float', 'value': 2.0},
                  {'name': 'Split', 'type': 'int', 'value': 4, 'limits': (1, 10)},
                  {'name': 'Resolution', 'type': 'int', 'value': 20, 'limits': (3, 30)},
                  {'name': 'Cap', 'type': 'bool', 'value': True}]
        self.set_parameters(params)

        self.cook()

    def run(self):
        s = self.get_property("Resolution")
        if s < 3:
            self.geo = None
            return

        tri, quad, vt = generate_cylinder(self.get_property("Radius"),
                                          self.get_property("Height"),
                                          s,
                                          self.get_property("Split"))

        self.geo = Mesh()
        self.geo.addVertices(vt)
        self.geo.addFaces(quad)
        if self.get_property("Cap"):
            self.geo.addFaces(tri)
        else:
            self.geo.removeVertices([0, 1])


class Icosahedron(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Icosahedron'

    def __init__(self):
        super(Icosahedron, self).__init__()
        params = [{'name': 'Radius', 'type': 'float', 'value': 1.0}]
        self.set_parameters(params)

        self.cook()

    def run(self):
        rad = self.get_property("Radius")
        if rad == 0:
            rad = 0.0001

        tri = o3d.geometry.TriangleMesh.create_icosahedron(rad)

        self.geo = Mesh()
        self.geo.addVertices(np.array(tri.vertices)[:, [0, 2, 1]])
        self.geo.addFaces(np.array(tri.triangles))


class Moebius(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Moebius'

    def __init__(self):
        super(Moebius, self).__init__()
        params = [{'name': 'Length Split', 'type': 'int', 'value': 70, 'limits': (1, 100)},
                  {'name': 'Width Split', 'type': 'int', 'value': 15, 'limits': (1, 100)},
                  {'name': 'Twists', 'type': 'int', 'value': 1, 'limits': (0, 10)},
                  {'name': 'Raidus', 'type': 'float', 'value': 1, 'limits': (0, 10)},
                  {'name': 'Flatness', 'type': 'float', 'value': 1, 'limits': (0, 30)},
                  {'name': 'Width', 'type': 'float', 'value': 1, 'limits': (0, 10)},
                  {'name': 'Scale', 'type': 'float', 'value': 1, 'limits': (0, 30)}]

        self.set_parameters(params)

        self.cook()

    def run(self):
        tri = o3d.geometry.TriangleMesh.create_moebius(self.get_property('Length Split'),
                                                       self.get_property('Width Split'),
                                                       self.get_property("Twists"),
                                                       self.get_property("Raidus"),
                                                       self.get_property("Flatness"),
                                                       self.get_property("Width"),
                                                       self.get_property("Scale"))

        self.geo = Mesh()
        self.geo.addVertices(np.array(tri.vertices)[:, [0, 2, 1]])
        self.geo.addFaces(np.array(tri.triangles))


class Octahedron(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Octahedron'

    def __init__(self):
        super(Octahedron, self).__init__()
        params = [{'name': 'Radius', 'type': 'float', 'value': 1.0}]
        self.set_parameters(params)

        self.cook()

    def run(self):
        rad = self.get_property("Radius")
        if rad == 0:
            rad = 0.0001

        tri = o3d.geometry.TriangleMesh.create_octahedron(rad)

        self.geo = Mesh()
        self.geo.addVertices(np.array(tri.vertices)[:, [0, 2, 1]])
        self.geo.addFaces(np.array(tri.triangles))


class Sphere(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Sphere'

    def __init__(self):
        super(Sphere, self).__init__()
        params = [{'name': 'Radius', 'type': 'float', 'value': 1.0},
                  {'name': 'Resolution', 'type': 'int', 'value': 20, 'limits': (2, 50)}]
        self.set_parameters(params)

        self.cook()

    def run(self):
        rad = self.get_property("Radius")
        if rad == 0:
            rad = 0.0001

        s = self.get_property("Resolution")
        if s < 2:
            self.geo = None
            return

        tri, quad, vt = generate_sphere(rad, s)
        self.geo = Mesh()
        self.geo.addVertices(vt)
        self.geo.addFaces(tri)
        self.geo.addFaces(quad)


class Tetrahedron(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Tetrahedron'

    def __init__(self):
        super(Tetrahedron, self).__init__()
        params = [{'name': 'Radius', 'type': 'float', 'value': 1.0}]
        self.set_parameters(params)

        self.cook()

    def run(self):
        rad = self.get_property("Radius")
        if rad == 0:
            rad = 0.0001

        tri = o3d.geometry.TriangleMesh.create_tetrahedron(rad)

        self.geo = Mesh()
        self.geo.addVertices(np.array(tri.vertices)[:, [0, 2, 1]])
        self.geo.addFaces(np.array(tri.triangles))


class Torus(GeometryNode):
    __identifier__ = 'Primitives'
    NODE_NAME = 'Torus'

    def __init__(self):
        super(Torus, self).__init__()
        params = [{'name': 'Radius', 'type': 'vector2', 'value': [1, 0.5]},
                  {'name': 'Radial resolution', 'type': 'int', 'value': 20, 'limits': (3, 50)},
                  {'name': 'Tubular resolution', 'type': 'int', 'value': 20, 'limits': (3, 50)}]
        self.set_parameters(params)

        self.cook()

    def run(self):
        rad = self.get_property("Radius")
        if rad[0] == 0:
            rad[0] = 0.0001
        if rad[1] == 0:
            rad[1] = 0.0001

        r1 = self.get_property("Radial resolution")
        r2 = self.get_property("Tubular resolution")
        if r1 < 3 or r2 < 3:
            self.geo = None
            return
        faces, vertices = generate_torus(rad[0], rad[1], r1, r2)
        self.geo = Mesh()
        self.geo.addVertices(vertices)
        self.geo.addFaces(faces)


if __name__ == '__main__':
    vertices, faces = generate_tube([0, 0, 0], [0, 1, 0],
                                    2, 2, 1, 1, 5,
                                    True)
    print(vertices)
