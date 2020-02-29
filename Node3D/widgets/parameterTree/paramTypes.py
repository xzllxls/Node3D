from ...vendor.pyqtgraph.parametertree import parameterTypes as pTypes
from ...vendor.pyqtgraph.parametertree import Parameter, ParameterItem, registerParameterType
from ...vendor.NodeGraphQt.widgets.properties import PropFilePath, _valueEdit, \
    _valueSliderEdit, PropVector2, PropVector3, PropVector4, PropLabel, \
    PropColorPicker, PropTextEdit
from Qt import QtGui, QtWidgets, QtCore
from .curveEditor import CurveWidget


class FileParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        opts = self.param.opts
        w = PropFilePath()
        w.set_ext(opts['ext'])
        w.setMaximumHeight(30)
        w.sigChanged = w.value_changed
        w.value = w.get_value
        w.setValue = w.set_value
        return w


class FileParameter(Parameter):
    itemClass = FileParameterItem


registerParameterType('file', FileParameter, override=True)


class FloatEditParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        w = _valueEdit()
        w.setMaximumHeight(30)
        w.sigChanged = w.valueChanged
        return w


class FloatEditParameter(Parameter):
    itemClass = FloatEditParameterItem


registerParameterType('float_', FloatEditParameter, override=True)


class IntEditParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        w = _valueEdit()
        w.set_data_type(int)
        w.setMaximumHeight(30)
        w.sigChanged = w.valueChanged
        return w


class IntEditParameter(Parameter):
    itemClass = IntEditParameterItem


registerParameterType('int_', IntEditParameter, override=True)


class FloatSliderEditParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        w = _valueSliderEdit()
        opts = self.param.opts
        if 'limits' in opts:
            _min, _max = opts['limits']
            w.set_min(_min)
            w.set_max(_max)

        w.setMaximumHeight(30)
        w.sigChanged = w.valueChanged
        return w


class FloatSliderEditParameter(Parameter):
    itemClass = FloatSliderEditParameterItem


registerParameterType('float', FloatSliderEditParameter, override=True)


class IntSliderEditParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        w = _valueSliderEdit()
        w.set_data_type(int)
        opts = self.param.opts
        if 'limits' in opts:
            _min, _max = opts['limits']
            w.set_min(_min)
            w.set_max(_max)

        w.setMaximumHeight(30)
        w.sigChanged = w.valueChanged
        return w


class IntSliderEditParameter(Parameter):
    itemClass = IntSliderEditParameterItem


registerParameterType('int', IntSliderEditParameter, override=True)


class Vector3ParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        w = PropVector3()
        w.setMaximumHeight(30)
        w.sigChanged = w.value_changed
        w.value = w.get_value
        w.setValue = w.set_value
        return w


class Vector3Parameter(Parameter):
    itemClass = Vector3ParameterItem


registerParameterType('vector3', Vector3Parameter, override=True)


class Vector2ParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        w = PropVector2()
        w.setMaximumHeight(30)
        w.sigChanged = w.value_changed
        w.value = w.get_value
        w.setValue = w.set_value
        return w


class Vector2Parameter(Parameter):
    itemClass = Vector2ParameterItem


registerParameterType('vector2', Vector2Parameter, override=True)


class Vector4ParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        w = PropVector4()
        w.setMaximumHeight(30)
        w.sigChanged = w.value_changed
        w.value = w.get_value
        w.setValue = w.set_value
        return w


class Vector4Parameter(Parameter):
    itemClass = Vector4ParameterItem


registerParameterType('vector4', Vector4Parameter, override=True)


class Vector3iParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        w = PropVector3()
        w.set_data_type(int)
        w.setMaximumHeight(30)
        w.sigChanged = w.value_changed
        w.value = w.get_value
        w.setValue = w.set_value
        return w


class Vector3iParameter(Parameter):
    itemClass = Vector3iParameterItem


registerParameterType('vector3i', Vector3iParameter, override=True)


class Vector2iParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        w = PropVector2()
        w.set_data_type(int)
        w.setMaximumHeight(30)
        w.sigChanged = w.value_changed
        w.value = w.get_value
        w.setValue = w.set_value
        return w


class Vector2iParameter(Parameter):
    itemClass = Vector2iParameterItem


