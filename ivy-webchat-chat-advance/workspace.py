# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from widgets.bars import ToolBar, ChoiceBar
from application import Log, Event, EventManager
from widgets.log_window import LogWindow
from widgets.buttons import ChoiceButton, ToolButton
from widgets.vm_list import VMList
from widgets.gmap import GMap
from widgets.side_panel import SideContainer, MapSidePanel, ControlSidePanel
from widgets.webchat import WebChat, WebChatContainer
import application
from message import Message


class TabContainer(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.tabWidget)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        self.tabWidget.currentChanged.connect(self.resetCurrentWebchat)
        EventManager.bind('Message.vmStarted', self.syncVideoOfVm)
        EventManager.bind('Message.vmStartFail', self.closeWebchat)

    def closeWebchat(self, params):
        vmId = params['vmId']
        for i in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(i)
            if not isinstance(widget, WebChatContainer):
                continue
            for webchat in widget.webchats:
                if webchat.vmId() == vmId:
                    widget.removeWebchat(webchat)

    def resetCurrentWebchat(self, index):
        widget = self.tabWidget.widget(index)
        if isinstance(widget, WebChatContainer):
            if widget.current:
                EventManager.trigger(Event('Webchat.currentChanged', widget.current))

    def syncVideoOfVm(self, params):
        """将合适的webchat vnc连接到合适的服务器上"""
        vmId = params['vmId']
        for i in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(i)
            if not isinstance(widget, WebChatContainer):
                continue
            for webchat in widget.webchats:
                if webchat.vmId() == vmId:
                    webchat.createVncViewPort(params)
                    return

    def lookUpVmTab(self, vmId):
        for i in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(i)
            if not isinstance(widget, WebChatContainer):
                continue
            for index, webchat in enumerate(widget.webchats):
                if webchat.vmId() == vmId:
                    return index, widget,
        return -1, None

    def lookUpVmSpace(self):
        for i in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(i)
            if not isinstance(widget, WebChatContainer):
                continue
            if widget.hasSpace():
                return widget.spaceIndex(), widget
        widget = WebChatContainer()
        widget.webchatRemoved.connect(self.handleWebchatRemoved)
        self.addTab(widget)
        return 0, widget

    def setCurrentWidget(self, widget, index=0):
        self.tabWidget.setCurrentWidget(widget)
        widget.setCurrent(index)

    def addTab(self, widget=None, name=None):
        if not widget:
            widget = WebChatContainer()
        if not name:
            name = u'未命名'
        self.tabWidget.addTab(widget, name)

    def setTabName(self, widget, name):
        self.tabWidget.setTabText(self.tabWidget.indexOf(widget), name)

    def tabName(self, widget):
        return self.tabWidget.tabText(self.tabWidget.indexOf(widget))

    def handleWebchatRemoved(self):
        for i in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(i)
            if isinstance(widget, WebChatContainer):
                self.adjustTabName(widget)

    def adjustTabName(self, widget):
        name = ''
        for index, webchat in enumerate(widget.webchats):
            name += webchat.name()
            if index < len(widget.webchats) - 1:
                name += '|'
        self.setTabName(widget, name)

    def closeTab(self, index):
        widget = self.tabWidget.widget(index)
        msgBox = QMessageBox()
        msgBox.setText(u'是否真的要关闭: ' + self.tabWidget.tabText(index))
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        msgBox.setWindowTitle(u'关闭tab页')
        info = widget.information()
        if info:
            try:
                accounts = info['accounts']
                text = u'该tab页已登陆帐号：\n'
                for account in accounts:
                    text += account + '\n'
                text.rstrip('\n')
                msgBox.setInformativeText(unicode(text))
            except KeyError:
                pass
        result = msgBox.exec_()
        if result == QMessageBox.Yes:
            for webChat in widget.webchats:
                vmId = webChat.vmId()
                clientId = application.lookUpClientIdByResourceId(vmId)
                message = Message(cmd=Message.CMD_CLOSE_VM)
                message['vmId'] = vmId
                EventManager.trigger(Event('Client.replyReady.' + clientId, message))
            self.tabWidget.removeTab(index)

    def sizeHint(self):
        return QSize(1000, 600)

    def paintEvent(self, e):
        painter = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)


class StatusBar(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, e):
        painter = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

    def sizeHint(self):
        return QSize(self.width(), self.fontMetrics().height() + 8)


class SideStackedContainer(QStackedWidget):
    hidePanelClicked = pyqtSignal()

    def __init__(self, parent=None):
        QStackedWidget.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)


