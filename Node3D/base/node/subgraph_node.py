from .auto_node import AutoNode
from ...vendor.NodeGraphQt import SubGraph, topological_sort_by_down, BackdropNode
import json, os
from .utils import update_node_down_stream
from ...constants import NodeCategory


class SubGraphNode(AutoNode, SubGraph):
    """
    sub graph node.
    """
    NODE_CATEGORY = NodeCategory.NONE
    CHILDREN_CATEGORY = NodeCategory.NONE

    def __init__(self, defaultInputType=None, defaultOutputType=None, dynamic_port=True):
        super(SubGraphNode, self).__init__(defaultInputType, defaultOutputType)
        self._inited = False
        # self.init_sub_graph(dynamic_port)

    def init_sub_graph(self, dynamic_port):
        if self._inited:
            return
        SubGraph.__init__(self)
        self.set_property('color', (0.498, 0.212, 0.3647))
        self.sub_graph_input_nodes = []
        self.sub_graph_output_nodes = []
        self.create_property('graph_rect', None)
        self.create_property('published', False)
        self.set_dynamic_port(dynamic_port)

        if dynamic_port:
            self.add_int_input('input count', 'input count', 0)
            self.add_int_input('output count', 'output count', 0)
        else:
            self.create_property('input count', 0)
            self.create_property('output count', 0)
        self._marked_ports = []
        self.create_property('create_from_select', True)
        self._inited = True

    def mark_node_to_be_cooked(self, port):
        """
        Mark port corresponding SubGraphInputNode to be cooked.

        Args:
            port(Port)
        """

        if port not in self._marked_ports and port in self.input_ports():
            self._marked_ports.append(port)

    def is_editable(self):
        """
        Returns whether the node is allowed edit.
        """

        parent = self.parent()
        if parent is None:
            return not self.get_property('published')

        if not self.get_property('published') and self.parent().is_editable():
            return True
        return False

    def enter(self):
        """
        Action when enter the sub graph.
        """

        self.hide()
        [n.show() for n in self.children()]
        rect = self.get_property('graph_rect')
        if rect:
            self.graph.set_graph_rect(rect)

    def exit(self):
        """
        Action when exit the sub graph.
        """

        for n in self.children():
            n.hide()
            n.set_selected(False)
        self.model.set_property('graph_rect', self.graph.graph_rect())

    def show(self):
        AutoNode.show(self)
        self.update_port()

    def update_port(self):
        """
        Re layout the node port.
        """

        self.view.draw_node()

    def add_child(self, node):
        """
        Add node the the sub graph.

        Args:
            node(AutoNode).
        """

        self._children.add(node)
        node._parent = self

        if self.has_property('root'):
            return

        if isinstance(node, SubGraphInputNode):
            if node not in self.sub_graph_input_nodes:
                self.sub_graph_input_nodes.append(node)

        if isinstance(node, SubGraphOutputNode):
            if node not in self.sub_graph_output_nodes:
                self.sub_graph_output_nodes.append(node)

    def remove_child(self, node):
        """
        Remove node from the sub graph.

        Args:
            node(AutoNode).
        """

        if node in self._children:
            self._children.remove(node)

        if self.has_property('root'):
            return
        if isinstance(node, SubGraphInputNode):
            if node in self.sub_graph_input_nodes:
                self.sub_graph_input_nodes.remove(node)
        if isinstance(node, SubGraphOutputNode):
            if node in self.sub_graph_output_nodes:
                self.sub_graph_output_nodes.remove(node)

    def get_input_data_ref(self):
        """
        Returns the data of the first input port connected node.
        """
        to_port = self.get_input(0)

        if not to_port:
            return self.defaultValue

        from_ports = to_port.connected_ports()
        if not from_ports:
            return None
        return from_ports[0].node().get_data(from_ports[0])

    def get_data(self, port):
        if self.disabled():
            return self.get_input_data_ref()
        if port is None:
            return None
        index = int(port.name()[-1])
        for node in self.sub_graph_output_nodes:
            if node.get_property('output index') == index:
                return node.get_data(None)
        self.error('can\'t find matched index output node !!!')
        return self.defaultValue

    def run(self):
        self.update_ports()

        for node in self.sub_graph_input_nodes:
            node._parent = self

        start_nodes = []
        if self._marked_ports:
            for port in self._marked_ports:
                index = self.input_ports().index(port)
                for node in self.sub_graph_input_nodes:
                    if node.get_property('input index') == index:
                        start_nodes.append(node)
            self._marked_ports = []
        else:
            start_nodes = self.sub_graph_input_nodes

        nodes = topological_sort_by_down(start_nodes=start_nodes)

        for node in nodes:
            if node.disabled():
                continue
            node.cook()
            if node.has_error():
                self.error("{} : {}".format(node.name(), node._message))
                break

    def delete(self):
        """
        Action when the node is deleted from the NodeGraphQt.NodeGraph.
        """

        self._view.delete()
        for child in self._children:
            child._parent = None

        if self._parent is not None:
            self._parent.remove_child(self)

    def children(self):
        """
        Get all nodes of the sub graph.

        Returns:
            list[AutoNode].
        """

        return list(self._children)

    def create_input_node(self, update=True):
        """
        Create a sub graph input node.

        Args:
            update(bool): whether increase node 'input count' property.
        """
        input_node = self.graph.create_node('Utility.SubGraphInput', pos=[-400, 200 * len(self.sub_graph_input_nodes)])
        input_node.set_property('input index', len(self.sub_graph_input_nodes))
        self.sub_graph_input_nodes.append(input_node)
        input_node.set_parent(self)
        if update:
            self.set_property('input count', self.get_property('input count') + 1)
            self.update_port()
        return input_node

    def create_output_node(self, update=True):
        """
        Create a sub graph output node.

        Args:
            update(bool): whether increase node 'output count' property.
        """
        output_node = self.graph.create_node('Utility.SubGraphOutput',
                                             pos=[400, 200 * len(self.sub_graph_output_nodes)])
        output_node.set_property('output index', len(self.sub_graph_output_nodes))
        self.sub_graph_output_nodes.append(output_node)
        output_node.set_parent(self)

        if update:
            self.set_property('output count', self.get_property('output count') + 1)
            self.update_port()
        return output_node

    def create_from_nodes(self, nodes):
        """
        Create a SubGraph from the nodes.
        It will auto create input and output ports and nodes.

        Args:
            nodes(list[AutoNode]): nodes to create the sub graph.
        """

        if self in nodes:
            nodes.remove(self)
        [n.set_parent(self) for n in nodes]
        # if not nodes:
        #     return

        self.set_property('input count', 0)
        self.set_property('output count', 0)

        in_connect = []
        out_connect = []
        connected = []

        for node in nodes:
            if isinstance(node, BackdropNode):
                continue
            for port in node.input_ports():
                for pipe in port.view.connected_pipes:
                    if pipe.output_port.isVisible():
                        in_connect.append((pipe.output_port, pipe.input_port))
            for port in node.output_ports():
                for pipe in port.view.connected_pipes:
                    if pipe.input_port.isVisible():
                        out_connect.append((pipe.output_port, pipe.input_port))
        in_map = {}
        for idx, ports in enumerate(in_connect):
            if ports[0] in in_map.keys():
                in_map[ports[0]].append([ports[1], in_map[ports[0]][0][1]])
            else:
                self.create_input_node()
                if idx > 0:
                    in_map[ports[0]] = [[ports[1], len(self.input_ports()) - 1]]
                else:
                    in_map[ports[0]] = [[ports[1], 0]]

        for port0, data in in_map.items():
            for port_data in data:
                idx = port_data[1]
                connected.append((port0, self.input_ports()[idx].view))
                connected.append((self.sub_graph_input_nodes[idx].output_ports()[0].view, port_data[0]))

        out_map = {}
        for idx, ports in enumerate(out_connect):
            if ports[0] in out_map.keys():
                out_map[ports[0]].append([ports[1], out_map[ports[0]][0][1]])
            else:
                self.create_output_node()
                if idx > 0:
                    out_map[ports[0]] = [[ports[1], len(self.output_ports()) - 1]]
                else:
                    out_map[ports[0]] = [[ports[1], 0]]

        for port0, data in out_map.items():
            for port_data in data:
                idx = port_data[1]
                connected.append((port0, self.sub_graph_output_nodes[idx].input_ports()[0].view))
                connected.append((self.output_ports()[idx].view, port_data[0]))

        disconnected = in_connect + out_connect

        if disconnected or connected:
            self.graph._on_connection_changed(disconnected, connected)

        if len(self.input_ports()) == 0:
            self.create_input_node()
        if len(self.output_ports()) == 0:
            self.create_output_node()
        self.set_property('create_from_select', False)
        print(self.get_property('input count'))

    def update_ports(self):
        """
        Auto create/delete input and output ports by node property 'input count' and 'output count'.
        """

        input_count = self.get_property('input count')
        output_count = self.get_property('output count')
        current_input_count = len(self.input_ports())
        current_output_count = len(self.output_ports())

        update = False
        if input_count != current_input_count:
            if input_count > current_input_count:
                for i in range(input_count - current_input_count):
                    self.add_input('input' + str(len(self.input_ports())))
            else:
                for i in range(current_input_count - input_count):
                    self.delete_input(current_input_count - i - 1)
            update = True

        if output_count != current_output_count:
            if output_count > current_output_count:
                for i in range(output_count - current_output_count):
                    self.add_output('output' + str(len(self.output_ports())))
            else:
                for i in range(current_output_count - output_count):
                    self.delete_output(current_output_count - i - 1)
            update = True

        if update:
            self.view.draw_node()

    def publish(self, file_path, node_name, node_identifier, node_class_name):
        """
        Publish the sub graph as a file.
        It will auto create input and output ports and nodes.

        Args:
            file_path(str): sub graph node published file path.
            node_name(str): new sub graph node name.
            node_identifier(str): new sub graph node identifier.
            node_class_name(str): new sub graph node class object name.
        Returns:
            str: new sub graph node file path.
            None: publish failed.
        """

        if file_path and node_name and node_identifier and node_class_name:
            serialized_data = self.graph._serialize([self])
            data = {'node': serialized_data['nodes'][self.id]}
            data['sub_graph'] = data['node'].pop('sub_graph')
            data['node']['__identifier__'] = node_identifier
            data['node']['NODE_CATEGORY'] = self.NODE_CATEGORY
            data['node']['CHILDREN_CATEGORY'] = self.CHILDREN_CATEGORY
            data['node']['name'] = node_name
            data['node']['class_name'] = node_class_name.replace(" ", "_")
            data['node']['custom']['published'] = True
            data['node'].pop('type_')
            file_path = file_path.strip()
            with open(file_path, 'w') as file_out:
                json.dump(data, file_out, indent=2, separators=(',', ':'))
            return file_path
        return None