registerParameterType('vector2i', Vector2iParameter, override=True)


class Vector4iParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        w = PropVector4()
        w.set_data_type(int)
        w.setMaximumHeight(30)
        w.sigChanged = w.value_changed
        w.value = w.get_value
        w.setValue = w.set_value
        return w


class Vector4iParameter(Parameter):
    itemClass = Vector4iParameterItem


registerParameterType('vector4i', Vector4iParameter, override=True)




class ColorParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        w = PropColorPicker()
        w.setMaximumHeight(30)
        w.sigChanged = w.value_changed
        w.value = w.get_value
        w.setValue = w.set_value
        return w


class ColorParameter(Parameter):
    itemClass = ColorParameterItem


registerParameterType('color', ColorParameter, override=True)


class LabelParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        self.hideWidget = False
        super().__init__(param, depth)

    def makeWidget(self):
        w = PropLabel()
        w.setMaximumHeight(30)
        w.sigChanged = w.value_changed
        w.value = w.get_value
        w.setValue = w.set_value
        return w


class LabelParameter(Parameter):
    itemClass = LabelParameterItem


registerParameterType('label', LabelParameter, override=True)


class ColorRampParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        super(ColorRampParameterItem, self).__init__(param, depth)
        self.hideWidget = False
        self.subItem = QtWidgets.QTreeWidgetItem()
        self.addChild(self.subItem)

    def treeWidgetChanged(self):
        ParameterItem.treeWidgetChanged(self)
        if self.widget is not None:
            tree = self.treeWidget()
            if tree is None:
                return
            tree.setFirstItemColumnSpanned(self.subItem, True)
            tree.setItemWidget(self.subItem, 0, self.widget)
            self.selected(False)

    def makeWidget(self):
        from ...vendor.pyqtgraph.widgets.GradientWidget import GradientWidget
        ramp_widget = GradientWidget(orientation='bottom', height=40)
        ramp_widget.setMaximumHeight(65)
        self.ramp = ramp_widget.item
        self.hideWidget = False
        self.combox = QtWidgets.QComboBox()
        items = ['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous', 'next']
        self.combox.addItems(items)
        self.combox.currentIndexChanged.connect(self._on_kind_change)

        wid = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        wid.setLayout(layout)
        layout.addWidget(ramp_widget)
        layout.addWidget(self.combox)
        wid.sigChanged = ramp_widget.sigGradientChangeFinished
        wid.sigChanging = ramp_widget.sigGradientChanged
        wid.value = self.ramp.value
        wid.setValue = self.setValue

        return wid

    def _on_kind_change(self):
        self.ramp.set_kind(self.combox.currentText())

    def setValue(self, value):
        """
        :param value: [ np.ndarray: colors, np.ndarray: keys, str:kind ]
        """
        if value is None:
            return
        idx = self.combox.findText(value[2], QtCore.Qt.MatchExactly)
        self.combox.setCurrentIndex(idx)
        self.ramp.setValue(value)


class ColorRampParameter(Parameter):
    itemClass = ColorRampParameterItem


registerParameterType('colorRamp', ColorRampParameter, override=True)


class CurveRampParameterItem(ColorRampParameterItem):
    def __init__(self, param, depth):
        super(CurveRampParameterItem, self).__init__(param, depth)

    def makeWidget(self):
        self.ramp = CurveWidget()
        self.ramp.setMaximumHeight(500)
        self.hideWidget = False
        self.combox = QtWidgets.QComboBox()

        items = ['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous', 'next']
        self.combox.addItems(items)
        self.combox.currentIndexChanged.connect(self._on_kind_change)
        self.combox.setCurrentIndex(4)

        wid = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        wid.setLayout(layout)
        layout.addWidget(self.ramp)
        layout.addWidget(self.combox)
        wid.sigChanged = self.ramp.valueChangeFinished
        wid.sigChanging = self.ramp.valueChanged
        wid.value = self.ramp.value
        wid.setValue = self.setValue
        wid.setMinimumHeight(200)
        return wid

    def setValue(self, value):
        """
        :param value: [ np.ndarray: 2d pos , str: kind ]
        """
        if value is None:
            return
        idx = self.combox.findText(value[1], QtCore.Qt.MatchExactly)
        self.combox.setCurrentIndex(idx)
        self.ramp.setValue(value)


