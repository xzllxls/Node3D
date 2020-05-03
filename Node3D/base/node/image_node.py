from .auto_node import AutoNode
from ...vendor.NodeGraphQt.base.port import Port
from ...constants import NodeCategory
import copy


class ImageNode(AutoNode):

    __identifier__ = 'Utility'
    NODE_CATEGORY = NodeCategory.IMAGE

    def __init__(self, pre_generate=True):
        super(ImageNode, self).__init__(defaultInputType=ImageNode, defaultOutputType=ImageNode)
        self._image = None
        if pre_generate:
            self.add_output("out")
            self.create_property("out", None)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._image = image

    def get_port(self, port):
        if type(port) is not Port:
            return self.get_input(port)
        else:
            return port

    def get_data(self, port):
        if self.disabled():
            return self.get_input_image(0, True)
        return self.image

    def get_input_image(self, port, ref=False):
        to_port = self.get_port(port)

        if not to_port:
            return self.defaultValue

        from_ports = to_port.connected_ports()
        if not from_ports:
            return None

        for from_port in from_ports:
            image = from_port.node().get_data(from_port)
            if image is None:
                return None
            if ref:
                return image
            else:
                return image.copy()

    def get_input_image_ref(self, port):
        return self.get_input_image(port, True)

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
        self.image = self.get_input_image(index)
        return self.image is not None

    def set_graph(self, graph):
        super(ImageNode, self).set_graph(graph)
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
