from ...vendor.NodeGraphQt import PropertiesBinWidget
from ...vendor.NodeGraphQt.widgets.properties import defaultdict, PropLineEdit
from ...vendor.NodeGraphQt.constants import *
from Qt import QtCore, QtWidgets, QtGui
from .parameterTreeWidget import NodeParamTreeWidget
from ...vendor.pyqtgraph.parametertree import Parameter
from .constant import TYPE_MAP


class PropWidget(QtWidgets.QWidget):
    #: signal (node_id, prop_name, prop_value)
    property_changed = QtCore.Signal(str, str, object)
    property_closed = QtCore.Signal(str)

    def __init__(self, parent=None, node=None):
        super(PropWidget, self).__init__(parent)
        self.__node_id = node.id
        self.__tab_windows = {}
        self.__tab = QtWidgets.QTabWidget()

        close_btn = QtWidgets.QPushButton('')
        close_btn.setIcon(QtGui.QIcon(ICON_CLOSE))
        close_btn.setToolTip('close property')
        close_btn.clicked.connect(self._on_close)

        self.name_wgt = PropLineEdit()
        self.name_wgt.setToolTip('name')
        self.name_wgt.set_value(node.name())
        self.name_wgt.value_changed.connect(self._on_property_changed)

        self.type_wgt = QtWidgets.QLabel(node.type_)
        self.type_wgt.setAlignment(QtCore.Qt.AlignRight)
        self.type_wgt.setToolTip('type_')
        font = self.type_wgt.font()
        font.setPointSize(10)
        self.type_wgt.setFont(font)

        name_layout = QtWidgets.QHBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.addWidget(QtWidgets.QLabel('name'))
        name_layout.addWidget(self.name_wgt)
        name_layout.addWidget(close_btn)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(4)
        layout.addLayout(name_layout)
        layout.addWidget(self.__tab)
        layout.addWidget(self.type_wgt)
        self._read_node(node)

    def __repr__(self):
        return '<NodePropWidget object at {}>'.format(hex(id(self)))

    def value_change(self, p, changes):
        for param, change, data in changes:
            name = param.name()
            if change == 'value':
                self._on_property_changed(name, data)

    def _on_close(self):
        """
        called by the close button.
        """
        self.property_closed.emit(self.__node_id)

    def _on_property_changed(self, name, value):
        """
        slot function called when a property widget has changed.

        Args:
            name (str): property name.
            value (object): new value.
        """
        self.property_changed.emit(self.__node_id, name, value)

    def _read_node(self, node):
        from ...base.node import AutoNode

        model = node.model
        graph_model = node.graph.model

        common_props = graph_model.get_node_common_properties(node.type_)

        # sort tabs and properties.
        tab_mapping = defaultdict(list)
        for prop_name, prop_val in model.custom_properties.items():
            try:
                tab_name = model.get_tab_name(prop_name)
                tab_mapping[tab_name].append((prop_name, prop_val))
            except Exception as e:
                print(e)
                print(node.name())

        if isinstance(node, AutoNode):
            # process parameters
            params = node.get_params()
            if params:
                node.update_parameters()
                for tab, params in params.items():
                    if tab not in self.get_tab_names():
                        self.add_tab(tab)
                    prop_window = self.get_tab_window(tab)
                    p = Parameter.create(name='params', type='group', children=params)
                    prop_window.setParameters(p, showTop=False)
                    p.sigTreeStateChanged.connect(self.value_change)

        # process NodeGraphQt properties.
        for tab in sorted(tab_mapping.keys()):
            if tab == 'Node':
                continue
            params = []
            for prop_name, value in tab_mapping[tab]:
                wid_type = model.get_widget_type(prop_name)
                if wid_type == 0:
                    continue

                parm_type = TYPE_MAP.get(wid_type)
                param = {'name': prop_name, 'type': parm_type, 'value': value}

                if prop_name in common_props.keys():
                    if 'items' in common_props[prop_name].keys():
                        _prop_name = '_' + prop_name + "_"
                        if node.has_property(_prop_name):
                            param['values'] = node.get_property(_prop_name)
                        else:
                            param['values'] = common_props[prop_name]['items']
                    if 'range' in common_props[prop_name].keys():
                        prop_range = common_props[prop_name]['range']
                        param['limits'] = tuple(prop_range)
                    if 'ext' in common_props[prop_name].keys():
                        param['ext'] = common_props[prop_name]['ext']
                    if 'funcs' in common_props[prop_name].keys():
                        param['funcs'] = common_props[prop_name]['funcs']
                        param['node'] = node

                if wid_type == NODE_PROP_QLABEL:
                    param['Read-only'] = True
                params.append(param)
            if params:
                p = Parameter.create(name='params', type='group', children=params)

                p.sigTreeStateChanged.connect(self.value_change)
                prop_window = self.add_tab(tab)
                prop_window.setParameters(p, showTop=False)

        # add "Node" tab properties.
        self.add_tab('Node')
        default_props = ['color', 'text_color', 'disabled', 'id']
        prop_window = self.get_tab_window('Node')
        params = []
        for prop_name in default_props:
            wid_type = model.get_widget_type(prop_name)
            parm_type = TYPE_MAP.get(wid_type)
            param = {'name': prop_name, 'type': parm_type, 'value': model.get_property(prop_name)}
            if wid_type == NODE_PROP_QLABEL:
                param['Read-only'] = True
            params.append(param)
        if params:
            p = Parameter.create(name='params', type='group', children=params)
            prop_window.setParameters(p, showTop=False)
            p.sigTreeStateChanged.connect(self.value_change)

        self.type_wgt.setText(model.get_property('type_'))
        self.update()

    def node_id(self):
        """
        Returns the node id linked to the widget.

        Returns:
            str: node id
        """
        return self.__node_id

    def add_widget(self, name, widget, tab='Properties'):
        """
        add new node property widget.

        Args:
            name (str): property name.
            widget (BaseProperty): property widget.
            tab (str): tab name.
        """
        if tab not in self._widgets.keys():
            tab = 'Properties'
        window = self.get_tab_window(tab)
        window.add_widget(name, widget)
        widget.value_changed.connect(self._on_property_changed)

    def add_tab(self, name):
        if name in self.get_tab_names():
            raise AssertionError('Tab name {} already taken!'.format(name))
        self.add_tab_window(name, NodeParamTreeWidget(self))
        self.get_tab().addTab(self.get_tab_window(name), name)
        return self.get_tab_window(name)

    def get_widget(self, name):
        """
        get property widget.

        Args:
            name (str): property name.

        Returns:
            QtWidgets.QWidget: property widget.
        """
        if name == 'name':
            return self.name_wgt
        for tab_name, prop_win in self.__tab_windows.items():
            widget = prop_win.get_widget(name)
            if widget:
                return widget

    def get_tab(self):
        return self.__tab

    def get_tab_window(self, name):
        return self.__tab_windows[name]

    def add_tab_window(self, tab_name, window):
        self.__tab_windows[tab_name] = window

    def get_tab_names(self):
        return self.__tab_windows.keys()


