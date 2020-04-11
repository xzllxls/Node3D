from Node3D.base.node import GeometryNode
from Node3D.opengl import Mesh
from Node3D.vendor.NodeGraphQt.constants import *
import openmesh
import igl
import numpy as np
import pyassimp
import open3d as o3d

imports = ['3d', '3ds', '3mf', 'ac', 'ac3d', 'acc', 'amj', 'ase', 'ask', 'b3d',
           'blend', 'bvh', 'cms', 'cob', 'dae', 'collada', 'dxf', 'enff', 'fbx',
           'gltf', 'hmb', 'irr', 'lwo', 'lws', 'lxo', 'm3d', 'md2', 'md3', 'md5',
           'mdc', 'mdl', 'mesh', 'mot', 'ms3d', 'ndo', 'nff', 'obj', 'off', 'ogex',
           'ply', 'pmx', 'prj', 'q3o', 'q3s', 'raw', 'scn', 'sib', 'smd', 'stp',
           'stl', 'ter', 'uc', 'vta', 'x', 'x3d', 'xgl', 'zgl']

exports = ['dae ', 'collada', 'stl', 'obj', 'ply', 'x', '3ds', 'json', 'assbin',
           'step', 'gltf', '3mf', 'fbx']

import_flages = aiProcessPreset_TargetRealtime_MaxQuality = ( \
            pyassimp.postprocess.aiProcess_GenSmoothNormals | \
            pyassimp.postprocess.aiProcess_JoinIdenticalVertices | \
            pyassimp.postprocess.aiProcess_ImproveCacheLocality | \
            pyassimp.postprocess.aiProcess_LimitBoneWeights | \
            pyassimp.postprocess.aiProcess_RemoveRedundantMaterials | \
            pyassimp.postprocess.aiProcess_SplitLargeMeshes | \
            pyassimp.postprocess.aiProcess_SortByPType | \
            pyassimp.postprocess.aiProcess_FindDegenerates | \
            pyassimp.postprocess.aiProcess_FindInvalidData | \
            pyassimp.postprocess.aiProcess_FindInstances | \
            pyassimp.postprocess.aiProcess_ValidateDataStructure | \
            pyassimp.postprocess.aiProcess_OptimizeMeshes | \
            0)


class File(GeometryNode):
    __identifier__ = 'Geometry'
    NODE_NAME = 'File'

    def __init__(self):
        super(File, self).__init__()
        ext = "*." + ";*.".join(imports)
        self.add_file_input("file", "file", ext=ext)

    def load(self, filePath):
        self.geo = Mesh()
        scene = pyassimp.load(filePath, processing=import_flages)
        norms = None
        uvs = None
        for mesh in scene.meshes:
            offset = self.geo.getNumVertexes()
            self.geo.addVertices(mesh.vertices)
            for vts in mesh.faces:
                self.geo.mesh.add_face([self.geo.mesh.vertex_handle(i + offset) for i in vts if i >= 0])
            normals = mesh.normals
            if normals.shape[0] > 0:
                if norms is None:
                    norms = [normals]
                else:
                    norms.append(normals)
            elif norms is not None:
                norms.append(np.zeros((len(mesh.vertices), 3)))

            texcoords = mesh.texturecoords
            if texcoords.shape[0] > 0:
                if uvs is None:
                    uvs = [texcoords[0]]
                else:
                    uvs.append(texcoords[0])
            elif uvs is not None:
                uvs.append(np.zeros((len(mesh.vertices), 3)))

        if norms is not None:
            self.geo.setVertexAttribData('normal', np.vstack(norms), attribType='vector3', defaultValue=[0, 0, 0])
        if uvs is not None:
            self.geo.setVertexAttribData('uv', np.vstack(uvs), attribType='vector3', defaultValue=[0, 0, 0])

        pyassimp.release(scene)

    def run(self):
        file = self.get_property("file")
        self.geo = None
        if os.path.exists(file):
            self.load(file)


class Smooth(GeometryNode):
    __identifier__ = 'Geometry'
    NODE_NAME = 'Smooth'

    def __init__(self):
        super(Smooth, self).__init__()
        self.create_property(
            "Iteration", 1, widget_type=NODE_PROP_INT, range=(0, 10))

        self.add_input("geo")

    def run(self):
        if not self.copyData():
            return
        self.geo.meshFuncs.smoothMesh(self.get_property("Iteration"))


class Subdivide(GeometryNode):
    __identifier__ = 'Geometry'
    NODE_NAME = 'Subdivide'

    def __init__(self):
        super(Subdivide, self).__init__()
        self.add_combo_menu("Method", "Method", items=["Upsample", "Loop"])
        self.add_int_input("Iteration", "Iteration", 1, range=(0, 10))
        self.add_input("geo")

    def run(self):
        geo = self.get_input_geometry_ref(0)
        if geo is None:
            return

        if geo.getNumFaces() == 0 or geo.getNumVertexes() == 0:
            return
        itera = self.get_property("Iteration")
        if itera == 0:
            return

        mesh = geo.getTriangulateMesh()
        v = mesh.points()
        f = mesh.face_vertex_indices()

        mt = self.get_property("Method")
        if mt == "Upsample":
            for i in range(itera):
                v, f = igl.upsample(v, f)
        elif mt == "Loop":
            for i in range(itera):
                v, f = igl.loop(v, f)

        self.geo = Mesh()
        self.geo.addVertices(v)
        self.geo.addFaces(f)


