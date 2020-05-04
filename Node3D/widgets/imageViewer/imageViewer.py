from PySide2 import QtCore, QtWidgets
import numpy as np
from .imageGraphics import ImageGraphicsView
from ...vendor.NodeGraphQt.widgets.properties import PropFloat
from ...base.node import ImageNode

WITH_CUDA = False
try:
    import cupy

    WITH_CUDA = True
except:
    pass


class ImageViewer(QtWidgets.QWidget):
    def __init__(self):
        super(ImageViewer, self).__init__()
        self.setWindowTitle("Image Viewer")
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(hbox)

        # channelLabel = QtWidgets.QLabel()
        # channelLabel.setText("Channels")
        # channelLabel.setAlignment(QtCore.Qt.AlignLeft)
        # channelLabel.setStyleSheet("QLabel{background-color:transparent;margin:0px;padding:0px;"
        #                            "font-size:15px;border-width:0px;max-width:100px}")

        self.channelCombobox = QtWidgets.QComboBox()
        self.channelCombobox.addItems(['rgb'])
        self.channelCombobox.currentTextChanged.connect(self.on_channel_changed)
        self.channelCombobox.setStyleSheet("QComboBox{{max-width:{0}px;min-width:{0}px}}".format(45))

        gammaLabel = QtWidgets.QLabel()
        gammaLabel.setText("Gamma")
        gammaLabel.setAlignment(QtCore.Qt.AlignLeft)
        gammaLabel.setStyleSheet("QLabel{background-color:transparent;margin:0px;padding:0px;"
                                 "font-size:15px;border-width:0px;max-width:100px}")
        self.gamma = PropFloat()
        self.gamma.set_value(1.0)
        self.gamma.value_changed.connect(self.on_postfx_changed)

        multiplyLabel = QtWidgets.QLabel()
        multiplyLabel.setText("Multiply")
        multiplyLabel.setAlignment(QtCore.Qt.AlignLeft)
        multiplyLabel.setStyleSheet("QLabel{background-color:transparent;margin:0px;padding:0px;"
                                    "font-size:15px;border-width:0px;max-width:100px}")
        self.multiply = PropFloat()
        self.multiply.set_value(1.0)
        self.multiply.value_changed.connect(self.on_postfx_changed)

        # hbox.addWidget(channelLabel)
        hbox.addWidget(self.channelCombobox)
        hbox.addWidget(multiplyLabel)
        hbox.addWidget(self.multiply)
        hbox.addWidget(gammaLabel)
        hbox.addWidget(self.gamma)

        self.viewer = ImageGraphicsView()
        self.viewer.position_changed.connect(self.on_position_changed)
        self.viewer.color_changed.connect(self.on_color_changed)
        vbox.addWidget(self.viewer)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(hbox)

        self.positionLabel = QtWidgets.QLabel()
        self.positionLabel.setText("X:0,Y:0")
        self.positionLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.positionLabel.setStyleSheet("QLabel{background-color:transparent;margin:0px;padding:0px;"
                                         "font-size:14px;border-width:0px;max-width:100px}")

        self.sizeLabel = QtWidgets.QLabel()
        self.sizeLabel.setText("Width:0,Height:0")
        self.sizeLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.sizeLabel.setStyleSheet("QLabel{background-color:transparent;margin:0px;padding:0px;"
                                     "font-size:14px;border-width:0px;max-width:200px}")

        self.RLabel = QtWidgets.QLabel()
        self.RLabel.setText("R:0.000")
        self.RLabel.setAlignment(QtCore.Qt.AlignRight)
        self.RLabel.setStyleSheet("QLabel{background-color:transparent;margin:0px;padding:0px;"
                                  "font-size:14px;color:red;border-width:0px;max-width:70px}")

        self.GLabel = QtWidgets.QLabel()
        self.GLabel.setText("G:0.000")
        self.GLabel.setAlignment(QtCore.Qt.AlignRight)
        self.GLabel.setStyleSheet("QLabel{background-color:transparent;margin:0px;padding:0px;"
                                  "font-size:14px;color:green;border-width:0px;max-width:70px}")

        self.BLabel = QtWidgets.QLabel()
        self.BLabel.setText("B:0.000")
        self.BLabel.setAlignment(QtCore.Qt.AlignRight)
        self.BLabel.setStyleSheet("QLabel{background-color:transparent;margin:0px;padding:0px;"
                                  "font-size:14px;color:blue;border-width:0px;max-width:70px}")

        self.ALabel = QtWidgets.QLabel()
        self.ALabel.setText("A:0.000")
        self.ALabel.setAlignment(QtCore.Qt.AlignRight)
        self.ALabel.setStyleSheet("QLabel{background-color:transparent;margin:0px;padding:0px;"
                                  "font-size:14px;color:white;border-width:0px;max-width:70px}")

        hbox.addWidget(self.positionLabel)
        hbox.addWidget(self.sizeLabel)
        hbox.addStretch()
        hbox.addWidget(self.RLabel, QtCore.Qt.AlignRight)
        hbox.addWidget(self.GLabel)
        hbox.addWidget(self.BLabel)
        hbox.addWidget(self.ALabel)
        self.node = None
        self.block_signal = False

    def set_image(self, image):
        gamma = self.gamma.get_value()
        if gamma != 1.0 or self.multiply.get_value() != 1.0:
            self.viewer.image_data = image
            self.on_postfx_changed()
        else:
            self.viewer.set_image(image)
        w = image.shape[0]
        h = image.shape[1]
        self.sizeLabel.setText("Width:{0},Height:{1}".format(w, h))

    def on_position_changed(self, x, y):
        self.positionLabel.setText("X:{0},Y:{1}".format(x, y))

    def on_color_changed(self, color):
        dim = self.viewer.image_data.shape[-1]
        if len(self.viewer.image_data) == 2:
            dim = 1
        if dim == 1:
            self.RLabel.setText("R:%.4f" % color)
            self.GLabel.setText("G:0.000")
            self.BLabel.setText("B:0.000")
            self.ALabel.setText("A:1.000")
        elif dim == 3:
            self.RLabel.setText("R:%.4f" % color[0])
            self.GLabel.setText("G:%.4f" % color[1])
            self.BLabel.setText("B:%.4f" % color[2])
            self.ALabel.setText("A:1.000")
        elif dim == 4:
            self.RLabel.setText("R:%.4f" % color[0])
            self.GLabel.setText("G:%.4f" % color[1])
            self.BLabel.setText("B:%.4f" % color[2])
            self.ALabel.setText("A:%.4f" % color[3])

    def on_postfx_changed(self):
        if self.viewer.image_data is not None:
            gamma = self.gamma.get_value()
            multiply = self.multiply.get_value()
            if gamma <= 0.000001 or multiply <= 0.000001:
                new_data = np.zeros(self.viewer.image_data.shape, dtype=self.viewer.image_data.dtype)
            else:
                if WITH_CUDA:
                    cu_image = cupy.asarray(self.viewer.image_data)
                    if multiply > 0.000001:
                        cu_image *= multiply
                    if gamma > 0.000001:
                        cu_image = cupy.asnumpy(cupy.power(cu_image, 1.0 / gamma))
                    new_data = cupy.asnumpy(cu_image)
                else:
                    new_data = self.viewer.image_data
                    if multiply > 0.000001:
                        new_data = new_data * multiply
                    if gamma > 0.000001:
                        new_data = np.power(new_data, 1.0 / gamma)
            self.viewer.set_image(new_data, False)

    def set_node(self, node):
        if not isinstance(node, ImageNode):
            return
        if self.node:
            if node.id != self.node.id:
                self.node.cooked.disconnect(self.update_data)
                self.node = node
            else:
                return
        else:
            self.node = node
        self.update_data()
        self.node.cooked.connect(self.update_data)

    def set_channel_items(self, items):
        num = 0
        for item in items:
            num = max(0, len(item))
        self.channelCombobox.addItems(items)
        self.channelCombobox.setStyleSheet("QComboBox{{max-width:{0}px;min-width:{0}px}}".format(num * 10))

    def update_data(self):
        text = self.channelCombobox.currentText()
        self.channelCombobox.clear()
        if self.node is None:
            return
        image = self.node.image
        if image is None:
            return
        self.block_signal = True
        if isinstance(image, dict):
            self.set_channel_items(list(image.keys()))
            if text in image:
                self.channelCombobox.setCurrentText(text)
            else:
                text = self.channelCombobox.currentText()
            self.set_image(image[text])
        else:
            self.set_image(image)
            if len(image.shape) == 2:
                self.set_channel_items(['grey'])
            elif image.shape[-1] == 3:
                self.set_channel_items(['rgb'])
            elif image.shape[-1] == 4:
                self.set_channel_items(['rgba'])
        self.block_signal = False

    def on_channel_changed(self, text):
        if self.block_signal:
            return
        if self.node is None:
            return
        image = self.node.image
        if image is None:
            return
        if text in image:
            self.set_image(image[text])
