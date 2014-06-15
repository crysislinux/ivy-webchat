# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from workspace import Workspace


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.createActions()
        self.createMenuBar()
        self.createToolBar()
        self.setCentralWidget(self.createCentralWidget())
        self.setWindowIcon(QIcon('images/logo.png'))
        self.loadSettings()

    def createActions(self):
        self.fileAction = QAction(QIcon('images/map.png'), u'文件', self)
        self.helpAction = QAction(QIcon('images/add.png'), u'帮助', self)

    def createMenuBar(self):
        fileMenu = self.menuBar().addMenu(u'文件')
        fileMenu.addAction(self.fileAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.helpAction)
        helpMenu = self.menuBar().addMenu(u'帮助')
        helpMenu.addAction(self.helpAction)
        helpMenu.triggered.connect(self.actionTest)

    def createToolBar(self):
        toolBar = self.addToolBar(u'文件')
        toolBar.setIconSize(QSize(16, 16))
        toolBar.setMovable(False)
        toolBar.addAction(self.fileAction)
        toolBar.addSeparator()
        toolBar.addAction(self.helpAction)

    def createCentralWidget(self):
        self.centralWidget = Workspace()
        return self.centralWidget

    def actionTest(self):
        print('test')

    def loadSettings(self):
        settings = QSettings()
        geometry = settings.value('MainWindow/geometry')

        #如果设置文件存在，那么geometry的值一定存在，否则说明是第一次启动，跳过之后的设置读取过程
        if not geometry:
            return
        self.restoreGeometry(geometry)

    def saveSettings(self):
        settings = QSettings()
        settings.beginGroup('MainWindow')
        settings.setValue('geometry', self.saveGeometry())
        settings.endGroup()

    def closeEvent(self, e):
        self.saveSettings()
        self.centralWidget.saveSettings()


if __name__ == '__main__':
    from application import Globals
    Globals.setAttr('servers', {'server1': ('127.0.0.1', 22333)})
    import singleton
    app = singleton.getApplication()
    app.setOrganizationName('ivy')
    app.setApplicationName('webchat-chat-advance')
    app.setStyleSheet(
        'QWidget{background-color: #D6D6D6;color: #000;font-size: 13px;}'

        'QScrollBar:horizontal {border-top: 1px solid grey;height: 15px;border-bottom: none;padding: 1px 0;}'

        'QScrollBar:vertical {border-left: 1px solid grey;width: 15px;padding: 0 1px; border-right:none}'

        'QScrollBar::add-line,  QScrollBar::sub-line {width:0;}'

        'QScrollBar::handle:horizontal {border: 1px solid #818A9A; border-radius: 4px;'
        'background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,'
        'stop: 0 #ECECEC, stop: 0.4 #E4E4E4,stop: 0.5 #E0E0E0, stop: 1.0 #D6D6D6);}'

        'QScrollBar::handle:horizontal:hover{background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,'
        'stop: 0 #D6D6D6, stop: 0.5 #A7A7A7, stop: 1.0 #9B9B9B);}'

        'QScrollBar::handle:vertical {border: 1px solid #818A9A; border-radius: 4px;'
        'background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,'
        'stop: 0 #ECECEC, stop: 0.4 #E4E4E4,stop: 0.5 #E0E0E0, stop: 1.0 #D6D6D6);}'

        'QScrollBar::handle:vertical:hover{background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,'
        'stop: 0 #D6D6D6, stop: 0.5 #A7A7A7, stop: 1.0 #9B9B9B);}'

        'QTreeView {background: white}'

        'QTreeView::item {padding: 4px 0; background:  transparent;}'

        'QTreeView::item:selected {background:  transparent; color: black}'

        'QTreeView::branch {background: white}'

        'QTreeView::branch:has-siblings:adjoins-item {border-image: url(images/branch-more.png) 0;}'

        'QTreeView::branch:!has-children:!has-siblings:adjoins-item {border-image: url(images/branch-end.png) 0;}'

        'QTreeView::branch:has-children:!has-siblings:closed,QTreeView::branch:closed:has-children:has-siblings {'
        'border-image: none;image: url(images/branch-closed.png);}'

        'QTreeView::branch:open:has-children:!has-siblings,QTreeView::branch:open:has-children:has-siblings  {'
        'border-image: none;image: url(images/branch-open.png);}'

        'QPushButton {border: 1px solid #818A9A;border-radius: 0;'
        'background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,''stop: 0 #f6f7fa, stop: 1 #dadbde);'
        'min-width: 60px; min-height: 21px}'
        'QPushButton:pressed {background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,'
        'stop: 0 #dadbde, stop: 1 #f6f7fa);}'
        'QPushButton:flat {border: none;}'
        'QPushButton:default {border-color: #1D953F;}'

        'QMenuBar {padding: 2px 0; border-bottom: 1px solid #818A9A;}'
        'QMenuBar::item {padding: 2px 4px;}'
        'QMenuBar::item:selected {background-color: #426AB3; color: white;}'

        'QMenu {border-top: 1px solid white; border-left: 1px solid white;border-right: 2px solid #949494; '
        'border-bottom: 2px solid #949494;padding: 2px 1px;}'
        'QMenu::separator {height: 1px; background: #818A9A; border-bottom: 1px solid white; margin-top: 1px;}'
        'QMenu::item {padding: 2px 60px 2px 24px;border: 1px solid transparent;}'
        'QMenu::item:selected {background-color: #426AB3; color: white;}'

        'QToolBar {border-bottom: 1px solid #818A9A;}'
        'QToolBar::separator {width: 1px; background: #818A9A; margin: 0 1px;}'

        'QTableView::item:selected {background: #426AB3}'

        'QLineEdit{background-color: #FFF; color: #000; border: 1px solid #818A9A; padding: 2px}'
    )
    b = MainWindow()
    b.show()
    from network import ExternalManager
    externalManager = ExternalManager()
    externalManager.start()
    app.exec_()