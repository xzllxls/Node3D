from .auto_node import AutoNode
from ...opengl import Mesh
from ...vendor.NodeGraphQt.base.port import Port
import copy


class GeometryNode(AutoNode):

    __identifier__ = 'OpenGL'

    def __init__(self, pre_generate=True):
        super(GeometryNode, self).__init__(defaultInputType=GeometryNode, defaultOutputType=GeometryNode)
        self.geo = Mesh()
        if pre_generate:
            self.add_output("out")
            self.create_property("out", None)
        # else:
        #     self.geo = None

    def get_port(self, port):
        if type(port) is int:
            return self.input(port)
        elif type(port) is str:
            return self.inputs()[port]
        elif type(port) is Port:
            return port
        else:
            return None

    def getData(self, port):
        return self.geo

    def when_disabled(self):
        self.geo = self.getInputGeometry(0, True)

    def copy_geo(self, geo):
        if geo is None:
            return None
        mesh = Mesh(copy.deepcopy(geo.mesh))
        mesh.opts = copy.deepcopy(geo.opts)
        mesh._detailAttribute = copy.deepcopy(geo.detailAttribute)
        return mesh

    def getInputGeometry(self, port, ref=False):
        to_port = self.get_port(port)

        if not to_port:
            return self.defaultValue

        from_ports = to_port.connected_ports()
        if not from_ports:
            return None

        for from_port in from_ports:
            geo = from_port.node().getData(from_port)
            if ref:
                return geo
            else:
                return self.copy_geo(geo)

    def getInputGeometryRef(self, port):
        return self.getInputGeometry(port, True)

    def getInputNode(self, port):
        to_port = self.get_port(port)
        if not to_port:
            return None

        from_ports = to_port.connected_ports()
        if not from_ports:
            return copy.deepcopy(self.defaultValue)

        for from_port in from_ports:
            return from_port.node()

    def copyData(self, index=0):
        self.geo = None
        self.geo = self.getInputGeometry(index)
        return self.geo is not None

    def set_graph(self, graph):
        super(GeometryNode, self).set_graph(graph)
        if self.get_property('Depend Time'):
            self.graph.master.timeline.frameChanged.connect(self.updateFrame)

    def getFrame(self):
        return self.graph.master.timeline.getFrame()

    def getTime(self):
        return self.graph.master.timeline.getTime()

    def getFps(self):
        return self.graph.master.timeline.fps

    def updateFrame(self):
        self.cook()

    def setDependTime(self, state):
        if not self.has_property('Depend Time'):
            self.create_property('Depend Time', state)

        if self.graph is not None:
            if state:
                self.graph.master.timeline.frameChanged.connect(self.updateFrame)
            else:
                try:
                    self.graph.master.timeline.frameChanged.disconnect(self.updateFrame)
                except:
                    pass
