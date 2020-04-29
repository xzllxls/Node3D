from Qt import QtGui
import os
icon_path = os.path.abspath(os.path.dirname(__file__))+"/icons"
icon_path = icon_path.replace("\\", "/")
mainColor = QtGui.QColor(55, 55, 55).name()

mainStyle = '''
QDialog {{
    background-color: {0};
    }}
QWidget{{
    background-color:{0};
    color:rgb(200,200,200);
    border-style: groove;
    border-width: 0px;
    border-color: rgb(30,30,30);
    }}
QLabel{{
    background-color:{0};
    color:rgb(200,200,200);
    font-size:13px;
    border:0px;
    }}
QTabWidget::pane {{
        top:20px;
        border-width: 1px;
        border-color: rgb(70,70,70);
        background-color: rgb(70,70,70);
    }}
QTableWidget::item{{
    selection-background-color: rgb(0,255,2);
    }}
QTabWidget::tab-bar{{
    background:transparent;
    }}
QTabBar::tab{{
    max-width:200px;
    max-height:15px;
    background-color:rgb(80,80,80);
    color: rgb(200,200,200); 
    }}
QTabBar::tab:selected{{
    background-color: rgb(30,100,200);
    }}
QTabBar::tab::hover {{
    background-color: rgb(30,80,200);
}}
QSlider {{
    border-width: 0px;
}}
QLineEdit{{
    border: 1px groove;
    border-radius: 1px;
    background: rgb(20,20,20);
    max-height: 17px;
}}
QGraphicsView{{
    border-style: groove;
    border-width: 0px;
    border-color: rgb(30,30,30);
    }}
QGraphicsScene{{
    border-width: 1px;
    background-color: rgb(10,80,200);
    }}
QComboBox{{
    border-style: inset;
    border-width: 1px;
    border-radius: 1px;
    }}
QComboBox::hover {{
    background-color: rgb(30, 30, 30);
    }}
QCheckBox{{
    border-width: 0px;
    spacing: 0px;
    }}
QPushButton {{ 
    background-color: rgb(70, 70, 70);
    border-style: outset;
    border-radius: 1px;  
    border-width: 2px;
    border-color: rgb(30,30,30);
    min-width: 30;
    min-height: 10;
    max-width: 30;
    max-height: 10;
    }}
QPushButton::pressed {{
    border-style: inset;
    }}
QPushButton::hover {{
    border-color: rgb(10,80,150);
    }}
QColorDialog{{
    background-color: rgb(50, 50, 50);
    }}
QDockWidget::float-button{{
    background-color: transparent;
    }}
QDockWidget::close-button{{
    background-color: transparent;
    }}
QDockWidget::title{{
    background-color: rgb(65,65,65);
    border-width: 1px;
    border-style: groove;
    border-color: rgb(70,70,70);
    padding: 0px;
    }}
QDockWidget::dockWidgetContents{{
    border: 1px solid;
    }}
QSpinBox{{
    max-height: 15;
    background-color: rgb(20,20,20);
    border-radius: 0px;  
    }}
QMenuBar{{
    border: 1px;
    max-height: 28;
    }}
QTreeWidget{{
    background:{0};
    border-width: 0px;
    }}
QTreeView::item:hover {{ 
    background: rgb(70,70,70);
}}
QHeaderView::section{{
    background-color:{0};
    }}
QTreeWidget::branch{{
    background:{0};
    }}
QTreeView::branch:has-siblings:!adjoins-item {{
    border-image: url({1}/vline.png) 0;
    }}
QTreeView::branch:has-siblings:adjoins-item {{
    border-image: url({1}/branch-more.png) 0;
    }}
QTreeView::branch:!has-children:!has-siblings:adjoins-item {{
    border-image: url({1}/branch-end.png) 0;
    }}
QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings {{
        border-image: none;
        image: url({1}/branch-closed.png);
    }}
QTreeView::branch:open:has-children:!has-siblings,
QTreeView::branch:open:has-children:has-siblings  {{
        border-image: none;
        image: url({1}/branch-open.png);
    }}
QTableWidget{{
    background:{0};
    gridline-color: rgb(70, 70, 70);
    border:0px;
    border-radius: 0px; 
    }}
QTableCornerButton::section{{
    background:{0};
    }}
QMainWindow::separator {{
    width: 0px;
    height: 0px;
    margin: 0px;
    padding: 5px;
    background: rgb(70,70,70);
    border-width: 1px;
    border-color: rgb(20,20,20)
}}
QMainWindow::separator:hover {{
    background: rgb(90,90,90);
    border-color: rgb(20,20,20)
}}
QSplitter::handle:horizontal {{
    width: 4px;
    background: rgb(70,70,70);
    border-width: 1px;
    border-color: rgb(20,20,20)
}}
QSplitter::handle:horizontal:hover {{
    background-color: rgb(90,90,90);
}}
QSplitter::handle:vertical {{
    height: 4px;
    background: rgb(70,70,70);
    border-width: 1px;
    border-color: rgb(20,20,20)
}}
QMenu::item{{
    background-color: {0};
}}
QMenu::item:selected {{
    background-color: rgb(50,155,230);
}}
QScrollBar:vertical{{
    background: rgb(40,40,40);
    border-width: 1px;
    border-style: groove;
}}
QScrollBar:horizontal {{
    background: rgb(40,40,40);
    border-width: 1px;
    border-style: groove;
}}
QTextBrowser{{
    background: rgb(35,35,35);
}}
QStatusBar {{
    background: rgb(45,45,45);
}}
QSlider::Horizontal{{
    height: 6px;
    background:transparent;
}}
QSlider::groove::Horizontal{{
    border: 1px solid rgb(0, 0, 0);
    height: 4px;
    background:rgb(30,30,30);
}}
QSlider::handle:Horizontal{{
    border: 1px solid rgb(0, 0, 0);
    width: 5px;
    margin: -10px 0;
    border-radius: 1px;
}}
QSlider::sub-page:Horizontal{{
    border: 1px solid rgb(0, 0, 0);
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                stop:0 rgb(231,80,229), 
                                stop:1 rgb(7,208,255));
    height: 6px;
}}
'''.format(mainColor, icon_path)


