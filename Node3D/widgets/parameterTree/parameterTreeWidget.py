from ...vendor.pyqtgraph.parametertree import ParameterTree
from ..styles import PROP_TREE_VIEW


class NodeParamTreeWidget(ParameterTree):
    def __init__(self, parent=None):
        super(NodeParamTreeWidget, self).__init__(parent, showHeader=False)
        self.param = None
        self.setStyleSheet(PROP_TREE_VIEW)

    def __repr__(self):
        return '<NodeParamTreeWidget object at {}>'.format(hex(id(self)))

    def add_widget(self, name, widget, value, label=None):
        pass

    def get_widget(self, name, param=None):
        if param is None:
            param = self.param
            if param is None:
                return None
        if name in param.names.keys():
            return param.names[name]
        else:
            for child in param.names.values():
                wid = self.get_widget(name, child)
                if wid is not None:
                    return wid
        return None

    def setParameters(self, param, showTop=True):
        self.param = param
        super(NodeParamTreeWidget, self).setParameters(param, showTop)
