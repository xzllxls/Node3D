from .geometry_node import GeometryNode
from ...vendor.NodeGraphQt.constants import NODE_PROP_QTEXTEDIT, NODE_PROP_QCHECKBOX
import numpy as np
import math


class ScriptNode(GeometryNode):
    def __init__(self, pre_generate=True):
        super(ScriptNode, self).__init__(pre_generate)
        self.add_input('geo1')
        self.add_input('geo2')
        self.create_property('Script', '', widget_type=NODE_PROP_QTEXTEDIT)
        self.create_property('Depend Time', False, widget_type=NODE_PROP_QCHECKBOX)
        self.namespace = {'node': self, 'np': np, 'gp': self.graph, 'math': math}

    def update_namespace(self, namespace):
        self.namespace.update(namespace)

    def set_property(self, name, value):
        super(ScriptNode, self).set_property(name, value)
        if name == 'Depend Time':
            self.set_depend_time(value)