class CurveRampParameter(Parameter):
    itemClass = CurveRampParameterItem


registerParameterType('curveRamp', CurveRampParameter, override=True)


class SpacerParameterItem(ParameterItem):
    def __init__(self, param, depth):
        ParameterItem.__init__(self, param, depth)
        self._widget = QtWidgets.QWidget()
        opts = param.opts
        color = opts.get('color', None)
        if color is None:
            color = (0.15, 0.15, 0.15)
        height = opts.get('height', None)
        if height is None:
            height = 2

        c = [int(max(min(i*255, 255), 0)) for i in color]
        self._widget.setStyleSheet(
            '''QWidget {{background-color: rgb({0}, {1}, {2});}}'''.format(*c))
        self._widget.setFixedHeight(height)
        self.setText(0, '')

    def treeWidgetChanged(self):
        ParameterItem.treeWidgetChanged(self)
        tree = self.treeWidget()
        if tree is None:
            return

        tree.setFirstItemColumnSpanned(self, True)  # one line just show one widget
        tree.setItemWidget(self, 0, self._widget)


class SpacerParameter(Parameter):
    itemClass = SpacerParameterItem


registerParameterType('spacer', SpacerParameter, override=True)


class TextParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        super(TextParameterItem, self).__init__( param, depth)
        self.hideWidget = False
        self.subItem = QtWidgets.QTreeWidgetItem()
        self.addChild(self.subItem)

    def treeWidgetChanged(self):
        # (WidgetParameter should just natively support this style)
        # WidgetParameterItem.treeWidgetChanged(self)
        self.treeWidget().setFirstItemColumnSpanned(self.subItem, True)
        self.treeWidget().setItemWidget(self.subItem, 0, self.textBox)

        # for now, these are copied from ParameterItem.treeWidgetChanged
        self.setHidden(not self.param.opts.get('visible', True))
        self.setExpanded(self.param.opts.get('expanded', True))

    def makeWidget(self):
        self.textBox = PropTextEdit()
        self.textBox.setMaximumHeight(500)
        self.textBox.setReadOnly(self.param.opts.get('readonly', False))
        self.textBox.value = self.textBox.get_value
        self.textBox.setValue = self.textBox.set_value
        self.textBox.sigChanged = self.textBox.value_changed
        return self.textBox


class TextParameter(Parameter):
    itemClass = TextParameterItem


registerParameterType('text', TextParameter, override=True)


class ComboBox(QtWidgets.QComboBox):
    show_popup = QtCore.Signal()
    editing_finished = QtCore.Signal(object)

    def __init__(self):
        super(ComboBox, self).__init__()
        self.currentIndexChanged.connect(self.on_value_changed)

    def showPopup(self):
        self.show_popup.emit()
        super(ComboBox, self).showPopup()

    def on_value_changed(self):
        self.editing_finished.emit(self.currentText())

    def focusOutEvent(self, event):
        super(ComboBox, self).focusOutEvent(event)
        self.editing_finished.emit(self.currentText())


class ListTextParameterItem(pTypes.WidgetParameterItem):
    def __init__(self, param, depth):
        super(ListTextParameterItem, self).__init__(param, depth)

    def makeWidget(self):
        opts = self.param.opts
        w = ComboBox()
        w.setEditable(True)
        w.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        w.setStyleSheet(""" QComboBox{background-color: rgb(20,20,20)}
                            QComboBox::drop-down{
                            background-color: rgb(55,55,55); 
                            }""")
        w.sigChanged = w.editing_finished
        w.value = self.value
        w.setValue = self.setValue
        self.widget = w
        limits = opts.get('limits', None)
        if limits:
            self.limitsChanged(limits)

        return w

    def value(self):
        return self.widget.currentText()

    def setValue(self, val):
        if type(val) is list:
            self.limitsChanged(val)
            return
        if type(val) is int:
            self.widget.setCurrentIndex(val)
            return
        self.widget.setCurrentText(val)

    def limitsChanged(self, limits):
        old = self.value()
        self.widget.clear()
        self.widget.addItems(limits)
        self.widget.setCurrentText(old)


class ListTextParameter(Parameter):
    itemClass = ListTextParameterItem


registerParameterType('listText', ListTextParameter, override=True)