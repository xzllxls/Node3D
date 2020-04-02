from Qt import QtWidgets, QtCore, QtGui
from ..vendor.NodeGraphQt.widgets.properties import _valueSliderEdit, _valueEdit
from .styles import STYLE_BUTTON
import os


class TimeLine(QtWidgets.QWidget):
    frameChanged = QtCore.Signal(int)

    def __init__(self):
        super(TimeLine, self).__init__()
        self.setMaximumHeight(30)
        self.setStyleSheet(STYLE_BUTTON)
        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        # hbox.setSpacing(0)
        self.setLayout(hbox)

        btn1 = QtWidgets.QPushButton("<<")
        btn2 = QtWidgets.QPushButton("<")
        self.btn3 = QtWidgets.QPushButton("")

        icon = os.path.abspath(os.path.dirname(__file__)) + "/icons/pause.png"
        self.btn3.setIcon(QtGui.QIcon(icon))

        btn4 = QtWidgets.QPushButton(">")
        btn5 = QtWidgets.QPushButton(">>")

        hbox.addWidget(btn1)
        hbox.addWidget(btn2)
        hbox.addWidget(self.btn3)
        hbox.addWidget(btn4)
        hbox.addWidget(btn5)

        btn1.setStyleSheet(STYLE_BUTTON)
        btn2.setStyleSheet(STYLE_BUTTON)
        self.btn3.setStyleSheet(STYLE_BUTTON)
        btn4.setStyleSheet(STYLE_BUTTON)
        btn5.setStyleSheet(STYLE_BUTTON)

        self.slider = _valueSliderEdit()
        self.slider.set_data_type(int)
        hbox.addWidget(self.slider)

        self.startValue = _valueEdit()
        self.startValue.set_data_type(int)
        self.startValue.setMaximumWidth(50)
        self.endValue = _valueEdit()
        self.endValue.set_data_type(int)
        self.endValue.setMaximumWidth(50)
        hbox.addWidget(self.startValue)
        hbox.addWidget(self.endValue)

        self.timeline = QtCore.QTimeLine()
        self.timeline.setCurveShape(QtCore.QTimeLine.LinearCurve)
        self.setFrameRange(0, 100)
        self.startValue.setValue(0)
        self.endValue.setValue(100)
        self.fps = 25

        btn1.clicked.connect(self.gotoStart)
        btn2.clicked.connect(lambda: self.start(False))
        self.btn3.clicked.connect(self.stop)
        btn4.clicked.connect(lambda: self.start(True))
        btn5.clicked.connect(self.gotoEnd)

        self.startValue.valueChanged.connect(lambda: self.setFrameRange(start=self.startValue.value()))
        self.endValue.valueChanged.connect(lambda: self.setFrameRange(end=self.endValue.value()))
        self.timeline.valueChanged.connect(self.onFrameChanged)
        self.slider.valueChanged.connect(lambda: self.frameChanged.emit(self.slider.value()))

    def onFrameChanged(self):
        self.slider.setValue(self.timeline.currentFrame())

    def setFrameRange(self, start=None, end=None):
        _value = self.slider.value()
        if start is not None:
            self.timeline.setStartFrame(start)
            self.slider.set_min(start)

        if end is not None:
            self.timeline.setEndFrame(end)
            self.slider.set_max(end)
        self.slider.setValue(_value)

    def start(self, forward=True):
        if self.timeline.state() == QtCore.QTimeLine.Running:
            return
        if forward:
            self.setForward()
            self.timeline.setFrameRange(self.slider.value(), self.endValue.value())
        else:
            self.setBackward()
            self.timeline.setFrameRange(self.startValue.value(), self.slider.value())
        self.updateTime()
        self.timeline.start()

    def stop(self):
        self.timeline.stop()

    def gotoStart(self):
        self.slider.setValue(self.startValue.value())

    def gotoEnd(self):
        self.slider.setValue(self.endValue.value())

    def getFrame(self):
        return self.slider.value()

    def getTime(self):
        return float(self.slider.value())/self.fps

    def setForward(self):
        self.timeline.setDirection(QtCore.QTimeLine.Forward)

    def setBackward(self):
        self.timeline.setDirection(QtCore.QTimeLine.Backward)

    def updateTime(self):
        delat = float(self.timeline.endFrame() - self.timeline.startFrame())
        time = delat / self.fps
        self.timeline.setDuration(int(time * 1000))

    def setFps(self, fps):
        self.fps = fps
        self.updateTime()
