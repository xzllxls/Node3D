from Node3D.base.node import SubGraphNode, SubGraphInputNode, \
    SubGraphOutputNode, GeometryNode, PublishedNode
from Node3D.constants import NodeCategory


class SubGraph(GeometryNode, SubGraphNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'SubGraph'
    NODE_CATEGORY = NodeCategory.NONE
    CHILDREN_CATEGORY = NodeCategory.GEOMETRY

    def __init__(self, dynamic_port=True):
        super(SubGraph, self).__init__(False)
        SubGraphNode.init_sub_graph(self, dynamic_port)

    def publish(self, file_path, node_name, node_identifier, node_class_name):
        file_path = super(SubGraph, self).publish(
            file_path, node_name,node_identifier, node_class_name)
        if file_path:
            self.graph.register_node(
                PublishedGeometry.create_node_class(file_path, PublishedGeometry))

    def run(self):
        SubGraphNode.run(self)

    def get_data(self, port):
        return SubGraphNode.get_data(self, port)

    @property
    def geo(self):
        if self.output_ports():
            return self.get_data(self.output_ports()[0])
        return None


class SubGraphInput(SubGraphInputNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'SubGraphInput'

    def __init__(self):
        super(SubGraphInput, self).__init__()


class SubGraphOutput(SubGraphOutputNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'SubGraphOutput'

    def __init__(self):
        super(SubGraphOutput, self).__init__()


class PublishedGeometry(SubGraph, PublishedNode):
    __identifier__ = '__None'
    NODE_NAME = '__None'

    def __init__(self):
        SubGraph.__init__(self, dynamic_port=False)
        self.set_property('color', (0.1412, 0.38, 0.392))
        self.set_property('published', True)
        self.created = False
        self.create_by_deserialize = False

    def set_graph(self, graph):
        SubGraph.set_graph(self, graph)
        if not self.created:
            self.create_from_file()
            self.created = True

    def publish(self, file_path, node_name, node_identifier, node_class_name):
        if self.get_property('published'):
            return
        SubGraph.publish(self, file_path, node_name, node_identifier, node_class_name)


class SubGraphCalculate(SubGraphNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'SubGraphCalculate'
    NODE_CATEGORY = NodeCategory.NONE
    CHILDREN_CATEGORY = NodeCategory.CALCULATE

    def __init__(self, dynamic_port=True):
        super(SubGraphCalculate, self).__init__()
        SubGraphNode.init_sub_graph(self, dynamic_port)

    def publish(self, file_path, node_name, node_identifier, node_class_name):
        file_path = super(SubGraphCalculate, self).publish(
            file_path, node_name,node_identifier, node_class_name)
        if file_path:
            self.graph.register_node(
                PublishedCalculate.create_node_class(file_path, PublishedCalculate))


class PublishedCalculate(SubGraphCalculate, PublishedNode):
    __identifier__ = '__None'
    NODE_NAME = '__None'

    def __init__(self):
        SubGraphCalculate.__init__(self, dynamic_port=False)
        self.set_property('color', (0.1412, 0.38, 0.392))
        self.set_property('published', True)
        self.created = False
        self.create_by_deserialize = False

    def set_graph(self, graph):
        SubGraphCalculate.set_graph(self, graph)
        if not self.created:
            self.create_from_file()
            self.created = True

    def publish(self, file_path, node_name, node_identifier, node_class_name):
        if self.get_property('published'):
            return
        SubGraphCalculate.publish(self, file_path, node_name, node_identifier, node_class_name)
