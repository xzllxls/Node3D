from Node3D.base.node import GeometryNode
from .geometry_nodes import File
import os


class Toy(File):
    __identifier__ = 'Test Geometry'
    NODE_NAME = 'Toy'

    def __init__(self, filePath=None):
        GeometryNode.__init__(self)
        if filePath:
            self.filePath = filePath
        else:
            self.filePath = "test_geos/Toy.obj"
        self.cook()

    def run(self):
        self.geo = None
        if os.path.exists(self.filePath):
            self.load(self.filePath)


class Pig(Toy):
    __identifier__ = 'Test Geometry'
    NODE_NAME = 'Pig'

    def __init__(self):
        super().__init__("test_geos/Pig.obj")


class Squab(Toy):
    __identifier__ = 'Test Geometry'
    NODE_NAME = 'Squab'

    def __init__(self):
        super().__init__("test_geos/Squab.fbx")


class Armadillo(Toy):
    __identifier__ = 'Test Geometry'
    NODE_NAME = 'Armadillo'

    def __init__(self):
        super().__init__("test_geos/Armadillo.obj")


class Bunny(Toy):
    __identifier__ = 'Test Geometry'
    NODE_NAME = 'Bunny'

    def __init__(self):
        super().__init__("test_geos/Bunny.obj")


class Knot(Toy):
    __identifier__ = 'Test Geometry'
    NODE_NAME = 'Knot'

    def __init__(self):
        super().__init__("test_geos/Knot.obj")



class Nano(Toy):
    __identifier__ = 'Test Geometry'
    NODE_NAME = 'Nano'

    def __init__(self):
        super().__init__("test_geos/scene.gltf")
