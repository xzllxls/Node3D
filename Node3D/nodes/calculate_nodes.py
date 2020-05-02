from Node3D.base.node import GeometryNode
from Node3D.vendor.NodeGraphQt.constants import *
from scipy.spatial import ckdtree
import numpy as np
import igl


class GaussianCurvature(GeometryNode):
    __identifier__ = 'Calculate'
    NODE_NAME = 'Gaussian_Curvature'

    def __init__(self):
        super(GaussianCurvature, self).__init__()
        self.add_text_input("Attribute Name", "Attribute Name", "curvature")
        self.add_float_input("Scale", "Scale", 1.0)
        self.add_input("geo")

    def run(self):
        if not self.copyData():
            return

        if self.geo.getNumFaces() == 0 or self.geo.getNumVertexes() == 0:
            return

        mesh = self.geo.getTriangulateMesh()
        r = igl.gaussian_curvature(mesh.points(), mesh.face_vertex_indices())
        s = self.get_property("Scale")
        self.geo.setVertexAttribData(self.get_property("Attribute Name"), r * s, attribType='float', defaultValue=0.0)


class AttributeBlur(GeometryNode):
    __identifier__ = 'Calculate'
    NODE_NAME = 'Attribute_Blur'

    def __init__(self):
        super(AttributeBlur, self).__init__()
        self.add_combo_menu('Attribute', 'Attribute', items= ['No Attribute'])
        self.create_property(
            "Iteration", 1, widget_type=NODE_PROP_INT, range=(0, 10))

        self.add_input("geo")

    def run(self):
        if not self.copyData():
            return

        items = ['No Attribute']
        items.extend(self.geo.getAttribNames()['vertex'])
        self.update_list_param('Attribute', items)

        name = self.get_property('Attribute')
        try:
            if not self.geo.hasAttribute("vertex", name):
                return
        except:
            self.error("can not blur this attribute")
            return

        self.geo.meshFuncs.smoothVertexAttrib(name, self.get_property("Iteration"))


class DistanceAlongSurface(GeometryNode):
    __identifier__ = 'Calculate'
    NODE_NAME = 'Distance_Along_Surface'

    def __init__(self):
        super(DistanceAlongSurface, self).__init__()
        self.add_text_input("Attribute Name", "Attribute Name", "distance")
        self.add_int_input("Start Point", "Start Point", 0, range=(0, 100))
        self.add_checkbox("Normalize", "Normalize", state=False)
        self.add_input("geo")

    def run(self):
        if not self.copyData():
            return

        if self.geo.getNumFaces() == 0 or self.geo.getNumVertexes() == 0:
            return
        start_index = self.get_property("Start Point")
        if start_index >= self.geo.getNumVertexes():
            return

        mesh = self.geo.getTriangulateMesh()
        v = mesh.points()
        f = mesh.face_vertex_indices()

        vs = np.array([start_index])
        vt = np.arange(v.shape[0])
        d = igl.exact_geodesic(v, f, vs, vt)

        if self.get_property("Normalize"):
            d /= np.max(d)
        self.geo.setVertexAttribData(self.get_property("Attribute Name"), d, attribType='float', defaultValue=0.0)


class Harmonic(GeometryNode):
    __identifier__ = 'uv'
    NODE_NAME = 'Harmonic'

    def __init__(self):
        super(Harmonic, self).__init__()
        self.add_text_input("Attribute Name", "Attribute Name", "uv")
        self.add_combo_menu("Show Mode", "Show Mode", items=["3D", "2D"])
        self.add_input("geo")

    def run(self):
        if not self.copyData():
            return

        if self.geo.getNumFaces() == 0 or self.geo.getNumVertexes() == 0:
            return
        mesh = self.geo.getTriangulateMesh()
        v = mesh.points()
        f = mesh.face_vertex_indices()

        bnd = igl.boundary_loop(f)
        bnd_uv = igl.map_vertices_to_circle(v, bnd)

        uv = igl.harmonic_weights(v, f, bnd, bnd_uv, 1)
        uv = np.hstack([uv, np.zeros((uv.shape[0], 1))])

        self.geo.setVertexAttribData(self.get_property("Attribute Name"), uv, attribType='vector3', defaultValue=[0, 0, 0])
        if self.get_property("Show Mode") == "2d":
            self.geo.mesh.setVertexAttribData("pos", uv)


class ARAP(GeometryNode):
    __identifier__ = 'uv'
    NODE_NAME = 'ARAP'

    def __init__(self):
        super(ARAP, self).__init__()
        self.add_text_input("Attribute Name", "Attribute Name", "uv")
        self.add_combo_menu("Show Mode", "Show Mode", items=["3D", "2D"])
        self.add_input("geo")

    def run(self):
        if not self.copyData():
            return

        if self.geo.getNumFaces() == 0 or self.geo.getNumVertexes() == 0:
            return

        mesh = self.geo.getTriangulateMesh()
        v = mesh.points()
        f = mesh.face_vertex_indices()

        # Find the open boundary
        bnd = igl.boundary_loop(f)

        # Map the boundary to a circle, preserving edge proportions
        bnd_uv = igl.map_vertices_to_circle(v, bnd)

        # Harmonic parametrization for the internal vertices
        uv = igl.harmonic_weights(v, f, bnd, bnd_uv, 1)

        arap = igl.ARAP(v, f, 2, np.zeros((0)))
        uv = arap.solve(np.zeros((0, 0)), uv)

        self.geo.setVertexAttribData(self.get_property("Attribute Name"), uv, attribType='vector3', defaultValue=[0, 0, 0])
        if self.get_property("Show Mode") == "2d":
            self.geo.mesh.setVertexAttribData("pos", uv)