class SubGraphInputNode(AutoNode):
    """
    sub graph input node.
    """
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'SubGraphInput'

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(SubGraphInputNode, self).__init__(defaultInputType, defaultOutputType)
        self.set_property('color', (0.1568, 0.196, 0.2588))
        self.add_output('out')
        self.add_int_input('input index', 'input index', value=0)

    def get_data(self, port):
        parent = self.parent()
        if parent is not None:
            from_port = self.get_parent_port(parent)
            if from_port:
                return from_port.node().get_data(from_port)
            else:
                # can not find port
                return self.defaultValue
        else:
            # can not find parent
            return self.defaultValue

    def get_parent_port(self, parent=None):
        if parent is None:
            parent = self.parent()
        index = self.get_property('input index')
        if index < 0 or index >= len(parent.inputs()):
            self.error('input index out of range !!!')
            return None
        to_port = parent.input(int(index))
        from_ports = to_port.connected_ports()
        if from_ports:
            return from_ports[0]
        else:
            return None


class SubGraphOutputNode(AutoNode):
    """
    sub graph output node.
    """
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'SubGraphOutput'

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(SubGraphOutputNode, self).__init__(defaultInputType, defaultOutputType)
        self.set_property('color', (0.1568, 0.196, 0.2588))
        self.add_input('in')
        self.add_int_input('output index', 'output index', value=0)

    def get_data(self, port=None):
        to_port = self.input(0)
        from_ports = to_port.connected_ports()
        if not from_ports:
            return self.defaultValue

        for from_port in from_ports:
            return from_port.node().get_data(from_port)

    def run(self):
        parent = self.parent()
        if parent is None:
            return
        if not parent.auto_cook:
            return

        port = parent.get_output(self.get_property('output index'))
        if not port:
            return

        to_ports = port.connected_ports()
        if not to_ports:
            return

        nodes = [p.node() for p in to_ports]
        update_node_down_stream(nodes)


