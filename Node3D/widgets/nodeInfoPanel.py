from Qt import QtWidgets, QtCore, QtGui, QtCompat
from ..base.node.geometry_node import GeometryNode
import os

ATTRIBUTE_DATA_COLOR = {"float": '<font color="yellow">{}</font>({})',
                        "vector2": '<font color="MediumSpringGreen">{}</font>({})',
                        "vector3": '<font color="MediumSpringGreen">{}</font>({})',
                        "vector4": '<font color="MediumSpringGreen">{}</font>({})',
                        "list": '<font color="MediumSpringGreen">{}</font>({})',
                        "tuple": '<font color="MediumSpringGreen">{}</font>({})',
                        "matrix3": '<font color="MediumSpringGreen">{}</font>({})',
                        "matrix4": '<font color="MediumSpringGreen">{}</font>({})',
                        "int": '<font color="Orange">{}</font>({})',
                        "bool": '<font color="Orchid">{}</font>({})',
                        "str": '<font color="lightpink">{}</font>({})',
                        "group": '<font color="DeepSkyBlue">{}</font>({})',
                        "custom": '<font>{}</font>',
                        "none": '<font>{}</font>'}

MESSAGE_COLOR = {"none": '<font color="lime">{}</font>',
                 "warning": '<font color="orange">{}</font>',
                 "error": '<font color="red">{}</font>'}