class Collapse_Small_Triangles(GeometryNode):
    __identifier__ = 'Geometry'
    NODE_NAME = 'Collapse_Small_Triangles'

    def __init__(self):
        super(Collapse_Small_Triangles, self).__init__()
        self.add_float_input("Threshold", "Threshold", 0.01, range=(0, 1))
        self.add_input("geo")

    def run(self):
        if not self.copyData():
            return

        if self.geo.getNumFaces() == 0 or self.geo.getNumVertexes() == 0:
            return

        mesh = self.geo.getTriangulateMesh()
        v = mesh.points()
        f = mesh.face_vertex_indices()

        v, f = igl.collapse_small_triangles(v, f, 0.1)

        self.geo._mesh = openmesh.PolyMesh()
        self.geo.addVertices(v)
        self.geo.addFaces(f)


class Scatter(GeometryNode):
    __identifier__ = 'Geometry'
    NODE_NAME = 'Scatter'

    def __init__(self):
        super(Scatter, self).__init__()
        self.add_combo_menu("Method", "Method", items=['Uniform', "Relax"])
        self.add_int_input("Count", "Count", 100, range=(0, 1000))
        self.add_int_input("Relax Iteration", "Relax Iteration", 5, range=(1, 10))
        self.add_input("geo")

    def run(self):
        geo = self.get_input_geometry_ref(0)
        if geo is None:
            return

        if geo.getNumFaces() == 0 or geo.getNumVertexes() == 0:
            return
        count = self.get_property('Count')
        method = self.get_property('Method')
        iteration = self.get_property('Relax Iteration')

        tri = geo.getTriangulateMesh()
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(tri.points())
        mesh.triangles = o3d.utility.Vector3iVector(tri.face_vertex_indices())

        pcd = None
        if method == 'Uniform':
            pcd = mesh.sample_points_uniformly(count)
        elif method == 'Relax':
            pcd = mesh.sample_points_poisson_disk(count, iteration)

        self.geo = Mesh()
        self.geo.addVertices(np.array(pcd.points))
        mesh.clear()


class Clean(GeometryNode):
    __identifier__ = 'Geometry'
    NODE_NAME = 'Clean'

    def __init__(self):
        super(Clean, self).__init__()
        self.add_input("geo")
        self.create_property(
            "Remove isolated vertices", True, widget_type=NODE_PROP_QCHECKBOX)
        self.create_property(
            "Clean", False, widget_type=NODE_PROP_QCHECKBOX)

    def run(self):
        if not self.copyData():
            return

        if self.get_property("Remove isolated vertices"):
            self.geo.mesh.delete_isolated_vertices()
        if self.get_property("Clean"):
            self.geo.mesh.clean()


class Divide(GeometryNode):
    __identifier__ = 'Geometry'
    NODE_NAME = 'Divide'

    def __init__(self):
        super(Divide, self).__init__()
        self.add_input("geo")

    def run(self):
        if not self.copyData():
            return
        self.geo.mesh.triangulate()


class EdgeCusp(GeometryNode):
    __identifier__ = 'Geometry'
    NODE_NAME = 'EdgeCusp'

    def __init__(self):
        super(EdgeCusp, self).__init__()
        self.add_input("geo")

    def run(self):
        if not self.copyData():
            return

        fv = self.geo.mesh.face_vertex_indices()
        pos = self.geo.mesh.points()
        to_remove = self.geo.mesh.vertices()

        for f, vs in enumerate(fv):
            new_vhs = []
            for v in vs:
                if v < 0:
                    continue
                new_p = self.geo.mesh.add_vertex(pos[v])
                old_p = self.geo.mesh.vertex_handle(v)
                self.geo.mesh.copy_all_properties(old_p, new_p, True)
                new_vhs.append(new_p)
            new_f = self.geo.mesh.add_face(new_vhs)
            old_f = self.geo.mesh.face_handle(f)
            self.geo.mesh.copy_all_properties(old_f, new_f, True)

        for vh in to_remove:
            self.geo.mesh.delete_vertex(vh, True)

        self.geo.mesh.garbage_collection()


class Fuse(GeometryNode):
    __identifier__ = 'Geometry'
    NODE_NAME = 'Fuse'

    def __init__(self):
        super(Fuse, self).__init__()
        self.add_float_input('Snap Distance', 'Snap Distance')
        self.add_input("geo")

    def run(self):
        if not self.copyData():
            return