class RootNode(SubGraphNode):
    """
    Root node of the NodeGraphQt.NodeGraph.
    """

    __identifier__ = '__None'

    # initial default node name.
    NODE_NAME = 'root'
    NODE_CATEGORY = NodeCategory.NONE
    CHILDREN_CATEGORY = NodeCategory.GEOMETRY

    def __init__(self):
        super(RootNode, self).__init__()
        self.create_property('root', True)
        self.model.set_property('id', '0' * 13)
        self.init_sub_graph(False)

    def set_graph(self, graph):
        super(RootNode, self).set_graph(graph)
        graph.set_node_space(self)

    def has_error(self):
        return False


def read_json(file_path):
    file_path = file_path.strip()
    if not os.path.isfile(file_path):
        raise IOError('node file {} does not exist.'.format(file_path))
    try:
        with open(file_path) as data_file:
            layout_data = json.load(data_file)
    except Exception as e:
        layout_data = None
        print('Cannot read data from file.\n{}'.format(e))
    return layout_data


class PublishedNode(object):
    """
    Read published sub graph file and create corresponding node class.
    """

    __identifier__ = '__None'
    NODE_NAME = '__None'
    NODE_FILE = None
    NODE_CATEGORY = None

    def create_from_file(self):
        """
        Update node properties and create sub graph nodes by published node file.
        """

        if self.NODE_FILE is None or not self.get_property('published'):
            return
        data = read_json(self.NODE_FILE)
        if not data:
            return

        children_data = data.pop('sub_graph')

        if not self.create_by_deserialize:
            n_data = data.pop('node')
            n_data.pop('name')
            # set properties.
            for prop in self.model.properties.keys():
                if prop in n_data.keys():
                    self.model.set_property(prop, n_data[prop])
            # set custom properties.
            for prop, val in n_data.get('custom', {}).items():
                self.model.set_property(prop, val)

            if n_data.get('dynamic_port', None):
                self.set_ports({'input_ports': n_data['input_ports'], 'output_ports': n_data['output_ports']})

        children = self.graph._deserialize(children_data, set_parent=False)
        [node.set_parent(self) for node in children]

    @staticmethod
    def create_node_class(file_path, parent_class):
        """
        Create a new node class by published node file.

        Args:
            file_path(str): published node file path.
            parent_class(object): published node class.
        """

        data = read_json(file_path)

        if not data:
            return None
        try:
            class_name = data['node']['class_name']
            new_node_class = type(class_name, (parent_class,), {'NODE_FILE': file_path})
            new_node_class.__identifier__ = data['node']['__identifier__']
            new_node_class.NODE_NAME = data['node']['name']
            new_node_class.NODE_CATEGORY = data['node']['NODE_CATEGORY']
            new_node_class.CHILDREN_CATEGORY = data['node']['CHILDREN_CATEGORY']
            return new_node_class
        except:
            print('file {} is not a correct published node.'.format(file_path))
            return None