class NodeInfoPanel(QtWidgets.QWidget):
    # This panel shows information of the selected node.

    def __init__(self):
        super().__init__()
        self.workingPath = os.path.dirname(__file__).replace("\\", "/")
        self.ui = QtCompat.loadUi(self.workingPath + "/uiFiles/nodeInfoPanel.ui", self)
        self.setWindowTitle("Node Information")

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.width = 400
        self.height = 600
        self.resize(self.width, self.height)
        self.nodeInfoWidget.setFixedHeight(100)

        self.screenSize = QtWidgets.QDesktopWidget().screenGeometry()
        self.screenWidth = self.screenSize.width()
        self.screenHeight = self.screenSize.height()

        self.attribTextEdits = {"vertex": self.ui.vertexAttrText,
                                "edge": self.ui.edgeAttrText,
                                "face": self.ui.faceAttrText,
                                "detail": self.ui.detailAttrText}

        self.attribLabels = {"vertex": self.ui.label_23,
                             "edge": self.ui.label,
                             "face": self.ui.label_3,
                             "detail": self.ui.label_6}

        self.node = None
        self._always_show = False

    @property
    def always_show(self):
        return self._always_show

    @always_show.setter
    def always_show(self, state):
        self._always_show = state
        if state:
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def clear(self, clear_all=True):
        # clear node info
        if clear_all:
            self.ui.nodeNameLabel.setText("")
            self.ui.nodeTypeLabel.setText("")
            self.ui.cookTimeLabel.setText("")
        self.ui.vertexCntLabel.setText("")
        self.ui.edgeCntLabel.setText("")
        self.ui.faceCntLabel.setText("")

        [i.setText('') for i in [self.ui.bboxCenterXLabel, self.ui.bboxCenterYLabel, self.ui.bboxCenterZLabel]]
        [i.setText('') for i in [self.ui.bboxMinXLabel, self.ui.bboxMinYLabel, self.ui.bboxMinZLabel]]
        [i.setText('') for i in [self.ui.bboxMaxXLabel, self.ui.bboxMaxYLabel, self.ui.bboxMaxZLabel]]
        [i.setText('') for i in [self.ui.bboxSizeXLabel, self.ui.bboxSizeYLabel, self.ui.bboxSizeZLabel]]
        [i.setText('') for i in self.attribTextEdits.values()]

    def hide_elements(self):
        [i.setVisible(False) for i in self.attribTextEdits.values()]
        [i.setVisible(False) for i in self.attribLabels.values()]
        self.ui.nodeErrorText.setVisible(False)
        self.ui.label_9.setVisible(False)

    def setNode(self, node):
        # node is the specific type of node, eg: bunny node
        # collect node related info

        nodeName = node.name()
        nodeType = node.type_
        nodeCookTime = node.getCookTime()
        nodeMessage, nodeMessageLevel = node.get_message()

        self.hide_elements()
        self.ui.nodeNameLabel.setText(nodeName)
        self.ui.nodeTypeLabel.setText(nodeType)
        self.ui.cookTimeLabel.setText(str(nodeCookTime))

        if nodeMessageLevel > 0:
            if nodeMessageLevel == 1:
                # warning
                messageColor = MESSAGE_COLOR["warning"]
            elif nodeMessageLevel == 2:
                # error
                messageColor = MESSAGE_COLOR["error"]
            else:
                # other
                messageColor = MESSAGE_COLOR["none"]

            self.ui.label_9.setVisible(True)
            self.ui.nodeErrorText.setVisible(True)
            self.ui.nodeErrorText.setHtml(messageColor.format(nodeMessage))
        else:
            self.ui.nodeErrorText.setText("")

        # collect geo related info
        if isinstance(node, GeometryNode) and node.geo is not None:
            vertexCount = node.geo.getNumVertexes()
            edgeCount = node.geo.getNumEdges()
            faceCount = node.geo.getNumFaces()

            if vertexCount > 0:
                # if mesh has actual geo data
                self.ui.vertexCntLabel.setText(str(vertexCount))
                self.ui.edgeCntLabel.setText(str(edgeCount))
                self.ui.faceCntLabel.setText(str(faceCount))

                # set bbox related info to labels
                bboxMin, bboxMax, bboxCenter = node.geo.get_bbox_info()
                bboxSize = [abs(bboxMin[0] - bboxMax[0]),
                            abs(bboxMin[1] - bboxMax[1]),
                            abs(bboxMin[2] - bboxMax[2])]

                bboxCenterLabels = [self.ui.bboxCenterXLabel, self.ui.bboxCenterYLabel, self.ui.bboxCenterZLabel]
                [label.setText('%.3f' % (bboxCenter[i])) for i, label in enumerate(bboxCenterLabels)]

                bboxMinLabels = [self.ui.bboxMinXLabel, self.ui.bboxMinYLabel, self.ui.bboxMinZLabel]
                [label.setText('%.3f' % (bboxMin[i])) for i, label in enumerate(bboxMinLabels)]

                bboxMaxLabels = [self.ui.bboxMaxXLabel, self.ui.bboxMaxYLabel, self.ui.bboxMaxZLabel]
                [label.setText('%.3f' % (bboxMax[i])) for i, label in enumerate(bboxMaxLabels)]

                bboxSizeLabels = [self.ui.bboxSizeXLabel, self.ui.bboxSizeYLabel, self.ui.bboxSizeZLabel]
                [label.setText('%.3f' % (bboxSize[i])) for i, label in enumerate(bboxSizeLabels)]

                # collect attribute related info
                attribData = node.geo.getAttribNames(with_group=True)

                for attribClass, attrNames in attribData.items():
                    # vertex, edge, face, detail
                    if not attrNames:
                        continue
                    else:
                        self.attribLabels[attribClass].setVisible(True)
                        self.attribTextEdits[attribClass].setVisible(True)

                    attrDisplay = []
                    for attr in attrNames:
                        if ":" in attr:
                            attr = attr[2:]
                            attrType = "group"
                        else:
                            attrType = node.geo.getAttribType(attribClass, attr)
                        if attrType not in ATTRIBUTE_DATA_COLOR.keys():
                            attrType = "none"
                        attrDisplay.append(ATTRIBUTE_DATA_COLOR[attrType].format(attr, attrType))

                    self.attribTextEdits[attribClass].setHtml("; ".join(attrDisplay))
        else:
            self.clear(False)

    def refresh(self, node=None, always_show=False):
        isVisible = self.isVisible()
        if node is not None:
            self.node = node
            self.setNode(node)
        elif self.node is not None:
            self.setNode(self.node)
        else:
            self.clear()

        if self._always_show and isVisible:
            return

        self.always_show = always_show

        if not isVisible or self._always_show:
            self.show()
        if not isVisible:
            self.adjustWindowPos()

    def keyPressEvent(self, event):
        # use "S" key to make panel always show
        if not self._always_show and event.key() == QtCore.Qt.Key_S:
            self.refresh(None, True)
        super().keyPressEvent(event)

    def close(self):
        # if the panel is in always show state , don't auto close it
        if self._always_show:
            return
        self.always_show = False
        self.node = None
        super().close()

    def adjustWindowPos(self):
        # make sure window is inside the screen
        margin = 20
        targetPos = QtGui.QCursor.pos() + QtCore.QPoint(margin, -self.height * 0.5)

        if targetPos.x() + self.width > self.screenWidth:
            # if further to the right
            targetPos += QtCore.QPoint(-self.width, 0)
            targetPos += QtCore.QPoint(-margin * 2, 0)

        if targetPos.y() < 0:
            # if higher than the top screen
            targetPos += QtCore.QPoint(0, abs(targetPos.y()) + margin)

        if targetPos.y() + self.height > self.screenHeight:
            # if lower than bottom screen
            targetPos += QtCore.QPoint(0, -abs(targetPos.y() + self.height - self.screenHeight) - margin)

        self.move(targetPos)
