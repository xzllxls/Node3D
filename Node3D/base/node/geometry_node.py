from .auto_node import AutoNode
from ...opengl import Mesh
from ...vendor.NodeGraphQt.base.port import Port
import copy
import gc


class GeometryNode(AutoNode):

    __identifier__ = 'OpenGL'

    def __init__(self, pre_generate=True):
        super(GeometryNode, self).__init__(defaultInputType=GeometryNode, defaultOutputType=GeometryNode)
        self._geo = None
        if pre_generate:
            self.add_output("out")
            self.create_property("out", None)

    @property
    def geo(self):
        return self._geo

    @geo.setter
    def geo(self, geo):
        if self._geo is not None:
            self._geo.clear()
            del self._geo
            gc.collect()
        self._geo = geo

    def get_port(self, port):
        if type(port) is not Port:
            return self.get_input(port)
        else:
            return port

    def get_data(self, port):
        if self.disabled():
            return self.get_input_geometry(0, True)
        return self.geo

    @staticmethod
    def copy_geo(geo):
        if geo is None:
            return None
        mesh = Mesh(copy.deepcopy(geo.mesh))
        mesh.opts = copy.deepcopy(geo.opts)
        mesh._attributeMap = copy.deepcopy(geo.attributeMap)
        return mesh

    def get_input_geometry(self, port, ref=False):
        to_port = self.get_port(port)

        if not to_port:
            return self.defaultValue

        from_ports = to_port.connected_ports()
        if not from_ports:
            return None

        for from_port in from_ports:
            geo = from_port.node().get_data(from_port)
            if ref:
                return geo
            else:
                return self.copy_geo(geo)

    def get_input_geometry_ref(self, port):
        return self.get_input_geometry(port, True)

    def get_input_node(self, port):
        to_port = self.get_port(port)
        if not to_port:
            return None

        from_ports = to_port.connected_ports()
        if not from_ports:
            return copy.deepcopy(self.defaultValue)

        for from_port in from_ports:
            return from_port.node()

    def copyData(self, index=0):
        self.geo = self.get_input_geometry(index)
        return self.geo is not None

    def set_graph(self, graph):
        super(GeometryNode, self).set_graph(graph)
        if self.get_property('Depend Time'):
            self.graph.master.timeline.frameChanged.connect(self.update_frame)

    def get_frame(self):
        return self.graph.master.timeline.getFrame()

    def get_time(self):
        return self.graph.master.timeline.getTime()

    def get_fps(self):
        return self.graph.master.timeline.fps

    def update_frame(self):
        self.cook()

    def set_depend_time(self, state):
        if not self.has_property('Depend Time'):
            self.create_property('Depend Time', state)

        if self.graph is not None:
            if state:
                self.graph.master.timeline.frameChanged.connect(self.update_frame)
            else:
                try:
                    self.graph.master.timeline.frameChanged.disconnect(self.update_frame)
                except:
                    pass
