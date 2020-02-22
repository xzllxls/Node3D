from ..vendor.pyqtgraph import opengl as gl
from .glWidget import GLViewWidget
from ..base.node.geometry_node import GeometryNode


class glScene(GLViewWidget):
    def __init__(self):
        super(glScene, self).__init__()
        self.node = None
        self.init_scene()

    def init_scene(self):
        self.grid = gl.GLGridItem()
        self.grid.scale(2, 2, 2)
        self.addItem(self.grid)

    def set_node(self, node):
        if not isinstance(node, GeometryNode):
            return
        if self.node:
            if node.id != self.node.id:
                self.node.cooked.disconnect(self.update_data)
                self.node = node
            else:
                return
        else:
            self.node = node
        self.update_data()
        self.node.cooked.connect(self.update_data)

    def update_data(self):
        self.clear_MeshItems()
        if self.node and self.node.geo:
            self.addMeshItem(self.node.geo)
        self.update()

    def evalKeyState(self):
        if len(self.keysPressed) > 0:
            pass
            #for key in self.keysPressed:
                #if key == QtCore.Qt.Key_Right:

