from ..vendor.NodeGraphQt import *
from ..vendor.NodeGraphQt.constants import *
from ..vendor.NodeGraphQt.widgets.file_dialog import messageBox
from ..vendor.NodeGraphQt.base import utils
from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from .styles import mainStyle
from ..base.node.auto_node import AutoNode
from .glScene import glScene
from .timeLine import TimeLine
from .scriptEditor import nodeScriptEditor
from .dataTreeWidget import NodeDataTreeWidget
import numpy
from .parameterTree import NodePropBin
from .nodeInfoPanel import NodeInfoPanel


def cook_node(graph, node):
    node.cook(True)


def print_functions(graph, node):
    for func in node.module_functions:
        print(func)


def toggle_auto_cook(graph, node):
    node.autoCook = not node.autoCook


def add_command(menu, name, func=None, parent=None, shortcut=None):
    action = QtWidgets.QAction(name, parent)
    if shortcut:
        action.setShortcut(shortcut)
    if func:
        action.triggered.connect(func)
    menu.addAction(action)


def setup_menubar(graph, window, root_menu):
    root_menu.setNativeMenuBar(False)
    view = graph.viewer()

    file_menu = root_menu.addMenu(' &File')
    edit_menu = root_menu.addMenu(' &Edit')
    graph_menu = root_menu.addMenu(' &Graph')

    # create "File" menu.
    add_command(file_menu, 'Open...', lambda: utils._open_session(graph), window, QtGui.QKeySequence.Open)
    add_command(file_menu, 'Import...', lambda: utils._import_session(graph), window)
    add_command(file_menu, 'Save...', lambda: utils._save_session(graph), window, QtGui.QKeySequence.Save)
    add_command(file_menu, 'Save As...', lambda: utils._save_session_as(graph), window, 'Ctrl+Shift+s')
    add_command(file_menu, 'New Session', lambda: utils._new_session(graph), window)
    add_command(file_menu, 'Close', window.close, window)

    # create "Edit" menu.
    undo_actn = graph.undo_stack().createUndoAction(view, '&Undo')
    undo_actn.setShortcutVisibleInContextMenu(True)
    undo_actn.setShortcuts(QtGui.QKeySequence.Undo)
    edit_menu.addAction(undo_actn)

    redo_actn = graph.undo_stack().createRedoAction(view, '&Redo')
    redo_actn.setShortcutVisibleInContextMenu(True)
    redo_actn.setShortcuts(QtGui.QKeySequence.Redo)
    edit_menu.addAction(redo_actn)

    edit_menu.addSeparator()
    add_command(edit_menu, 'Clear Undo History', lambda: utils._clear_undo(graph))
    edit_menu.addSeparator()

    add_command(edit_menu, 'Copy', lambda: utils._copy_nodes(graph), view, QtGui.QKeySequence.Copy)
    add_command(edit_menu, 'Paste', lambda: utils._paste_nodes(graph), view, QtGui.QKeySequence.Paste)
    add_command(edit_menu, 'Delete', lambda: utils._delete_items(graph), view, QtGui.QKeySequence.Delete)

    edit_menu.addSeparator()

    add_command(edit_menu, 'Select all', lambda: utils._select_all_nodes(graph), view, 'Ctrl+A')
    add_command(edit_menu, 'Deselect all', lambda: utils._clear_node_selection(graph), view, 'Ctrl+Shift+A')
    add_command(edit_menu, 'Enable/Disable', lambda: utils._disable_nodes(graph), view, 'd')

    add_command(edit_menu, 'Duplicate', lambda: utils._duplicate_nodes(graph), view, 'Alt+c')

    pipe_menu = graph_menu.addMenu('&Pipe')
    add_command(pipe_menu, 'Curve Pipe', lambda: graph.set_pipe_style(PIPE_LAYOUT_CURVED), view)
    add_command(pipe_menu, 'Straght Pipe', lambda: graph.set_pipe_style(PIPE_LAYOUT_STRAIGHT), view)
    add_command(pipe_menu, 'Angle Pipe', lambda: graph.set_pipe_style(PIPE_LAYOUT_ANGLE), view)
    add_command(graph_menu, 'Toggle Disable Grid', lambda: graph.display_grid(not graph.scene().grid), view)
    graph_menu.addSeparator()
    add_command(graph_menu, 'Zoom In', lambda: utils._zoom_in(graph), view, '=')
    add_command(graph_menu, 'Zoom Out', lambda: utils._zoom_out(graph), view, '-')
    add_command(graph_menu, 'Reset Zoom', lambda: utils._reset_zoom(graph), view, 'h')
    add_command(edit_menu, 'Center Selection', lambda: utils._fit_to_selection(graph), view, 'f')
    graph_menu.addSeparator()

    # node menu
    node_menu = graph.context_nodes_menu()
    # node_menu.add_command('Print Functions', print_functions, node_class=ModuleNode)
    node_menu.add_command('Cook Node', cook_node, node_class=AutoNode)
    node_menu.add_command('Toggle Auto Cook', toggle_auto_cook, node_class=AutoNode)


class mainWindow(QMainWindow):
    closed = QtCore.Signal()

    def __init__(self):
        super(mainWindow, self).__init__()
        self.windowTitle = 'ANRO Node Framework'
        self.setWindowTitle(self.windowTitle)
        self.init_ui()
        self.init_stylesheet()
        self.on_load()

    def init_ui(self):
        self.graph = NodeGraph()
        self.graph.use_opengl()
        self.graph.session_changed.connect(self.on_session_changed)
        self.graph.node_double_clicked.connect(self.update_data)
        self.graph.show_node_info_panel_triggerd.connect(self.show_node_info_panel)
        self.graph.close_node_info_panel_triggered.connect(self.close_node_info_panel)
        self.graph.master = self

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
        menubar = QtWidgets.QMenuBar()
        self.setMenuBar(menubar)
        setup_menubar(self.graph, self, menubar)
        self.setStatusBar(QtWidgets.QStatusBar())

    def update_data(self, node):
        node = self.graph.get_node_by_id(node.id)
        self.dataTreeWidget.set_node(node)
        self.glWidget.set_node(node)
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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                self.graph.import_session(url.toLocalFile())
        else:
            event.ignore()

    def show_node_info_panel(self, node):
        self.nodeInfoPanel.refresh(node)

    def close_node_info_panel(self, node):
        self.nodeInfoPanel.close()