class AmbientOcclusion(GeometryNode):
    __identifier__ = 'Calculate'
    NODE_NAME = 'Ambient_Occlusion'

    def __init__(self):
        super(AmbientOcclusion, self).__init__()
        self.add_text_input("Attribute Name", "Attribute Name", "ao")
        self.add_int_input("Angle", "Angle", 50, range=(0, 180))
        self.add_input("geo")

    def run(self):
        if not self.copyData():
            return

        if self.geo.getNumFaces() == 0 or self.geo.getNumVertexes() == 0:
            return

        mesh = self.geo.getTriangulateMesh()
        mesh.update_vertex_normals()

        v = mesh.points()
        f = mesh.face_vertex_indices()
        n = mesh.vertex_normals()

        # Compute ambient occlusion factor using embree
        ao = igl.ambient_occlusion(v, f, v, n, self.get_property("Angle"))
        ao = 1.0 - ao

        self.geo.setVertexAttribData(self.get_property("Attribute Name"), ao, attribType='float', defaultValue=0.0)


class Measure(GeometryNode):
    __identifier__ = 'Calculate'
    NODE_NAME = 'Measure'

    def __init__(self):
        super(Measure, self).__init__()
        # self.add_text_input("Attribute Name","Attribute Name", "area")
        self.add_combo_menu("Method", "Method", items=["Area", "FaceCent", "Edge Length"])
        self.add_input("geo")

    def run(self):
        if not self.copyData():
            return

        if self.geo.getNumFaces() == 0 or self.geo.getNumVertexes() == 0:
            return

        mt = self.get_property("Method")
        if mt == "FaceCent":
            self.geo.meshFuncs.facePos(True)
        elif mt == "Area":
            area = igl.doublearea(self.geo.getVertexes(), self.geo.mesh.face_vertex_indices()) / 2.0
            self.geo.setFaceAttribData("area", area, attribType='float', defaultValue=0.0)
        elif mt == "Edge Length":
            self.geo.meshFuncs.edgeLength(True)
        # elif mt == "Gradient":
        #     g = igl.grad(self.geo.getVertexes(), self.geo.getFaces())
        #     print(g)
        # self.geo.setFaceAttribData("gradient", g, attribType='float', defaultValue=0.0)


class WindingNumber(GeometryNode):
    __identifier__ = 'Calculate'
    NODE_NAME = 'Winding_Number'

    def __init__(self):
        super(WindingNumber, self).__init__()
        self.add_text_input("Attribute Name", "Attribute Name", "winding_number")
        self.add_input("geo")
        self.add_input("bound geo")

    def run(self):
        if not self.copyData():
            return
        g = self.get_input_geometry_ref(1)
        if g is None:
            return

        if g.getNumFaces() == 0 or g.getNumVertexes() == 0:
            return

        mesh = g.getTriangulateMesh()
        v = mesh.points()
        f = mesh.face_vertex_indices()
        wn = igl.winding_number(v, f, self.geo.getVertexes())
        self.geo.setVertexAttribData(self.get_property("Attribute Name"), wn, attribType='float', defaultValue=0.0)


class Kdtree(GeometryNode):
    __identifier__ = 'Calculate'
    NODE_NAME = 'Kdtree'

    def __init__(self):
        super(Kdtree, self).__init__()
        self.add_input("geo")
        self.set_parameters([{'name': 'Group Name', 'type': 'str', 'value': 'searched'},
                             {'name': 'Distance Name', 'type': 'str', 'value': 'distance'},
                             {'name': 'Search Radius', 'type': 'float', 'value': 1.0},
                             {'name': 'Search Count', 'type': 'int', 'value': 100000},
                             {'name': 'Search Position', 'type': 'vector3', 'value': [0, 1, 0]}])

    def run(self):
        if not self.copyData():
            return

        group_name = self.get_property('Group Name')
        distance_name = self.get_property('Distance Name')
        if not group_name or not distance_name:
            return

        search_position = self.get_property('Search Position')
        max_count = self.get_property('Search Count')
        max_dist = self.get_property('Search Radius')
        if max_dist <= 0:
            max_dist = None
        points = self.geo.getVertexes()
        tree = ckdtree.cKDTree(points)
        dist, idx = tree.query(search_position, max_count, distance_upper_bound=max_dist)
        if len(idx) == 0:
            return
        npoints = self.geo.getNumVertexes()
        self.geo.createGroup('vertex', group_name)
        self.geo.createAttribute('vertex', distance_name, "float", -1.0, True)
        if not self.geo.hasAttribute('vertex', 'color'):
            self.geo.createAttribute('vertex', 'color', "vector3", [1.0, 1.0, 1.0], True)

        for i, d in zip(idx, dist):
            if i >= npoints:
                continue

            self.geo.setVertexAttrib(distance_name, i, d)
            self.geo.setGroup('vertex', group_name, i, True)
            self.geo.setVertexAttrib("color", i, [1.0, 0, 0])

