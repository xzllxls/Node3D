from Qt import QtWidgets, QtCore
from Qt.QtWidgets import QMainWindow, QDockWidget, QMessageBox
from Qt.QtCore import Qt, QSettings
from ..vendor.NodeGraphQt import NodeGraph, NodeTreeWidget
from ..vendor.NodeGraphQt.widgets.file_dialog import messageBox
from ..vendor.NodeGraphQt.base import utils
from ..base.node import RootNode, update_nodes
from .styles import mainStyle
from .glScene import glScene
from .timeLine import TimeLine
from .scriptEditor import nodeScriptEditor
from .dataTreeWidget import NodeDataTreeWidget
from .parameterTree import NodePropBin
from .nodeInfoPanel import NodeInfoPanel
from .menuBar import setup_menu_bar
import numpy


class mainWindow(QMainWindow):
    closed = QtCore.Signal()

    def __init__(self):
        super(mainWindow, self).__init__()
        self.windowTitle = 'Node3D'
        self.setWindowTitle(self.windowTitle)
        self.init_ui()
        self.init_stylesheet()
        self.on_load()

    def init_ui(self):
        self.graph = NodeGraph()
        self.graph.use_OpenGL()
        self.graph.session_changed.connect(self.on_session_changed)
        self.graph.cook_graph.connect(self.cook_graph_nodes)
        self.graph.node_double_clicked.connect(self.update_view)
        self.graph.node_selected.connect(self.update_param_widget)
        self.graph.show_node_info_panel_triggerd.connect(self.show_node_info_panel)
        self.graph.close_node_info_panel_triggered.connect(self.close_node_info_panel)
        self.graph.master = self
        self.graph.add_node(RootNode())
        self.graph.undo_stack().clear()

        self.propertiesBin = NodePropBin(node_graph=self.graph)
        self.propertiesBin.setWindowFlags(QtCore.Qt.Tool)
        self.propertiesBin.set_limit(2)
        self.node_tree = NodeTreeWidget(node_graph=self.graph)

        self.dataTreeWidget = NodeDataTreeWidget()
        self.consoleWidget = self.add_console()
        self.glWidget = glScene()

        self.timeline = TimeLine()
        self.timeline.setFps(25)
        self.setCentralWidget(self.timeline)

        self.nodeInfoPanel = NodeInfoPanel()

        # set up default menu and commands.
        self.setup_menus()

        self.setDockNestingEnabled(True)

        graphDock = self.add_dock(self.graph.widget, "Graph")
        propertiesDock = self.add_dock(self.propertiesBin, "Properties")
        nodeTreeDock = self.add_dock(self.node_tree, "Node tree")
        dataTreeDock = self.add_dock(self.dataTreeWidget, "Data tree")
        consoleDock = self.add_dock(self.consoleWidget, "Console")
        glDock = self.add_dock(self.glWidget, "Scene")
        # timeDock = self.add_dock(self.timeline, "TimeLine")

        # Qt.Horizontal/Qt.Vertical
        self.addDockWidget(Qt.TopDockWidgetArea, glDock)
        # self.addDockWidget(Qt.BottomDockWidgetArea, timeDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, consoleDock)
        self.splitDockWidget(consoleDock, graphDock, Qt.Horizontal)
        self.splitDockWidget(graphDock, propertiesDock, Qt.Horizontal)
        self.splitDockWidget(propertiesDock, dataTreeDock, Qt.Vertical)
        self.tabifyDockWidget(consoleDock, nodeTreeDock)

        nodeTreeDock.setMaximumWidth(250)
        self.setup_scene()

    def setup_menus(self):
        menu_bar = QtWidgets.QMenuBar()
        self.setMenuBar(menu_bar)
        setup_menu_bar(self.graph, self, menu_bar)
        self.setStatusBar(QtWidgets.QStatusBar())

    def update_view(self, node):
        node = self.graph.get_node_by_id(node.id)
        self.glWidget.set_node(node)

    def update_param_widget(self, node):
        node = self.graph.get_node_by_id(node.id)
        if self.dataTreeWidget.isVisible():
            self.dataTreeWidget.set_node(node)
            print('da')
        if self.consoleWidget.isVisible():
            self.consoleWidget.set_node(node)

    def add_console(self):
        # background-color: #373737; color: #00BFFF
        # background-color: black; color: #0489B1
        # namespace = {'gp': self.graph}
        # text = "import graph as gp"
        # console = ConsoleWidget(namespace=namespace, text=text)
        # console.setStyleSheet("QWidget(border:0px solid;)")
        console = nodeScriptEditor()
        console.updateNamespace({"gp": self.graph, 'wid': self, 'np': numpy})
        return console

    def add_dock(self, widget, name):
        # dock.setAutoFillBackground(True)
        # dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

        dock = QDockWidget(name, self)
        dock.setWidget(widget)
        dock.setObjectName(name)
        return dock

    def setup_scene(self):
        pass

    def closeEvent(self, event):
        if self.maybeSave():
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())
            event.accept()
            self.closed.emit()
        else:
            event.ignore()

    def on_session_changed(self, session_name):
        self.setWindowTitle(self.windowTitle + "    " + session_name)
        self.message("session changed")

    def init_stylesheet(self):
        self.setStyleSheet(mainStyle)

    def on_load(self):
        self.settings = QSettings("ARNO", "APP")
        if self.settings.value("geometry") is not None:
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.value("windowState") is not None:
            self.restoreState(self.settings.value("windowState"))

    def maybeSave(self):
        res = messageBox("Would you like to save session?",
                         "Save Information",
                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if res == QMessageBox.Yes:
            utils._save_session(self.graph)
            return True
        elif res == QMessageBox.Cancel:
            return False

        return True

    def message(self, msg):
        self.statusBar().showMessage(msg)

    def show_node_info_panel(self, node):
        self.nodeInfoPanel.refresh(node)

    def close_node_info_panel(self):
        self.nodeInfoPanel.close()

    def cook_graph_nodes(self):
        update_nodes(self.graph.root_node().children())