from ...vendor.NodeGraphQt import topological_sort_by_down, QtCore, NodeGraph


class CookThread(QtCore.QThread):
    def __init__(self, parent):
        super(CookThread, self).__init__(parent)
        self.start_nodes = None
        self.all_nodes = None

    def run(self):
        _update_nodes(topological_sort_by_down(start_nodes=self.start_nodes,
                                               all_nodes=self.all_nodes))


def _update_nodes(nodes):
    for node in nodes:
        if node.disabled():
            continue
        node.cook()
        if node.has_error():
            break


def update_node_down_stream(nodes):
    if not isinstance(nodes, list):
        nodes = [nodes]
    _update_nodes(topological_sort_by_down(start_nodes=nodes))
    # thread = CookThread(NodeGraph.graph_instance.widget)
    # thread.start_nodes = nodes
    # thread.start()


def update_nodes(nodes):
    _update_nodes(topological_sort_by_down(all_nodes=nodes))
    # thread = CookThread(NodeGraph.graph_instance.widget)
    # thread.all_nodes = nodes
    # thread.start()


def convert_data_type(data_type):
    if type(data_type) is not str:
        if data_type is None:
            data_type = 'None'
        else:
            try:
                data_type = data_type.__name__
            except:
                data_type = type(data_type).__name__
    return data_type