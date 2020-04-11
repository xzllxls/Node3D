from Qt import QtGui, QtWidgets
from ..base.node import AutoNode, GeometryNode, SubGraphNode
from ..vendor.NodeGraphQt import NodePublishWidget
from ..vendor.NodeGraphQt.base import utils
from ..vendor.NodeGraphQt.constants import (PIPE_LAYOUT_ANGLE, PIPE_LAYOUT_STRAIGHT,
                                            PIPE_LAYOUT_CURVED, VIEWER_GRID_DOTS,
                                            VIEWER_GRID_LINES, VIEWER_GRID_NONE)


def allow_edit(graph, node):
    node.set_property('published', False)


def cook_node(graph, node):
    node.update_stream(forceCook=True)


def print_functions(graph, node):
    for func in node.module_functions:
        print(func)


def toggle_auto_cook(graph, node):
    node.auto_cook = not node.auto_cook


def show_parameter(graph, node):
    graph.master.propertiesBin.add_node(node)


def draw_geometry(graph, node):
    graph.master.glWidget.set_node(node)


def enter_node(graph, node):
    graph.set_node_space(node)


def print_path(graph, node):
    print(node.path())


def find_node_by_path(graph, node):
    print(graph.get_node_by_path(node.path()))


def print_children(graph, node):
    children = node.children()
    print(len(children), children)


def publish_node(graph, node):
    wid = NodePublishWidget(node=node)
    wid.show()


def add_command(menu, name, func=None, parent=None, shortcut=None):
    action = QtWidgets.QAction(name, parent)
    if shortcut:
        action.setShortcut(shortcut)
    if func:
        action.triggered.connect(func)
    menu.addAction(action)


def setup_menu_bar(graph, window, root_menu):
    root_menu.setNativeMenuBar(False)
    view = graph.viewer()

    file_menu = root_menu.addMenu(' &File')
    edit_menu = root_menu.addMenu(' &Edit')
    graph_menu = root_menu.addMenu(' &Graph')

    # File Menu
    add_command(file_menu, 'Open...', lambda: utils._open_session(graph), window, QtGui.QKeySequence.Open)
    add_command(file_menu, 'Import...', lambda: utils._import_session(graph), window)
    add_command(file_menu, 'Save...', lambda: utils._save_session(graph), window, QtGui.QKeySequence.Save)
    add_command(file_menu, 'Save As...', lambda: utils._save_session_as(graph), window, 'Ctrl+Shift+S')
    add_command(file_menu, 'New Session', lambda: utils._new_session(graph), window)
    add_command(file_menu, 'Close', window.close, window)

    # Edit Menu
    undo_actn = graph.undo_stack().createUndoAction(view, '&Undo')
    undo_actn.setShortcutVisibleInContextMenu(True)
    undo_actn.setShortcuts(QtGui.QKeySequence.Undo)
    edit_menu.addAction(undo_actn)

    redo_actn = graph.undo_stack().createRedoAction(view, '&Redo')
    redo_actn.setShortcutVisibleInContextMenu(True)
    redo_actn.setShortcuts(QtGui.QKeySequence.Redo)
    edit_menu.addAction(redo_actn)

    edit_menu.addSeparator()
    add_command(edit_menu, 'Clear Undo History', lambda: utils._clear_undo(graph), view)
    edit_menu.addSeparator()

    add_command(edit_menu, 'Copy', lambda: utils._copy_nodes(graph), view, QtGui.QKeySequence.Copy)
    add_command(edit_menu, 'Duplicate', lambda: utils._duplicate_nodes(graph), view, 'Alt+C')
    add_command(edit_menu, 'Cut', lambda: utils._cut_nodes(graph), view, QtGui.QKeySequence.Cut)
    add_command(edit_menu, 'Paste', lambda: utils._paste_nodes(graph), view, QtGui.QKeySequence.Paste)
    add_command(edit_menu, 'Delete', lambda: utils._delete_items(graph), view, QtGui.QKeySequence.Delete)
    edit_menu.addSeparator()

    add_command(edit_menu, 'Select all', lambda: utils._select_all_nodes(graph), view, 'Ctrl+A')
    add_command(edit_menu, 'Deselect all', lambda: utils._clear_node_selection(graph), view, 'Ctrl+Shift+A')
    add_command(edit_menu, 'Enable/Disable', lambda: utils._disable_nodes(graph), view, 'D')

    # Graph Menu
    add_command(graph_menu, 'Jump In', lambda: utils._jump_in(graph), view, 'I')
    add_command(graph_menu, 'Jump Out', lambda: utils._jump_out(graph), view, 'O')
    graph_menu.addSeparator()

    add_command(graph_menu, 'Zoom In', lambda: utils._zoom_in(graph), view, '=')
    add_command(graph_menu, 'Zoom Out', lambda: utils._zoom_out(graph), view, '-')
    add_command(graph_menu, 'Reset Zoom', lambda: utils._reset_zoom(graph), view, 'H')
    add_command(edit_menu, 'Center Selection', lambda: utils._fit_to_selection(graph), view, 'F')
    graph_menu.addSeparator()

    add_command(graph_menu, 'Layout Graph Down Stream', lambda: utils._layout_graph_down(graph), view, 'L')
    add_command(graph_menu, 'Layout Graph Up Stream', lambda: utils._layout_graph_up(graph), view, 'Ctrl+L')
    graph_menu.addSeparator()

    pipe_menu = graph_menu.addMenu('&Pipe')
    add_command(pipe_menu, 'Curved Pipe', lambda: graph.set_pipe_style(PIPE_LAYOUT_CURVED), view)
    add_command(pipe_menu, 'Straight Pipe', lambda: graph.set_pipe_style(PIPE_LAYOUT_STRAIGHT), view)
    add_command(pipe_menu, 'Angle Pipe', lambda: graph.set_pipe_style(PIPE_LAYOUT_ANGLE), view)

    pipe_menu = graph_menu.addMenu('&Grid Mode')
    add_command(pipe_menu, 'None', lambda: graph.set_grid_mode(VIEWER_GRID_NONE), view)
    add_command(pipe_menu, 'Lines', lambda: graph.set_grid_mode(VIEWER_GRID_LINES), view)
    add_command(pipe_menu, 'Dots', lambda: graph.set_grid_mode(VIEWER_GRID_DOTS), view)
    graph_menu.addSeparator()

    # Node Menu
    node_menu = graph.context_nodes_menu()
    node_menu.add_command('Allow Edit', allow_edit, node_class=SubGraphNode)
    node_menu.add_command('Enter Node', enter_node, node_class=SubGraphNode)
    node_menu.add_command('Publish Node', publish_node, node_class=SubGraphNode)
    node_menu.add_command('Print Children', print_children, node_class=SubGraphNode)

    # node_menu.add_command('Print Functions', print_functions, node_class=ModuleNode)
    node_menu.add_command('Draw Geometry', draw_geometry, node_class=SubGraphNode)
    node_menu.add_command('Draw Geometry', draw_geometry, node_class=GeometryNode)
    node_menu.add_command('Cook Node', cook_node, node_class=AutoNode)
    node_menu.add_command('Toggle Auto Cook', toggle_auto_cook, node_class=AutoNode)
    node_menu.add_command('Show Parameter', show_parameter, node_class=AutoNode)
