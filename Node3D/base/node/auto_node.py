from ...vendor.NodeGraphQt import BaseNode
from ...vendor.NodeGraphQt.base.port import Port
from ...vendor.NodeGraphQt.constants import NODE_PROP
from ...vendor.NodeGraphQt import QtCore
import hashlib
import copy
import time
from ...widgets.parameterTree import DEFAULT_VALUE_MAP, build_curve_ramp, get_ramp_colors, get_ramp_color
import numpy as np
import traceback

NODE_NONE = 0
NODE_WARNING = 1
NODE_ERROR = 2


# Generate random color based on strings
class CryptoColors(object):
    def __init__(self):
        self.colors = {}

    def get(self, text, Min=50, Max=200):
        if text in self.colors:
            return self.colors[text]
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        d = int('0xFFFFFFFFFFFFFFFF', 0)
        r = int(Min + (int("0x" + h[:16], 0) / d) * (Max - Min))
        g = int(Min + (int("0x" + h[16:32], 0) / d) * (Max - Min))
        b = int(Min + (int("0x" + h[32:48], 0) / d) * (Max - Min))
        a = int(Min + (int("0x" + h[48:], 0) / d) * (Max - Min))
        self.colors[text] = (r, g, b, 255)
        return self.colors[text]


class AutoNode(BaseNode, QtCore.QObject):
    cooked = QtCore.Signal()
    param_changed = QtCore.Signal()
    input_changed = QtCore.Signal()

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(AutoNode, self).__init__()
        QtCore.QObject.__init__(self)
        self.needCook = True
        self._autoCook = True
        self._error = False
        self.matchTypes = [[float, int]]
        self.errorColor = (0.784, 0.196, 0.196)
        self.stopCookColor = (0.784, 0.784, 0.784)
        self._cryptoColors = CryptoColors()

        self.defaultColor = self.get_property("color")
        self.defaultValue = None
        self.defaultInputType = defaultInputType
        self.defaultOutputType = defaultOutputType

        self._cookTime = 0.0
        self._message = ""
        self._message_level = NODE_NONE
        self._params = {}

    @property
    def autoCook(self):
        return self._autoCook

    @autoCook.setter
    def autoCook(self, mode):
        if mode is self._autoCook:
            return

        self._autoCook = mode
        if mode:
            self.set_property('color', self.defaultColor)
        else:
            self.defaultColor = self.get_property("color")
            self.set_property('color', self.stopCookColor)

    def getCookTime(self):
        return self._cookTime

    def cookNextNode(self):
        for nodeList in self.connected_output_nodes().values():
            for n in nodeList:
                n.cook()

    def getData(self, port):
        # for custom output data
        return self.get_property(port.name())

    def getInputData(self, port):
        """
        get input data by input Port,the type of "port" can be :
        int : Port index
        str : Port name
        Port : Port object
        """

        if type(port) is int:
            to_port = self.input(port)
        elif type(port) is str:
            to_port = self.inputs()[port]
        elif type(port) is Port:
            to_port = port
        else:
            return self.defaultValue

        from_ports = to_port.connected_ports()
        if not from_ports:
            return copy.deepcopy(self.defaultValue)

        for from_port in from_ports:
            data = from_port.node().getData(from_port)
            return copy.deepcopy(data)

    def when_disabled(self):
        num = len(self.input_ports())
        for index, out_port in enumerate(self.output_ports()):
            self.set_property(out_port.name(), self.getInputData(index % num))

    def cook(self, forceCook=False):
        if not self._autoCook and forceCook is not True:
            if self.get_property('disabled'):
                self.cookNextNode()
            return

        if not self.needCook:
            return

        _tmp = self._autoCook
        self._autoCook = False

        self._close_message()

        _start_time = time.time()

        try:
            self.run()
        except:
            self.error(traceback.format_exc())

        self._autoCook = _tmp

        if self._message_level is NODE_ERROR:
            return

        self._cookTime = time.time() - _start_time

        self.cooked.emit()
        self.cookNextNode()

    def run(self):
        pass

    def on_input_connected(self, to_port, from_port):
        if self.checkPortType(to_port, from_port):
            self.cook()
        else:
            self.needCook = False
            to_port.disconnect_from(from_port)
        self.input_changed.emit()

    def on_input_disconnected(self, to_port, from_port):
        if not self.needCook:
            self.needCook = True
            return
        self.cook()
        self.input_changed.emit()

    def checkPortType(self, to_port, from_port):
        # None type port can connect with any other type port
        # types in self.matchTypes can connect with each other

        if hasattr(to_port, "DataType") and hasattr(from_port, "DataType"):
            if to_port.DataType is not from_port.DataType:
                for types in self.matchTypes:
                    if to_port.DataType in types and from_port.DataType in types:
                        return True
                return False

        return True

    def set_property(self, name, value):
        super(AutoNode, self).set_property(name, value)
        self.set_port_type(name, type(value))
        if name in self.model.custom_properties.keys():
            self.cook()

    def set_port_type(self, port, value_type):
        current_port = None

        if type(port) is Port:
            current_port = port
        elif type(port) is str:
            inputs = self.inputs()
            outputs = self.outputs()
            if port in inputs.keys():
                current_port = inputs[port]
            elif port in outputs.keys():
                current_port = outputs[port]

        if current_port:
            if hasattr(current_port, "DataType"):
                if current_port.DataType is value_type:
                    return
            else:
                current_port.DataType = value_type

            current_port.border_color = self._cryptoColors.get(str(value_type))
            current_port.color = self._cryptoColors.get(str(value_type))
            conn_type = 'multi' if current_port.multi_connection() else 'single'
            data_type_name = value_type.__name__ if value_type else "all"
            current_port.view.setToolTip('{}: {} ({}) '.format(current_port.name(), data_type_name, conn_type))

    def create_property(self, name, value, items=None, range=None,
                        widget_type=NODE_PROP, tab=None, ext=None, funcs=None):
        super(AutoNode, self).create_property(name, value, items, range, widget_type, tab, ext, funcs)

        if value is not None:
            self.set_port_type(name, type(value))

    def add_input(self, name='input', data_type=None, multi_input=False, display_name=True,
                  color=None):
        new_port = super(AutoNode, self).add_input(name, multi_input, display_name, color)
        if data_type:
            self.set_port_type(new_port, data_type)
        elif self.defaultInputType:
            self.set_port_type(new_port, self.defaultInputType)
        return new_port

    def add_output(self, name='output', data_type=None, multi_output=True, display_name=True,
                   color=None):
        new_port = super(AutoNode, self).add_output(name, multi_output, display_name, color)
        if data_type:
            self.set_port_type(new_port, data_type)
        elif self.defaultOutputType:
            self.set_port_type(new_port, self.defaultOutputType)
        return new_port

    def set_disabled(self, mode=False):
        super(AutoNode, self).set_disabled(mode)
        self._autoCook = not mode
        if mode is True:
            self.when_disabled()
            self.cookNextNode()
        else:
            self.cook()

    def get_message(self):
        return self._message, self._message_level

    def _close_message(self):
        if self._message_level is not NODE_NONE:
            self.set_property('color', self.defaultColor)
            self._message = ""
            self._message_level = NODE_NONE

    def _set_message(self, message, message_level):
        if self._message_level is NODE_NONE:
            self.defaultColor = self.get_property("color")
        self._message = str(message)
        self._message_level = message_level
        if message_level is NODE_ERROR:
            self.set_property('color', self.errorColor)

    def error(self, message):
        self._set_message(message, NODE_ERROR)

    def warning(self, message):
        self._set_message(message, NODE_WARNING)

    def update_model(self):
        if self._message_level is not NODE_NONE:
            self.set_property('color', self.defaultColor)
        super(AutoNode, self).update_model()

    def set_parameters(self, params, tab='Parameters'):
        self._params.update({tab: params})
        self.__create_props(params)
        self.param_changed.emit()

    def __create_props(self, params: list):
        for p in params:
            if 'children' not in p.keys():
                if p['type'] == 'action':
                    continue
                prop_name = p['name']
                if 'value' in p.keys():
                    value = p['value']
                else:
                    if 'limits' in p.keys():
                        value = p['limits'][0]
                    else:
                        value = DEFAULT_VALUE_MAP.get(p['type'], None)
                if not self.has_property(prop_name):
                    self.create_property(prop_name, value)
                else:
                    self.set_property(prop_name, value)
            else:
                self.__create_props(p['children'])

    def get_ramp_values(self, name, keys):
        p = self.get_property(name)
        if type(p) is not list:
            raise Exception("please input a ramp parameter name")
        """
        values = p[0]
        kind = p[1]
        """
        f = build_curve_ramp(p[0], p[1])
        if p is None:
            return None
        keys = np.clip(keys, 0, 1)
        return f(keys)

    def get_ramp_colors(self, name, keys):
        p = self.get_property(name)
        if type(p) is not list:
            raise Exception("please input a color ramp parameter name")
        """
        colors = p[0]
        pos = p[1]
        kind = p[2]
        """
        return get_ramp_colors(p[0], p[1], p[2], keys)

    def get_ramp_color(self, name, key):
        p = self.get_property(name)
        if type(p) is not list:
            raise Exception("please input a color ramp parameter name")

        return get_ramp_color(p[0], p[1], p[2], key)

    def update_parameters(self):
        [self.__update_params(p) for p in self._params.values()]
        self.param_changed.emit()

    def __update_params(self, params: list):
        for p in params:
            if 'children' not in p.keys():
                prop_name = p['name']
                p['value'] = self.get_property(prop_name)
                tp = p['type']

                if tp == 'button':
                    p['node'] = self

                elif tp == 'list' or tp == 'listText':
                    _prop_name = '_' + p['name'] + "_"
                    if self.has_property(_prop_name):
                        p['limits'] = self.get_property(_prop_name)
            else:
                self.__update_params(p['children'])

    def _update_list_param(self, name, items, reload=True):
        if not self.has_property(name):
            return
        old_value = self.get_property(name)
        self.set_property(name, items)
        _name = '_' + name + "_"
        if not self.has_property(_name):
            self.create_property(_name, items)
        else:
            self.set_property(_name, items)

        if reload:
            if old_value in items:
                self.set_property(name, old_value)
            else:
                self.set_property(name, items[0])
        else:
            self.set_property(name, old_value)

    def update_list_param(self, name, items):
        self._update_list_param(name, items)

    def update_list_text_param(self, name, attribute_class):
        if type(attribute_class) is str:
            attribute_class = [attribute_class]
        self._update_list_param(name, attribute_class, False)

    def get_params(self):
        return self._params
