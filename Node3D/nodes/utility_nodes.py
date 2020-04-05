from Node3D.base.node import GeometryNode
from Node3D.opengl import Mesh
from CGAL.CGAL_Kernel import Point_3
from CGAL import CGAL_Convex_hull_3
from CGAL.CGAL_Polyhedron_3 import Polyhedron_3


class ConvexHull(GeometryNode):
    __identifier__ = 'Utility'
    NODE_NAME = 'ConvexHull'

    def __init__(self):
        super(ConvexHull, self).__init__()
        self.add_input("geo")

    def run(self):
        self.geo = None
        geo = self.getInputGeometryRef(0)
        if geo is None:
            return

        if geo.getNumVertexes() == 0:
            return

        pts = [Point_3(*i) for i in geo.getVertexes()]

        res = Polyhedron_3()
        CGAL_Convex_hull_3.convex_hull_3(pts, res)
        pts = {}
        [pts.update({v: idx}) for idx, v in enumerate(res.vertices())]

        ff = []
        for f in res.facets():
            he = f.halfedge()
            done = he
            faces = []
            while True:
                faces.append(pts[he.vertex()])
                he = he.next()
                if he == done:
                    break

            ff.append(faces)

        self.geo = Mesh()
        self.geo.addVertices([[i.x(), i.y(), i.z()] for i in res.points()])
        self.geo.addFaces(ff)
