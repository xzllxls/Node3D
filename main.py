#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from Node3D.vendor.NodeGraphQt import *
from Node3D.vendor.NodeGraphQt.constants import *
from PySide2 import QtWidgets
from PySide2.QtGui import *
from Node3D.widgets.mainWindow import mainWindow
import inspect
import importlib
import qdarkstyle


class CommonHelper:
    def __init__(self):
        pass

    @staticmethod
    def readQss(style):
        with open(style, 'r') as f:
            return f.read()


def run(nodes=[]):
    app = QtWidgets.QApplication([])
    app.setFont(QFont("Consolas", 9))
    win = mainWindow()

    # styleFile = './Node3D/vendor/qss/Obit.qss'
    # qssStyle = CommonHelper.readQss(styleFile)
    # win.setStyleSheet(qssStyle)
    app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment())
    # app.setStyleSheet(mainStyle)

    # create node graph.
    graph = win.graph

    # registered nodes.
    nodes.append(BackdropNode)
    for n in nodes:
        graph.register_node(n)

    # graph.create_node('Viewers.DataViewerNode')

    win.node_tree.update()
    win.show()
    win.closed.connect(lambda:app.exit(0))
    sys.exit(app.exec_())


def GetNodesFromFolder(FolderPath):
    path, FolderName = os.path.split(FolderPath)
    if path not in sys.path:
        sys.path.append(path)

    nodes = []
    for i in os.listdir(FolderPath):
        if not i.endswith(".py") or i.startswith("_"):
            continue

        filename = i[:-3]
        module_name = FolderName + "." + filename

        for name, obj in inspect.getmembers(importlib.import_module(module_name)):
            if inspect.isclass(obj) and filename in str(obj):
                if len(inspect.getmembers(obj)) > 0:
                    nodes.append(obj)
    return nodes


if __name__ == '__main__':
    gl_path = os.getcwd() + "/Node3D/nodes"
    register_nodes = []
    register_nodes.extend(GetNodesFromFolder(gl_path))
    run(register_nodes)