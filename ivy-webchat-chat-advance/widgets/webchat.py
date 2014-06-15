# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from view_port import ViewPort
from application import EventManager, Event
from message import Message
from widgets.buttons import ToolButton


class Loading(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.loadingGif = QMovie('images/loading.gif')
        self.loading = QLabel()
        self.loading.setMovie(self.loadingGif)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.loading)
        self.setLayout(mainLayout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(QSize(100, 100))
        self.setStyleSheet(
            'background: transparent'
        )

    def start(self):
        self.loadingGif.start()

    def stop(self):
        self.loadingGif.stop()

    def sizeHint(self):
        return QSize(100, 100)


class Branding(QWidget):
    Effect_Fade = 0
    Effect_Slide_X_Up = 1
    Effect_Slide_X_Down = 2
    Effect_Slide_Y_Up = 3
    Effect_Slide_Y_Down = 4

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.text = QLabel(self)
        self.text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.closeButton = ToolButton(u'关闭', QIcon('images/close.png'), self)
        self.durationTimer = QTimer()
        self.durationTimer.setSingleShot(True)
        self.durationTimer.timeout.connect(self.hideBranding)
        self.effect = None
        self.duration = 5000
        self.fps = 30
        self.effectTimer = QTimer()
        self.effects = {
            Branding.Effect_Fade: (self.fadeIn, self.fadeOut),
            Branding.Effect_Slide_Y_Down: (self.slideInYDown, self.slideOutYUp)
        }
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(0)
        self.setStyleSheet(
            'background: #F00'
        )

    def setText(self, text):
        if self.durationTimer.isActive():
            self.durationTimer.stop()
            self.text.setText(text)
            self.durationTimer.start(self.duration)
        else:
            self.text.setText(text)

    def setEffect(self, effect):
        self.effect = effect

    def setDuration(self, duration):
        self.duration = duration

    def showBranding(self):
        if self.effect in self.effects:
            pass
        else:
            self.effect = Branding.Effect_Slide_Y_Down
        self.effectTimer.timeout.connect(self.effects[self.effect][0])
        self.durationTimer.start(self.duration)
        self.effectTimer.start(200/self.fps)

    def hideBranding(self):
        #self.effectTimer.timeout.connect(self.effects[self.effect][1])
        #self.effectTimer.start(1000/self.fps)
        print 'hide'

    def slideInYDown(self):
        try:
            self.slideInYUpCount += 1
        except AttributeError:
            self.slideInYUpCount = 1
        step = self.sizeHint().height()/self.fps
        self.setFixedHeight(step*self.slideInYUpCount)
        if step*(self.slideInYUpCount+1) > self.sizeHint().height():
            self.effectTimer.stop()

    def resizeEvent(self, e):
        size_ = self.text.size()
        self.text.move(0, (self.height() - size_.height())/2)

    def slideOutYUp(self):
        pass

    def fadeIn(self):
        pass

    def fadeOut(self):
        pass

    def sizeHint(self):
        return QSize(self.fontMetrics().width(self.text.text()), 40)

    def paintEvent(self, e):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)


class WebChat(QWidget):
    focused = pyqtSignal()

    def __init__(self, vmId, type_, name, parent=None):
        QWidget.__init__(self, parent)
        self._vmId = vmId
        self._type = type_
        self._name = name
        self.loading = Loading(self)
        self.loading.start()
        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(8, 8, 8, 8)
        self.setLayout(mainLayout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(QSize(336, 496))

    def createVncViewPort(self, params):
        url = 'vnc://:' + params['password'] + '@127.0.0.1:' + str(params['port'])
        self.viewPort = ViewPort(url)
        self.viewPort.start()
        self.viewPort.mouseLeftButtonClicked.connect(self.focused)
        self.layout().addWidget(self.viewPort)

    def mousePressEvent(self, e):
        self.focused.emit()
        return QWidget.mousePressEvent(self, e)

    def resizeEvent(self, e):
        size_ = self.loading.size()
        self.loading.move((self.width() - size_.width())/2,
                          self.height()*0.4 - size_.height()/2)

    def name(self):
        return self._name

    def vmId(self):
        return self._vmId

    def type(self):
        return self._type

    def paintEvent(self, e):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def information(self):
        info = {'name': '电子科大', 'accounts': ('496724812', '872155134')}
        return info

    def sizeHint(self):
        return QSize(336, 496)


class WebChatContainer(QWidget):
    webchatRemoved = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.webchats = []
        self.maxWebchatCount = 2
        self.current = None
        self.webChatsLayout = QHBoxLayout()
        self.webChatsLayout.setContentsMargins(8, 8, 8, 8)
        self.webChatsLayout.setSpacing(8)
        self.container = QWidget()
        self.container.setLayout(self.webChatsLayout)
        s = QScrollArea()
        s.setWidget(self.container)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(s)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

    def setCurrent(self, index):
        if index == -1:
            self.current = None
            EventManager.trigger(Event('Webchat.currentChanged', self.current))
            return
        self.webchats[index].setStyleSheet("WebChat{background-color: #b2d235;}")
        self.current = self.webchats[index]
        for i, webchat in enumerate(self.webchats):
            if i != index:
                self.webchats[i].setStyleSheet("WebChat{background-color: #FF0;}")
        EventManager.trigger(Event('Webchat.currentChanged', self.current))

    def handleFocused(self):
        sender = self.sender()
        if self.current == sender:
            return
        index = self.webchats.index(sender)
        self.setCurrent(index)
            
    def getCurrent(self):
        return self.current

    def information(self):
        info = {'name': '电子科大', 'accounts': ('496724812', '872155134')}
        return info

    def removeWebchat(self, webchat):
        """外部会保证webchat在webChatsLayout中"""
        self.webChatsLayout.removeWidget(webchat)
        self.webchats.remove(webchat)
        if self.current == webchat:
            self.setCurrent(len(self.webchats)-1)
        self.container.setFixedSize(
            QSize(webchat.width() * len(self.webchats) + self.webChatsLayout.spacing() * (len(self.webchats) - 1)
                  + self.webChatsLayout.contentsMargins().right() + self.webChatsLayout.contentsMargins().left(),
                  webchat.height() + self.webChatsLayout.contentsMargins().top()
                  + self.webChatsLayout.contentsMargins().bottom()))
        self.webchatRemoved.emit(webchat.vmId())

    def addWebchat(self, webchat):
        if self.hasSpace():
            self.webchats.append(webchat)
            self.container.setFixedSize(
                QSize(webchat.width() * len(self.webchats) + self.webChatsLayout.spacing() * (len(self.webchats) - 1)
                      + self.webChatsLayout.contentsMargins().right() + self.webChatsLayout.contentsMargins().left(),
                      webchat.height() + self.webChatsLayout.contentsMargins().top()
                      + self.webChatsLayout.contentsMargins().bottom()))
            webchat.focused.connect(self.handleFocused)
            self.webChatsLayout.addWidget(webchat)
            webchat.focused.emit()

    def hasSpace(self):
        if len(self.webchats) < self.maxWebchatCount:
            return True

    def spaceIndex(self):
        if self.hasSpace():
            return len(self.webchats)

    def paintEvent(self, e):
        painter = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)