#QCheckBox::indicator:checked {{
#    image: url({1}/check.png);
#}}


'''
QPushButton {{ 
    color: rgb(200,200,200);
    /* background-color: rgb(80,80,80); */
    border-style: outset;
    border-radius: 1px;  
    border-width: 2px;
    border-color: rgb(30,30,30);
    min-height: 15;
    min-width: 50;
    max-width: 200;
    max-height: 15;
    }}
QPushButton::pressed {{
    background-color: rgb(30, 30, 30);
    border-style: inset;
    }}
QPushButton::hover {{
    background-color: rgb(10,80,150);
    }}
'''


STYLE_BUTTON = '''
QPushButton {
    border-style: outset;
    border-radius: 0px;  
    border-width: 1px;
    border-color: rgb(30,30,30);
    min-width: 15;
    min-height: 15;
    max-width: 20;
    font-size: 13px;
    color:rgb(200,200,200);
    padding-left: 10px;
    padding-right: 10px;
    }
QPushButton::pressed {
    border-style: inset;
    }
QPushButton::hover {
    border-color: rgb(10,80,150);
    }
'''


PROP_TREE_VIEW = '''
QDialog {{ 
    border-width: 0px;
}}
QWidget{{ 
    border-width: 0px;
    padding: 0px;
    margin: 0px;
}}
QLineEdit{{ 
    border: 0px groove;
    border-radius: 0px;
    background:rgb(20,20,20);
    min-height: 20px;
    padding: 0px;
    margin: 0px;
    font-size:13px;
}}
QComboBox{{ 
    border-width: 1px;
    border-color: rgba(255,255,255,20);
    border-radius: 0px;
    background-color: rgb(70,70,70); 
    border-radius: 0px;
    padding-left: 4px;
    padding-right: 4px;
    max-height: 17px;
}}
QComboBox::hover{{ 
    background-color: rgb(80,80,80); 
}}
QComboBox QAbstractItemView {{
    border: 1px solid gray;
    border-radius: 0px;
    selection-background-color: rgb(50,155,230);
    background-color: rgb(45,45,45); 
}}
QComboBox::drop-down{{
    border: 1px groove;
    background-color: rgb(20,20,20); 
}}
QComboBox::down-arrow:on {{
    top: 1px;
    left: 1px;
}}
QTextEdit{{ 
    border: 0px groove;
    border-radius: 0px;
    background:rgb(35,35,35);
}}
QTreeWidget{{ 
    background:transparent;
    font-size:13px;
}}
QHeaderView::section {{  
    min-height: 25px;
    color:white;
    background-color:{0};
    alternate-background-color: transparent;
    border:0px solid gray; 
}}
QTreeView {{ 
    border:none;
    background-color: {0};
    show-decoration-selected: 0;
}}
QTreeView::item {{ 
    min-height: 25px;
    border: none;
    color:rgb(200,200,200);
    background-color: {0};
}}
QTreeView::item:hover {{ 
    background: rgb(70,70,70);
}}
QTreeView::item:selected{{ 
    background: rgb(50,50,50);
}}
QTreeView::branch {{ 
    background-color: {0};
    image:none;
}}
QTreeView::branch:has-siblings:adjoins-item {{
    image:none;
    border-image: none;
}}
QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings {{
    border-image: none;
    image: url({1}/branch-closed.png);
}}
QTreeView::branch:open:has-children:!has-siblings,
QTreeView::branch:open:has-children:has-siblings  {{
    border-image: none;
    image: url({1}/branch-open.png);
}}
QTreeView::branch:has-siblings:!adjoins-item {{
    image:none;
    border-image: none;
}}
QTreeView::branch:!has-children:!has-siblings:adjoins-item {{
    image:none;
    border-image: none;
}}
QLabel{{
    border:0px;
    font-size:13px;
}}
QScrollBar:vertical{{
    background: rgb(40,40,40);
    border-width: 1px;
    border-style: groove;
}}
QScrollBar:horizontal {{
    background: rgb(40,40,40);
    border-width: 1px;
    border-style: groove;
}}
QPushButton {{
    border-style: outset;
    border-radius: 0px;  
    border-width: 1px;
    border-color: rgb(30,30,30);
    min-width: 20;
    min-height: 17;
    font-size:13px;
    color:rgb(200,200,200);
    padding-left: 10px;
    padding-right: 10px;
}}
QPushButton::pressed {{
    border-style: inset;
}}
QPushButton::hover {{
    border-color: rgb(10,80,150);
}}
'''.format(mainColor, icon_path)