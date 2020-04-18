from ...vendor.NodeGraphQt import topological_sort_by_down, QtCore
from threading import Thread
import hashlib


class CookThread(Thread):
    def __init__(self):
        super(CookThread, self).__init__()
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
    # thread = CookThread()
    # thread.start_nodes = nodes
    # thread.start()


def update_nodes(nodes):
    _update_nodes(topological_sort_by_down(all_nodes=nodes))
    # thread = CookThread()
    # thread.all_nodes = nodes
    # thread.start()


def get_data_type(data_type):
    if not isinstance(data_type, str):
        if hasattr(data_type, '__name__'):
            data_type = data_type.__name__
        else:
            data_type = type(data_type).__name__
    return data_type


class CryptoColors(object):
    """
    Generate random color based on strings
    """

    colors = {}

    @staticmethod
    def get(text, Min=50, Max=200):
        if text in CryptoColors.colors:
            return CryptoColors.colors[text]
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        d = int('0xFFFFFFFFFFFFFFFF', 0)
        r = int(Min + (int("0x" + h[:16], 0) / d) * (Max - Min))
        g = int(Min + (int("0x" + h[16:32], 0) / d) * (Max - Min))
        b = int(Min + (int("0x" + h[32:48], 0) / d) * (Max - Min))
        # a = int(Min + (int("0x" + h[48:], 0) / d) * (Max - Min))
        CryptoColors.colors[text] = (r, g, b, 255)
        return CryptoColors.colors[text]