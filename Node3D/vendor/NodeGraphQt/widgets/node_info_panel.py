from .. import QtWidgets, QtCore, QtGui, QtCompat
from ....base.node.geometry_node import GeometryNode
import os


class NodeInfoPanel(QtWidgets.QWidget):
    # This panel shows information of the selected node.

    def __init__(self):
        super().__init__()
        self.workingPath = os.path.dirname(__file__)
        self.ui = QtCompat.loadUi(self.workingPath + "/node_info_panel.ui", self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.width = 400
        self.height = 600
        self.resize(self.width, self.height)

        self.screenSize = QtWidgets.QDesktopWidget().screenGeometry()
        self.screenWidth = self.screenSize.width()
        self.screenHeight = self.screenSize.height()

        self.attribTextEdits = {"vertex": self.ui.vertexAttrText,
                           "edge": self.ui.edgeAttrText,
                           "face": self.ui.faceAttrText,
                           "detail": self.ui.detailAttrText}

        self.attribColor = {"float": '<font color="yellow">',
                       "vector": '<font color="lime">',
                       "int": '<font color="teal">',
                       "bool": '<font color="purple">',
                       "str": '<font color="lightpink">',
                       "none": '<font>'}

        self.messageColor = {"none": '<font color="lime">',
                             "warning": '<font color="orange">',
                             "error": '<font color="red">'}

    def refresh(self, node):
        # node is the specific type of node, eg: bunny node
        # collect node related info
        nodeName = node.name()
        nodeType = node.type_
        nodeCookTime = node.getCookTime()
        nodeMessage, nodeMessageLevel = node.get_message()

        self.ui.nodeNameLabel.setText(nodeName)
        self.ui.nodeTypeLabel.setText(nodeType)
        self.ui.cookTimeLabel.setText(str(nodeCookTime))

        errorMessage = ""
        if nodeMessageLevel == 0:
            # no message
            errorMessage += self.messageColor["none"] + "Well Cooked"
        elif nodeMessageLevel == 1:
            # warning
            errorMessage += self.messageColor["warning"] + nodeMessage
        elif nodeMessageLevel == 2:
            # error
            errorMessage = self.messageColor["error"] + nodeMessage

        errorMessage += '</font>'
        self.ui.nodeErrorText.setHtml(errorMessage)

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
                bboxCenter = node.geo.bbox_center
                bboxMin = node.geo.bbox_min
                bboxMax = node.geo.bbox_max
                bboxSize = [abs(bboxMin[0] - bboxMax[0]),
                            abs(bboxMin[1] - bboxMax[1]),
                            abs(bboxMin[2] - bboxMax[2])]

                bboxCenterLabels = [self.ui.bboxCenterXLabel, self.ui.bboxCenterYLabel, self.ui.bboxCenterZLabel]
                [bboxCenterLabels[i].setText('%.3f' % (bboxCenter[i])) for i in range(len(bboxCenterLabels))]

                bboxMinLabels = [self.ui.bboxMinXLabel, self.ui.bboxMinYLabel, self.ui.bboxMinZLabel]
                [bboxMinLabels[i].setText('%.3f' % (bboxMin[i])) for i in range(len(bboxMinLabels))]

                bboxMaxLabels = [self.ui.bboxMaxXLabel, self.ui.bboxMaxYLabel, self.ui.bboxMaxZLabel]
                [bboxMaxLabels[i].setText('%.3f' % (bboxMax[i])) for i in range(len(bboxMaxLabels))]

                bboxSizeLabels = [self.ui.bboxSizeXLabel, self.ui.bboxSizeYLabel, self.ui.bboxSizeZLabel]
                [bboxSizeLabels[i].setText('%.3f' % (bboxSize[i])) for i in range(len(bboxSizeLabels))]

                # collect attribute related info
                attribData = node.geo.getAttribNames()

                for attrLevel in attribData:
                    # vertex, edge, face, detail
                    attrDisplayStr = ""
                    for attr in attribData[attrLevel]:
                        if attrDisplayStr != "":
                            attrDisplayStr += ","

                        attrType = node.geo.getAttribType(attrLevel, attr)
                        attrDisplayStr += self.attribColor[attrType]
                        attrDisplayStr = attrDisplayStr + attr
                        attrDisplayStr += "</font>"
                        attrDisplayStr += "(" + attrType + ")"


                    self.attribTextEdits[attrLevel].setHtml(attrDisplayStr)

        self.adjustWindowPos()

        self.show()

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
