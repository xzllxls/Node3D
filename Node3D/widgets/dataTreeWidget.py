from ..base.node.geometry_node import GeometryNode
from ..base.node.auto_node import AutoNode
from ..vendor import pyqtgraph as pg


class NodeDataTreeWidget(pg.DataTreeWidget):
    def __init__(self):
        super(NodeDataTreeWidget, self).__init__()
        self.node = None
        self.setAlternatingRowColors(False)

    def set_node(self, node):
        if not self.isVisible():
            if self.node:
                self.node.cooked.disconnect(self.update_date)
                self.node = None
            return

        if self.node:
            if node.id != self.node.id and isinstance(node, AutoNode):
                self.node.cooked.disconnect(self.update_date)
                self.node = node
            else:
                return
        else:
            self.node = node
        self.update_date()
        self.node.cooked.connect(self.update_date)

    def update_date(self):
        if self.node:
            if isinstance(self.node, GeometryNode):
                if self.node.geo is not None:
                    self.setData(self.node.geo.getAttribNames())
            else:
                self.setData(self.node.model.custom_properties)
