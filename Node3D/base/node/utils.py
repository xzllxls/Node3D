from ...vendor.NodeGraphQt import topological_sort_by_down


def _update_nodes(nodes):
    for node in nodes:
        if node.disabled():
            node.when_disabled()
        else:
            node.cook()
        if node.has_error():
            break


def update_node_down_stream(node=None, nodes=None):
    if node is not None:
        _update_nodes(topological_sort_by_down(start_nodes=[node]))
    elif nodes is not None:
        _update_nodes(topological_sort_by_down(start_nodes=nodes))


def update_nodes(nodes):
    _update_nodes(topological_sort_by_down(all_nodes=nodes))


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