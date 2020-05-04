from Node3D.base.node import SubGraphNode, PublishedNode, ImageNode
from Node3D.constants import NodeCategory


class SubGraphImage(ImageNode, SubGraphNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'SubGraphImage'
    NODE_CATEGORY = NodeCategory.NONE
    CHILDREN_CATEGORY = NodeCategory.IMAGE

    def __init__(self, dynamic_port=False):
        super(SubGraphImage, self).__init__(False)
        SubGraphNode.init_sub_graph(self, dynamic_port)

    def publish(self, file_path, node_name, node_identifier, node_class_name):
        file_path = super(SubGraphImage, self).publish(
            file_path, node_name, node_identifier, node_class_name)
        if file_path:
            self.graph.register_node(
                PublishedImage.create_node_class(file_path, PublishedImage))

    def run(self):
        SubGraphNode.run(self)

    def get_data(self, port):
        return SubGraphNode.get_data(self, port)

    @property
    def image(self):
        if self.output_ports():
            return self.get_data(self.output_ports()[0])
        return None

    def create_from_nodes(self, nodes):
        if self.parent().CHILDREN_CATEGORY != NodeCategory.IMAGE:
            self.set_property('create_from_select', False)
            return
        else:
            self.add_int_input('input count', 'input count', 0)
            self.add_int_input('output count', 'output count', 0)
            self.set_dynamic_port(True)
        SubGraphNode.create_from_nodes(self, nodes)


class PublishedImage(SubGraphImage, PublishedNode):
    __identifier__ = '__None'
    NODE_NAME = '__None'

    def __init__(self):
        PublishedImage.__init__(self, dynamic_port=False)
        self.set_property('color', (0.1412, 0.38, 0.392))
        self.set_property('published', True)
        self.created = False
        self.create_by_deserialize = False

    def set_graph(self, graph):
        PublishedImage.set_graph(self, graph)
        if not self.created:
            self.create_from_file()
            self.created = True

    def publish(self, file_path, node_name, node_identifier, node_class_name):
        if self.get_property('published'):
            return
        PublishedImage.publish(self, file_path, node_name, node_identifier, node_class_name)
