from ...vendor.NodeGraphQt import BaseNode, Port, QtCore
from . utils import update_node_down_stream, convert_data_type
import hashlib
import copy
import time
from ...widgets.parameterTree import DEFAULT_VALUE_MAP, build_curve_ramp, get_ramp_colors, get_ramp_color
import numpy as np
import traceback

NODE_NONE = 0
NODE_WARNING = 1
NODE_ERROR = 2


class CryptoColors(object):
    """
    Generate random color based on strings
    """

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
        # a = int(Min + (int("0x" + h[48:], 0) / d) * (Max - Min))
        self.colors[text] = (r, g, b, 255)
        return self.colors[text]


class AutoNode(BaseNode, QtCore.QObject):
    cooked = QtCore.Signal()
    param_changed = QtCore.Signal()
    input_changed = QtCore.Signal()

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(AutoNode, self).__init__()
        QtCore.QObject.__init__(self)
        self._needCook = True
        self.matchTypes = [['float', 'int']]
        self.errorColor = (0.784, 0.196, 0.196)
        self.stopCookColor = (0.784, 0.784, 0.784)
        self._cryptoColors = CryptoColors()

        self.create_property('auto_cook', True)
        self.create_property('default_color', self.get_property('color'))
        self.defaultValue = None
        self.defaultInputType = defaultInputType
        self.defaultOutputType = defaultOutputType

        self._cook_time = 0.0
        self._message = ""
        self._message_level = NODE_NONE
        self._params = {}

    @property
    def auto_cook(self):
        """
        Returns whether the node can update stream automatically.
        """

        return self.get_property('auto_cook')

    @auto_cook.setter
    def auto_cook(self, mode):
        """
        Set whether the node can update stream automatically.

        Args:
            mode(bool).
        """

        if mode is self.auto_cook:
            return

        self.model.set_property('auto_cook', mode)
        if mode:
            self.set_property('color', self.get_property('default_color'))
        else:
            self.model.set_property('default_color', self.get_property('color'))
            self.set_property('color', self.stopCookColor)

    def cook_time(self):
        """
        Returns the last cooked time of the node.
        """

        return self._cook_time

    def has_error(self):
        """
        Returns whether the node has errors.
        """

        return self._message_level is NODE_ERROR

    def update_stream(self, forceCook=False):
        """
        Update all down stream nodes.

        Args:
            forceCook(bool): if True, it will ignore the auto_cook and so on.
        """

        if not forceCook:
            if not self.auto_cook or not self._needCook:
                return
            if self.graph is not None and not self.graph.auto_update:
                return
        update_node_down_stream(self)

    def get_data(self, port):
        """
        Get node data by port.
        Most time it will called by output nodes of the node.

        Args:
            port(Port).

        Returns:
            node data.
        """
        if self.disabled() and self.input_ports():
            out_ports = self.output_ports()
            if port in out_ports:
                idx = out_ports.index(port)
                max_idx = max(0, len(self.input_ports()) - 1)
                return self.get_input_data(min(idx, max_idx))

        return self.get_property(port.name())

    def get_input_data(self, port):
        """
        Get input data by input port name/index/object.

        Args:
            port(str/int/Port): input port name/index/object.
        """

        if type(port) is not Port:
            to_port = self.get_input(port)
        else:
            to_port = port
        if to_port is None:
            return copy.deepcopy(self.defaultValue)

        from_ports = to_port.connected_ports()
        if not from_ports:
            return copy.deepcopy(self.defaultValue)

        for from_port in from_ports:
            data = from_port.node().get_data(from_port)
            return copy.deepcopy(data)

    def cook(self):
        """
        The entry of the node evaluation.
        Most time we need to call this method instead of AutoNode.run'.
        """

        _tmp = self.auto_cook
        self.model.set_property('auto_cook', False)

        self._close_message()

        _start_time = time.time()

        try:
            self.run()
        except:
            self.error(traceback.format_exc())

        self.model.set_property('auto_cook', _tmp)

        if self._message_level is NODE_ERROR:
            return

        self._cook_time = time.time() - _start_time

        self.cooked.emit()

    def run(self):
        """
        Node evaluation logic.
        """

        pass

    def on_input_connected(self, to_port, from_port):
        if self.check_port_type(to_port, from_port):
            self.update_stream()
        else:
            self._needCook = False
            to_port.disconnect_from(from_port)
        self.input_changed.emit()

    def on_input_disconnected(self, to_port, from_port):
        if not self._needCook:
            self._needCook = True
            return
        self.update_stream()
        self.input_changed.emit()

    def check_port_type(self, to_port, from_port):
        """
        Check whether the port_type of the to_port and from_type is matched.

        Args:
            to_port(Port).
            from_port(Port).

        Returns:
            bool.
        """

        if to_port.data_type != from_port.data_type:
            if to_port.data_type == 'None' or from_port.data_type == 'None':
                return True
            for types in self.matchTypes:
                if to_port.data_type in types and from_port.data_type in types:
                    return True
            return False

        return True

    def set_property(self, name, value):
        super(AutoNode, self).set_property(name, value)
        self.set_port_type(name, type(value).__name__)
        if name in self.model.custom_properties.keys():
            self.update_stream()

    def set_port_type(self, port, data_type: str):
        """
        Set the data_type of the port.

        Args:
            port(Port): the port to set the data_type.
            data_type(str): port new data_type.
        """

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
            if current_port.data_type == data_type:
                return
            else:
                current_port.data_type = data_type

            current_port.border_color = current_port.color = self._cryptoColors.get(data_type)
            conn_type = 'multi' if current_port.multi_connection() else 'single'
            current_port.view.setToolTip('{}: {} ({}) '.format(current_port.name(), data_type, conn_type))

    def add_input(self, name='input', data_type='None', multi_input=False, display_name=True,
                  color=None):
        new_port = super(AutoNode, self).add_input(name, multi_input, display_name, color)
        if data_type == 'None' and self.defaultInputType is not None:
            data_type = self.defaultInputType
        self.set_port_type(new_port, convert_data_type(data_type))

        return new_port

    def add_output(self, name='output', data_type='None', multi_output=True, display_name=True,
                   color=None):
        new_port = super(AutoNode, self).add_output(name, multi_output, display_name, color)
        if data_type == 'None' and self.defaultOutputType is not None:
            data_type = self.defaultOutputType
        self.set_port_type(new_port, convert_data_type(data_type))

        return new_port

    def set_disabled(self, mode=False):
        super(AutoNode, self).set_disabled(mode)
        self.update_stream()
        if mode:
            self.cooked.emit()

    def get_message(self):
        """
        Returns the node warning/error message.
        """
        return self._message, self._message_level

    def _close_message(self):
        """
        Set node to normal mode and clear the node warning/error message.
        """

        if self._message_level is not NODE_NONE:
            self.set_property('color', self.get_property('default_color'))
            self._message = ""
            self._message_level = NODE_NONE

    def _set_message(self, message, message_level):
        """
        Set node message.
        It will change the node color.

        Args:
            message(str): the describe of the error.
            message_level(int): NODE_NONE/NODE_WARNING/NODE_ERROR.
        """

        if self._message_level is NODE_NONE:
            self.model.set_property('default_color', self.get_property('color'))
        self._message = str(message)
        self._message_level = message_level
        if message_level is NODE_ERROR:
            self.set_property('color', self.errorColor)

    def error(self, message):
        """
        Set message_level to NODE_ERROR and change the node color.

        Args:
            message(str): the describe of the error.
        """

        self._set_message(message, NODE_ERROR)

    def warning(self, message):
        """
        Set message_level to NODE_WARNING.

        Args:
            message(str): the describe of the warning.
        """
        self._set_message(message, NODE_WARNING)

    def set_parameters(self, params, tab='Parameters'):
        """
        Update the node parameters.

        Args:
            params(dict): node parameters data.
            tab(str): the tab name of parameters.
        """

        self._params.update({tab: params})
        self.__create_props(params)
        self.param_changed.emit()

    def __create_props(self, params: list):
        """
        Update the node properties by parameter data.

        Args:
            params(list): node parameters data.
        """

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
        """
        Get the curve ramp parameter data by keys.

        Returns:
            numpy.ndarray, size:(len(keys),).
        """

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
        """
        Get the color ramp parameter data by keys.

        Returns:
            numpy.ndarray, size:(len(keys),3).
        """

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
        """
        Get the ramp color parameter data by key.

        Returns:
            r, g, b.
        """

        p = self.get_property(name)
        if type(p) is not list:
            raise Exception("please input a color ramp parameter name")

        return get_ramp_color(p[0], p[1], p[2], key)

    def update_parameters(self):
        """
        Update parameters by properties.
        """

        [self.__update_params(p) for p in self._params.values()]
        self.param_changed.emit()

    def __update_params(self, params: list):
        """
        Update parameters by properties.

        Args:
            params(list): parameters to be updated.
        """

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
        """
        Update list type parameter widget.

        Args:
            name(str): parameter name.
            items(list): parameter widget new items.
            reload(bool) if true the parameter value will forced be one of the items.
        """

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
        """
        Update list type parameter widget.

        Args:
            name(str): parameter name.
            items(list): parameter widget new items.
        """

        self._update_list_param(name, items)

    def update_list_text_param(self, name, items):
        """
        Update list text type parameter widget.

        Args:
            name(str): parameter name.
            items(str/list[str]).
        """

        if type(items) is str:
            items = [items]
        self._update_list_param(name, items, False)

    def get_params(self):
        """
        Get node parameters data.

        Returns:
            dict: parameters data.
        """
        return self._params

    # def __del__(self):
    #     print("Delete: ", self.path())