class BottomSideStackedContainer(QSplitter):
    hidePanelClicked = pyqtSignal()

    def __init__(self, parent=None):
        QSplitter.__init__(self, parent)
        self.setOrientation(Qt.Horizontal)
        self.setHandleWidth(1)
        self.setChildrenCollapsible(False)


class Workspace(QWidget):
    Left = 0
    Right = 1
    Bottom = 3

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.statusBar = StatusBar()
        self.statusBar.setStyleSheet(
            'StatusBar {border-bottom: 1px solid #818A9A; background-color: #C2C2C2;}'
        )

        self.choiceBars = {self.Left: ChoiceBar(), self.Right: ChoiceBar(), self.Bottom: ChoiceBar(Qt.Horizontal)}
        names = {self.Left: 'leftChoiceBar', self.Right: 'rightChoiceBar', self.Bottom: 'bottomChoiceBar'}
        for index in self.choiceBars:
            self.choiceBars[index].setObjectName(names[index])
        self.choiceBars[self.Right].setStyleSheet(
            'ChoiceBar {border-left: 1px solid #818A9A;}'
        )
        self.choiceBars[self.Right].setAutoExclusive(True)
        self.choiceBars[self.Left].setStyleSheet(
            'ChoiceBar {border-right: 1px solid #818A9A;}'
        )
        self.choiceBars[self.Left].setAutoExclusive(True)
        self.choiceBars[self.Bottom].setStyleSheet(
            'ChoiceBar {border-top: 1px solid #818A9A;}'
        )
        for position in self.choiceBars:
            self.choiceBars[position].checkedChanged.connect(self.changeCurrentSidePanel)

        self.upMainArea = QSplitter(Qt.Horizontal)
        self.upMainArea.setChildrenCollapsible(False)
        self.upMainArea.setHandleWidth(1)
        self.upMainArea.setStyleSheet(
            'QSplitter::handle {background: #818A9A;}'
        )

        self.sideAreas = {self.Left: SideStackedContainer(), self.Right: SideStackedContainer(),
                          self.Bottom: BottomSideStackedContainer()}

        self.sideAreas[self.Left].hidePanelClicked.connect(self.hideSideBar)
        self.sideAreas[self.Right].hidePanelClicked.connect(self.hideSideBar)
        for sideArea in [self.sideAreas[self.Left], self.sideAreas[self.Right]]:
            sideArea.hide()

        self.sideAreas[self.Bottom].hidePanelClicked.connect(self.hideSideBar)
        self.sideAreas[self.Bottom].setStyleSheet(
            'QSplitter::handle {border: 1px solid #818A9A; border-bottom: none}'
        )
        self.tabContainer = TabContainer()
        self.tabContainer.setStyleSheet(
            'QTabWidget::pane {border-top: 1px solid #818A9A;top: -1px;}'
            ''
            'WebChatContainer * {background: white}'

            'QWidget {border: none;}'

            'QTabWidget::tab-bar {border-left: 1px solid #818A9A; background-color: #FFF;}'

            'QTabBar::tab {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,'
            'stop: 0 #DEDEDE, stop: 0.4 #D8D8D8,stop: 0.5 #D8D8D8, stop: 1.0 #DEDEDE);'
            'color: #000;border: 1px solid #818A9A;padding: 3px;margin: -1px 0 0 -1px;}'

            'QTabBar::tab:selected {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,'
            'stop: 0 #FFFFFF, stop: 0.4 #F4F4F4,''stop: 0.5 #F4F4F4, stop: 1.0 #D6D6D6);'
            'border-bottom: 1px solid #D6D6D6}'

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
        )

        #tab1 = WebChatContainer()
        #ab2 = WebChatContainer()
        #self.tabContainer.addTab(tab1, u'电子科大')
        #self.tabContainer.addTab(tab2, u'西南财大柳林')
        self.upMainArea.addWidget(self.sideAreas[self.Left])
        self.upMainArea.addWidget(self.tabContainer)
        self.upMainArea.addWidget(self.sideAreas[self.Right])

        self.mainArea = QSplitter(Qt.Vertical)
        self.mainArea.setStyleSheet(
            'QSplitter::handle {background: #818A9A;}'
        )
        self.mainArea.setChildrenCollapsible(False)
        self.mainArea.setHandleWidth(1)
        self.mainArea.setOpaqueResize(False)

        self.mainArea.addWidget(self.upMainArea)
        self.mainArea.addWidget(self.sideAreas[self.Bottom])

        mainAreaLayout = QHBoxLayout()
        mainAreaLayout.addWidget(self.choiceBars[self.Left])
        mainAreaLayout.addWidget(self.mainArea)
        mainAreaLayout.addWidget(self.choiceBars[self.Right])

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(self.statusBar, 0, Qt.AlignTop)
        mainLayout.addLayout(mainAreaLayout)
        mainLayout.addWidget(self.choiceBars[self.Bottom], 0, Qt.AlignBottom)
        self.setLayout(mainLayout)

        self.createVmListSidePanel()
        self.createHistorySidePanel()
        self.createMapSidePanel()
        self.createControlSidePanel()
        self.createLogSidePanel()
        self.loadSettings()

    def saveSettings(self):
        settings = QSettings()
        settings.beginGroup('MainArea')
        settings.beginGroup('Horizontal')
        settings.setValue('state', self.upMainArea.saveState())
        settings.endGroup()
        settings.beginGroup('Vertical')
        settings.setValue('state', self.mainArea.saveState())
        settings.endGroup()
        settings.endGroup()
        settings.beginGroup('ChoiceBar')
        for index in self.choiceBars:
            choiceBar = self.choiceBars[index]
            settings.setValue(choiceBar.objectName() + 'IndexOfChecked', choiceBar.indexOfChecked())
        settings.endGroup()

    def loadSettings(self):
        """必须在构造函数末尾处调用，以保证upMainArea、mainArea在使用前已经初始化，其他相关的widget也已填充"""
        settings = QSettings()
        stateMainArea = settings.value('MainArea/Vertical/state')
        if stateMainArea:
            self.mainArea.restoreState(stateMainArea)

        stateUpMainArea = settings.value('MainArea/Horizontal/state')
        if stateUpMainArea:
            self.upMainArea.restoreState(stateUpMainArea)

        for index in self.choiceBars:
            choiceBar = self.choiceBars[index]
            i = settings.value('ChoiceBar/' + choiceBar.objectName() + 'IndexOfChecked')
            try:
                i = int(i)
            except ValueError:
                continue
            if i != -1:
                choiceBar.setChecked(i)

    def createLogSidePanel(self):
        position = Workspace.Bottom
        logWindow = LogWindow()
        logWindow.setStyleSheet('border-top: 1px solid #818A9A; background: #FFF')
        Log.connect(logWindow)
        toolbar = ToolBar('日志')
        application.addToolBar(toolbar.id(), position, 0)
        container = SideContainer()
        container.setStyleSheet('SideContainer {border-top: 1px solid #818A9A;}')
        container.setToolBar(toolbar)
        container.setContentWidget(logWindow)
        logButton = ChoiceButton(u'日志', QIcon('images/logo.png'))
        self.addPanel(logButton, container, position, ChoiceBar.ChoiceBar_Bottom)

    def createVmListSidePanel(self):
        position = Workspace.Left
        vmList = VMList()
        vmList.startOrGotoVm.connect(self.startOrGotoVm)
        mapButton = ChoiceButton(u'虚拟机', QIcon('images/virtualbox.png'))
        container = SideContainer()
        container.setContentWidget(vmList)
        container.setStyleSheet(
            'QTreeView {border: none}'
        )
        toolbar = ToolBar('虚拟机')
        toolbar.setStyleSheet('ToolBar{border-bottom: 1px solid #818A9A}')
        application.addToolBar(toolbar.id(), position, 0)
        minimizeButton = ToolButton(u'最小化', QIcon('images/hide-left.png'))
        minimizeButton.clicked.connect(self.sideAreas[position].hidePanelClicked)
        refreshButton = ToolButton(u'刷新', QIcon('images/refresh.png'))
        toolbar.addButton(refreshButton)
        toolbar.addButton(minimizeButton)
        container.setToolBar(toolbar)
        self.addPanel(mapButton, container, position, ChoiceBar.ChoiceBar_Top)

    def createMapSidePanel(self):
        position = Workspace.Left
        maps = MapSidePanel()
        mapButton = ChoiceButton(u'地图', QIcon('images/map.png'))
        container = SideContainer()
        container.setContentWidget(maps)
        toolbar = ToolBar('地图')
        toolbar.setStyleSheet('ToolBar{border-bottom: 1px solid #818A9A}')
        application.addToolBar(toolbar.id(), position, 2)
        minimizeButton = ToolButton(u'最小化', QIcon('./images/hide-left.png'))
        minimizeButton.clicked.connect(self.sideAreas[position].hidePanelClicked)
        toolbar.addButton(minimizeButton)
        container.setToolBar(toolbar)
        self.addPanel(mapButton, container, position)

    def createHistorySidePanel(self):
        position = Workspace.Left
        gMap = GMap()
        mapButton = ChoiceButton(u'历史', QIcon('images/history.png'))
        container = SideContainer()
        container.setContentWidget(gMap)
        toolbar = ToolBar('历史')
        toolbar.setStyleSheet('ToolBar{border-bottom: 1px solid #818A9A}')
        application.addToolBar(toolbar.id(), position, 1)
        minimizeButton = ToolButton(u'最小化', QIcon('images/hide-left.png'))
        minimizeButton.clicked.connect(self.sideAreas[position].hidePanelClicked)
        toolbar.addButton(minimizeButton)
        container.setToolBar(toolbar)
        self.addPanel(mapButton, container, position)

    def createControlSidePanel(self):
        position = Workspace.Right
        panel = ControlSidePanel()
        controlButton = ChoiceButton(u'控制', QIcon('images/control.png'))
        container = SideContainer()
        container.setContentWidget(panel)
        toolbar = ToolBar('控制')
        toolbar.setStyleSheet('ToolBar{border-bottom: 1px solid #818A9A}')
        application.addToolBar(toolbar.id(), position, 0)
        minimizeButton = ToolButton(u'最小化', QIcon('images/hide-right.png'))
        minimizeButton.clicked.connect(self.sideAreas[position].hidePanelClicked)
        toolbar.addButton(minimizeButton)
        container.setToolBar(toolbar)
        self.addPanel(controlButton, container, position)

    @pyqtSlot(dict)
    def startOrGotoVm(self, info):
        index, tab = self.tabContainer.lookUpVmTab(info['vmId'])
        if not tab:
            msgBox = QMessageBox()
            msgBox.setText('是否真的要开启虚拟机?')
            msgBox.setInformativeText('虚拟机参数\n名称：{name}'.format(name=info['name']))
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret == QMessageBox.Ok:
                self.startNewVm(info)
        else:
            self.tabContainer.setCurrentWidget(tab, index)

    def startNewVm(self, info):
        webchat = WebChat(info['vmId'], info['vmType'], info['desc'])
        index, tab = self.tabContainer.lookUpVmSpace()
        tab.addWebchat(webchat)
        self.tabContainer.adjustTabName(tab)
        self.tabContainer.setCurrentWidget(tab, index)
        message = Message(cmd=Message.CMD_START_VM, vmId=info['vmId'])
        EventManager.trigger(Event('Client.replyReady.' + info['serverId'], message))

    def addPanel(self, choiceButton, sidePanel, position, buttonPosition=ChoiceBar.ChoiceBar_Top):
        self.addSidePanel(sidePanel, position)
        self.addChoiceButton(choiceButton, position, buttonPosition)

    def addSidePanel(self, sidePanel, position):
        sideArea = self.sideAreas[position]
        if position == self.Bottom:
            sidePanel.hide()
            sideArea.addWidget(sidePanel)
        elif position == self.Left:
            sideArea.addWidget(sidePanel)
        elif position == self.Right:
            sideArea.addWidget(sidePanel)

    def addChoiceButton(self, choiceButton, position, buttonPosition):
        self.choiceBars[position].addButton(choiceButton, buttonPosition)

    def hideSideBar(self):
        sender = self.sender()
        if sender == self.sideAreas[self.Left]:
            position = self.Left
        elif sender == self.sideAreas[self.Right]:
            position = self.Right
        elif sender == self.sideAreas[self.Bottom]:
            position = self.Bottom
        else:
            return
        self.choiceBars[position].unCheckAll()

    def changeCurrentSidePanel(self, index, checked):
        sender = self.sender()
        if sender == self.choiceBars[self.Left]:
            if checked:
                if self.sideAreas[self.Left].isHidden():
                    self.sideAreas[self.Left].show()
                self.sideAreas[self.Left].setCurrentIndex(index)
            else:
                if self.choiceBars[self.Left].isAllUnchecked():
                    self.sideAreas[self.Left].hide()
        elif sender == self.choiceBars[self.Right]:
            if checked:
                if self.sideAreas[self.Right].isHidden():
                    self.sideAreas[self.Right].show()
                self.sideAreas[self.Right].setCurrentIndex(index)
            else:
                if self.choiceBars[self.Right].isAllUnchecked():
                    self.sideAreas[self.Right].hide()
        elif sender == self.choiceBars[self.Bottom]:
            if checked:
                self.sideAreas[self.Bottom].widget(index).show()
            else:
                self.sideAreas[self.Bottom].widget(index).hide()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    b = Workspace()
    b.show()
    app.exec_()