# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from widgets.side_panel import ResourceSidePanel, ControlSidePanel, InfoSidePanel
from widgets.bars import *


class WebChat(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setStyleSheet("WebChat{background-color: #FF0;}")
        self.setFixedSize(320, 480)

    def paintEvent(self, e):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def information(self):
        info = {'name': '电子科大', 'accounts': ('496724812', '872155134')}
        return info


class WebChatContainer(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.webChatPrimary = WebChat()
        self.webChatSecondary = WebChat()
        self.setStyleSheet('background-color: #D6D6D6')
       
        webChatsLayout = QHBoxLayout()
        webChatsLayout.addWidget(self.webChatPrimary)
        webChatsLayout.addWidget(self.webChatSecondary)
        w = QWidget()
        w.setLayout(webChatsLayout)
        s = QScrollArea()
        s.setWidget(w)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(s)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

    def information(self):
        info = {'name': '电子科大', 'accounts': ('496724812', '872155134')}
        return info

    def paintEvent(self, e):
        painter = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)


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

    def addTab(self, widget=None, name=None):
        if not widget:
            widget = WebChatContainer()
        if not name:
            name = u'未命名'
        self.tabWidget.addTab(widget, name)

    def closeTab(self, index):
        if self.tabWidget.count() == 1:
            return
        webChat = self.tabWidget.widget(index)
        msgBox = QMessageBox()
        msgBox.setText(u'是否真的要关闭: ' + self.tabWidget.tabText(index))
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        msgBox.setWindowTitle(u'关闭tab页')
        info = webChat.information()
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


class Workspace(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.statusBar = StatusBar()
        self.statusBar.setStyleSheet(
            'StatusBar {border-bottom: 1px solid #818A9A; background-color: #C2C2C2;}'
        )
        self.mainContent = QSplitter(Qt.Horizontal)
        self.mainContent.setChildrenCollapsible(False)
        self.mainContent.setHandleWidth(1)
        self.mainContent.setStyleSheet(
            'QSplitter::handle {background: #818A9A;}'
        )

        self.choiceBar = ChoiceBar()
        self.resourceSidePanel = ResourceSidePanel(self.choiceBar)

        self.mainContent.addWidget(self.choiceBar)
        self.mainContent.addWidget(self.resourceSidePanel)
        self.mainContent.handle(1).setDisabled(True)

        self.tabContainer = TabContainer()
        self.setStyleSheet(
            'QTabWidget::pane {border-top: 1px solid #818A9A;top: -1px;}'

            'QWidget {border: none;}'

            'QTabWidget::tab-bar {border-left: 1px solid #818A9A; background-color: #FFF;}'

            'QTabBar::tab {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,'
            'stop: 0 #DEDEDE, stop: 0.4 #D8D8D8,stop: 0.5 #D8D8D8, stop: 1.0 #DEDEDE);'
            'color: #000;border: 1px solid #818A9A;padding: 3px;margin: -1px 0 0 -1px;}'

            'QTabBar::tab:selected {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,'
            'stop: 0 #FFFFFF, stop: 0.4 #F4F4F4,''stop: 0.5 #F4F4F4, stop: 1.0 #D6D6D6);'
            'border-bottom: 1px solid #D6D6D6}'

            'QScrollBar:horizontal {border: 1px solid grey;height: 15px;border-bottom: none;padding: 1px 0;}'

            'QScrollBar:vertical {border: 1px solid grey;width: 15px;padding: 0 1px; border-right:none}'

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

        tab1 = WebChatContainer()
        tab2 = WebChatContainer()
        self.tabContainer.addTab(tab1, u'电子科大')
        self.tabContainer.addTab(tab2, u'西南财大')
        self.mainContent.addWidget(self.tabContainer)

        self.controlChoiceBar = ChoiceBar()
        self.controlSideBar = ControlSidePanel(self.controlChoiceBar)
        self.mainContent.addWidget(self.controlSideBar)
        self.mainContent.addWidget(self.controlChoiceBar)

        self.mainContent.setStretchFactor(0, 0)
        for i in range(self.mainContent.count()-2):
            self.mainContent.setStretchFactor(i+1, 1)

        self.vSplitter = QSplitter(Qt.Vertical)
        self.vSplitter.setChildrenCollapsible(False)
        self.vSplitter.setHandleWidth(1)
        self.vSplitter.setStyleSheet(
            'QSplitter::handle {background: #818A9A;}'
        )
        self.infoChoiceBar = ChoiceBar(Qt.Horizontal)
        self.infoSidePanel = InfoSidePanel(self.infoChoiceBar)
        self.vSplitter.addWidget(self.mainContent)
        self.vSplitter.addWidget(self.infoSidePanel)
        self.vSplitter.addWidget(self.infoChoiceBar)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.statusBar)
        mainLayout.addWidget(self.vSplitter)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    b = Workspace()
    b.show()
    app.exec_()