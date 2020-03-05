from Node3D.base.node import GeometryNode
from Node3D.vendor.NodeGraphQt.constants import *
import numpy as np
import igl


class Gaussian_Curvature(GeometryNode):
    __identifier__ = 'Calculate'
    NODE_NAME = 'Gaussian_Curvature'

    def __init__(self):
        super(Gaussian_Curvature, self).__init__()
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
        self.geo.setVertexAttribData(self.get_property("Attribute Name"), r * s, True)


class Attribute_Blur(GeometryNode):
    __identifier__ = 'Calculate'
    NODE_NAME = 'Attribute_Blur'

    def __init__(self):
        super(Attribute_Blur, self).__init__()
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


class Distance_Along_Surface(GeometryNode):
    __identifier__ = 'Calculate'
    NODE_NAME = 'Distance_Along_Surface'

    def __init__(self):
        super(Distance_Along_Surface, self).__init__()
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
        self.geo.setVertexAttribData(self.get_property("Attribute Name"), d, True)


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

        self.geo.setVertexAttribData(self.get_property("Attribute Name"), uv, True)
        if self.get_property("Show Mode") == "2d":
            self.geo.mesh.setVertexAttribData("pos", uv, True)


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

        self.geo.setVertexAttribData(self.get_property("Attribute Name"), uv, True)
        if self.get_property("Show Mode") == "2d":
            self.geo.mesh.setVertexAttribData("pos", uv, True)


class Ambient_Occlusion(GeometryNode):
    __identifier__ = 'Calculate'
    NODE_NAME = 'Ambient_Occlusion'

    def __init__(self):
        super(Ambient_Occlusion, self).__init__()
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

        self.geo.setVertexAttribData(self.get_property("Attribute Name"), ao, True)


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
            self.geo.setFaceAttribData("area", area, True)
        elif mt == "Edge Length":
            self.geo.meshFuncs.edgeLength(True)
        # elif mt == "Gradient":
        #     g = igl.grad(self.geo.getVertexes(), self.geo.getFaces())
        #     print(g)
        # self.geo.setFaceAttribData("gradient", g, True)


class Winding_Number(GeometryNode):
    __identifier__ = 'Calculate'
    NODE_NAME = 'Winding_Number'

    def __init__(self):
        super(Winding_Number, self).__init__()
        self.add_text_input("Attribute Name", "Attribute Name", "winding_number")
        self.add_input("geo")
        self.add_input("bound geo")

    def run(self):
        if not self.copyData():
            return
        g = self.getInputGeometryRef(1)
        if g is None:
            return

        if g.getNumFaces() == 0 or g.getNumVertexes() == 0:
            return

        mesh = g.getTriangulateMesh()
        v = mesh.points()
        f = mesh.face_vertex_indices()
        wn = igl.winding_number(v, f, self.geo.getVertexes())
        self.geo.setVertexAttribData(self.get_property("Attribute Name"), wn, True)
