from Node3D.base.node import GeometryNode
from Node3D.opengl import Mesh
import numpy as np
import open3d as o3d


class ConvexHull(GeometryNode):
    __identifier__ = 'Utility'
    NODE_NAME = 'ConvexHull'

    def __init__(self):
        super(ConvexHull, self).__init__()
        self.add_combo_menu("Generate By", "Generate By", items=['auto', 'faces', 'points'])
        self.add_input("geo")

    def run(self):
        self.geo = None
        geo = self.getInputGeometryRef(0)
        if geo is None:
            return

        if geo.getNumVertexes() == 0:
            return

        mode = self.get_property("Generate By")
        mesh = None
        pc = None

        if mode == 'auto' or mode == 'faces':
            if geo.getNumFaces() > 0:
                tri = geo.getTriangulateMesh()
                mesh = o3d.geometry.TriangleMesh()
                mesh.vertices = o3d.utility.Vector3dVector(tri.points())
                mesh.triangles = o3d.utility.Vector3iVector(tri.face_vertex_indices())
                hull, ls = mesh.compute_convex_hull()
            elif mode == 'faces':
                return
        if (mode == 'auto' and mesh is None) or mode == 'points':
            pc = o3d.geometry.PointCloud()
            pc.points = o3d.utility.Vector3dVector(geo.getVertexes())
            hull, ls = pc.compute_convex_hull()

        self.geo = Mesh()
        verts = np.array(hull.vertices)
        tri = np.array(hull.triangles)
        self.geo.addVertices(verts[tri.flatten()])
        # self.geo.addFaces(hull.triangles)
        # self.geo.addVertices(verts)
        self.geo.addFaces(np.arange(0, tri.shape[0]*3, 1).reshape(tri.shape[0], 3))

        hull.clear()
        if mesh is not None:
            mesh.clear()
        if pc is not None:
            pc.clear()
