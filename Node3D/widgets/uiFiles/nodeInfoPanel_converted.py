# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'nodeInfoPanel.ui'
##
## Created by: Qt User Interface Compiler version 5.14.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *


class Ui_Form(object):
    def setupUi(self, Form):
        if Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(327, 551)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, -1, -1, -1)
        self.nodeInfoWidget = QWidget(Form)
        self.nodeInfoWidget.setObjectName(u"nodeInfoWidget")
        self.nodeInfoWidget.setStyleSheet(u"background-color: rgb(53, 76, 127);")
        self.verticalLayout_3 = QVBoxLayout(self.nodeInfoWidget)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SetMinimumSize)
        self.verticalLayout_3.setContentsMargins(-1, -1, -1, 10)
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setSpacing(6)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, -1, -1, -1)
        self.nodeNameLabel = QLabel(self.nodeInfoWidget)
        self.nodeNameLabel.setObjectName(u"nodeNameLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nodeNameLabel.sizePolicy().hasHeightForWidth())
        self.nodeNameLabel.setSizePolicy(sizePolicy)
        self.nodeNameLabel.setSizeIncrement(QSize(0, 0))
        font = QFont()
        font.setFamily(u"Segoe UI")
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.nodeNameLabel.setFont(font)
        self.nodeNameLabel.setScaledContents(False)
        self.nodeNameLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.nodeNameLabel.setWordWrap(False)
        self.nodeNameLabel.setMargin(0)
        self.nodeNameLabel.setIndent(-1)

        self.verticalLayout_7.addWidget(self.nodeNameLabel)

        self.nodeTypeLabel = QLabel(self.nodeInfoWidget)
        self.nodeTypeLabel.setObjectName(u"nodeTypeLabel")
        sizePolicy.setHeightForWidth(self.nodeTypeLabel.sizePolicy().hasHeightForWidth())
        self.nodeTypeLabel.setSizePolicy(sizePolicy)
        font1 = QFont()
        font1.setFamily(u"Segoe UI")
        font1.setPointSize(9)
        self.nodeTypeLabel.setFont(font1)
        self.nodeTypeLabel.setScaledContents(False)
        self.nodeTypeLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_7.addWidget(self.nodeTypeLabel)


        self.verticalLayout_3.addLayout(self.verticalLayout_7)


        self.verticalLayout.addWidget(self.nodeInfoWidget)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout_2.setContentsMargins(10, -1, 10, -1)
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.vertexLabel = QLabel(Form)
        self.vertexLabel.setObjectName(u"vertexLabel")
        self.vertexLabel.setStyleSheet(u"color: rgb(0, 255, 127);")

        self.gridLayout_5.addWidget(self.vertexLabel, 0, 0, 1, 1)

        self.edgeCntLabel = QLabel(Form)
        self.edgeCntLabel.setObjectName(u"edgeCntLabel")
        self.edgeCntLabel.setStyleSheet(u"color: rgb(255, 168, 17);")

        self.gridLayout_5.addWidget(self.edgeCntLabel, 1, 1, 1, 1)

        self.faceLabel = QLabel(Form)
        self.faceLabel.setObjectName(u"faceLabel")
        self.faceLabel.setStyleSheet(u"color: rgb(255, 65, 240);")

        self.gridLayout_5.addWidget(self.faceLabel, 2, 0, 1, 1)

        self.vertexCntLabel = QLabel(Form)
        self.vertexCntLabel.setObjectName(u"vertexCntLabel")
        self.vertexCntLabel.setStyleSheet(u"color: rgb(0, 255, 127);")

        self.gridLayout_5.addWidget(self.vertexCntLabel, 0, 1, 1, 1)

        self.faceCntLabel = QLabel(Form)
        self.faceCntLabel.setObjectName(u"faceCntLabel")
        self.faceCntLabel.setStyleSheet(u"color: rgb(255, 65, 240);")

        self.gridLayout_5.addWidget(self.faceCntLabel, 2, 1, 1, 1)

        self.edgeLabel = QLabel(Form)
        self.edgeLabel.setObjectName(u"edgeLabel")
        self.edgeLabel.setStyleSheet(u"color: rgb(255, 168, 17);")

        self.gridLayout_5.addWidget(self.edgeLabel, 1, 0, 1, 1)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_5.addWidget(self.label_2, 3, 0, 1, 1)

        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_5.addWidget(self.label_5, 3, 1, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout_5)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.bboxSizeXLabel = QLabel(Form)
        self.bboxSizeXLabel.setObjectName(u"bboxSizeXLabel")

        self.gridLayout.addWidget(self.bboxSizeXLabel, 3, 1, 1, 1)

        self.label_11 = QLabel(Form)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setStyleSheet(u"color: rgb(144, 198, 255);")

        self.gridLayout.addWidget(self.label_11, 2, 0, 1, 1)

        self.bboxCenterYLabel = QLabel(Form)
        self.bboxCenterYLabel.setObjectName(u"bboxCenterYLabel")

        self.gridLayout.addWidget(self.bboxCenterYLabel, 0, 2, 1, 1)

        self.bboxMinZLabel = QLabel(Form)
        self.bboxMinZLabel.setObjectName(u"bboxMinZLabel")

        self.gridLayout.addWidget(self.bboxMinZLabel, 1, 3, 1, 1)

        self.bboxCenterXLabel = QLabel(Form)
        self.bboxCenterXLabel.setObjectName(u"bboxCenterXLabel")

        self.gridLayout.addWidget(self.bboxCenterXLabel, 0, 1, 1, 1)

        self.label_7 = QLabel(Form)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setStyleSheet(u"color: rgb(144, 198, 255);")

        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)

        self.bboxMaxYLabel = QLabel(Form)
        self.bboxMaxYLabel.setObjectName(u"bboxMaxYLabel")

        self.gridLayout.addWidget(self.bboxMaxYLabel, 2, 2, 1, 1)

        self.bboxSizeYLabel = QLabel(Form)
        self.bboxSizeYLabel.setObjectName(u"bboxSizeYLabel")

        self.gridLayout.addWidget(self.bboxSizeYLabel, 3, 2, 1, 1)

        self.bboxSizeZLabel = QLabel(Form)
        self.bboxSizeZLabel.setObjectName(u"bboxSizeZLabel")

        self.gridLayout.addWidget(self.bboxSizeZLabel, 3, 3, 1, 1)

        self.bboxCenterZLabel = QLabel(Form)
        self.bboxCenterZLabel.setObjectName(u"bboxCenterZLabel")

        self.gridLayout.addWidget(self.bboxCenterZLabel, 0, 3, 1, 1)

        self.bboxMaxXLabel = QLabel(Form)
        self.bboxMaxXLabel.setObjectName(u"bboxMaxXLabel")

        self.gridLayout.addWidget(self.bboxMaxXLabel, 2, 1, 1, 1)

        self.bboxMinXLabel = QLabel(Form)
        self.bboxMinXLabel.setObjectName(u"bboxMinXLabel")

        self.gridLayout.addWidget(self.bboxMinXLabel, 1, 1, 1, 1)

        self.bboxMaxZLabel = QLabel(Form)
        self.bboxMaxZLabel.setObjectName(u"bboxMaxZLabel")

        self.gridLayout.addWidget(self.bboxMaxZLabel, 2, 3, 1, 1)

        self.bboxMinYLabel = QLabel(Form)
        self.bboxMinYLabel.setObjectName(u"bboxMinYLabel")

        self.gridLayout.addWidget(self.bboxMinYLabel, 1, 2, 1, 1)

        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"color: rgb(144, 198, 255);")

        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.label_15 = QLabel(Form)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setStyleSheet(u"color: rgb(144, 198, 255);")

        self.gridLayout.addWidget(self.label_15, 3, 0, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout)


        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setContentsMargins(10, -1, 10, -1)
        self.label_23 = QLabel(Form)
        self.label_23.setObjectName(u"label_23")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_23)

        self.vertexAttrText = QTextEdit(Form)
        self.vertexAttrText.setObjectName(u"vertexAttrText")
        self.vertexAttrText.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.vertexAttrText.setReadOnly(True)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.vertexAttrText)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label)

        self.edgeAttrText = QTextEdit(Form)
        self.edgeAttrText.setObjectName(u"edgeAttrText")
        self.edgeAttrText.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.edgeAttrText.setReadOnly(True)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.edgeAttrText)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.faceAttrText = QTextEdit(Form)
        self.faceAttrText.setObjectName(u"faceAttrText")
        self.faceAttrText.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.faceAttrText.setReadOnly(True)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.faceAttrText)

        self.label_6 = QLabel(Form)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label_6)

        self.detailAttrText = QTextEdit(Form)
        self.detailAttrText.setObjectName(u"detailAttrText")
        self.detailAttrText.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.detailAttrText.setReadOnly(True)

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.detailAttrText)


        self.verticalLayout_5.addLayout(self.formLayout_2)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(10, -1, 10, 10)
        self.label_8 = QLabel(Form)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_8)

        self.nodeErrorText = QTextEdit(Form)
        self.nodeErrorText.setObjectName(u"nodeErrorText")
        self.nodeErrorText.setStyleSheet(u"")
        self.nodeErrorText.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nodeErrorText.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nodeErrorText.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.nodeErrorText.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.nodeErrorText)

        self.label_9 = QLabel(Form)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_9)

        self.cookTimeLabel = QLabel(Form)
        self.cookTimeLabel.setObjectName(u"cookTimeLabel")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.cookTimeLabel)


        self.verticalLayout_5.addLayout(self.formLayout)


        self.verticalLayout.addLayout(self.verticalLayout_5)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.nodeNameLabel.setText(QCoreApplication.translate("Form", u"Node Name", None))
        self.nodeTypeLabel.setText(QCoreApplication.translate("Form", u"Node Type", None))
        self.vertexLabel.setText(QCoreApplication.translate("Form", u"Vertices", None))
        self.edgeCntLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.faceLabel.setText(QCoreApplication.translate("Form", u"Faces", None))
        self.vertexCntLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.faceCntLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.edgeLabel.setText(QCoreApplication.translate("Form", u"Edges", None))
        self.label_2.setText("")
        self.label_5.setText("")
        self.bboxSizeXLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"Max", None))
        self.bboxCenterYLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.bboxMinZLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.bboxCenterXLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"Min", None))
        self.bboxMaxYLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.bboxSizeYLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.bboxSizeZLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.bboxCenterZLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.bboxMaxXLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.bboxMinXLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.bboxMaxZLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.bboxMinYLabel.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Center", None))
        self.label_15.setText(QCoreApplication.translate("Form", u"Size", None))
        self.label_23.setText(QCoreApplication.translate("Form", u"Vertex Attrs", None))
        self.label.setText(QCoreApplication.translate("Form", u"Edge Attrs", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Face Attrs", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"Detail Attrs", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"Cook Time", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"Message", None))
        self.cookTimeLabel.setText(QCoreApplication.translate("Form", u"0", None))
    # retranslateUi