class NodePropBin(PropertiesBinWidget):
    def __init__(self, parent=None, node_graph=None):
        super(NodePropBin, self).__init__(parent, node_graph)

    def _on_changed(self, node_id, prop_name, prop_value):
        if not self._block_signal:
            self.property_changed.emit(node_id, prop_name, prop_value)

    def _on_closed(self, node_id):
        items = self._prop_list.findItems(node_id, QtCore.Qt.MatchExactly)
        [self._prop_list.removeRow(i.row()) for i in items]

    def reload(self):
        # TODO: reload node parameters
        pass

    def add_node(self, node):
        if self.limit() == 0 or self._lock:
            return

        itm_find = self._prop_list.findItems(node.id, QtCore.Qt.MatchExactly)

        if itm_find:
            if itm_find[0].row() == 0:
                try:
                    itm_find[0].setEnabled(node.graph.editable)
                except:
                    pass
                return
            self._prop_list.removeRow(itm_find[0].row())

        self._prop_list.insertRow(0)
        prop_widget = PropWidget(node=node)
        prop_widget.setEnabled(node.graph.editable)
        prop_widget.property_changed.connect(self._on_changed)
        prop_widget.property_closed.connect(self._on_closed)
        self._prop_list.setCellWidget(0, 0, prop_widget)

        item = QtWidgets.QTableWidgetItem(node.id)
        self._prop_list.setItem(0, 0, item)
        self._prop_list.selectRow(0)

        rows = self._prop_list.rowCount()
        if rows > self.limit():
            self._prop_list.removeRow(rows - 1)

        self.update()