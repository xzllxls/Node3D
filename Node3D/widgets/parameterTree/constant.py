from ...vendor.NodeGraphQt.constants import *

TYPE_MAP = {
    NODE_PROP_QLABEL: 'label',
    NODE_PROP_QLINEEDIT: 'str',
    NODE_PROP_QTEXTEDIT: 'text',
    NODE_PROP_QCOMBO: 'list',
    NODE_PROP_QCHECKBOX: 'bool',
    NODE_PROP_QSPINBOX: 'float_',
    NODE_PROP_COLORPICKER: 'color',
    NODE_PROP_SLIDER: 'float',
    NODE_PROP_FILE: 'file',
    NODE_PROP_VECTOR2: 'vector2',
    NODE_PROP_VECTOR3: 'vector3',
    NODE_PROP_VECTOR4: 'vector4',
    NODE_PROP_FLOAT: 'float',
    NODE_PROP_INT: 'int',
    NODE_PROP_BUTTON: 'action',
}


DEFAULT_VALUE_MAP = {
    'label': "",
    'str': "",
    'list': [],
    'bool': False,
    'float_': 0.0,
    'int_': 0,
    'float': 0.0,
    'int': 0.0,
    'color': (1.0, 1.0, 1.0),
    'file': "",
    'vector2': [0, 0],
    'vector3': [0, 0, 0],
    'vector4': [0, 0, 0, 0],
    'vector2i': [0, 0],
    'vector3i': [0, 0, 0],
    'vector4i': [0, 0, 0, 0],
    'action': None,
    'spacer': None,
    'curveRamp': [[(0, 0), [1, 1]], 'quadratic'],
    'colorRamp': [[(0.0, 0.0, 0.0, 1.0), (1.0, 1.0, 1.0, 1.0)], [0, 1], 'linear'],
}
