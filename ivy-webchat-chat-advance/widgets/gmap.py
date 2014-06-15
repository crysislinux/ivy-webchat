# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtWebKitWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import resources
from widgets.buttons import ToolButton


class SearchBar(QLineEdit):
    searchClicked = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.searchButton = ToolButton('test', QIcon('images/search.png'), self)
        self.searchButton.setCursor(Qt.PointingHandCursor)
        self.searchButton.clicked.connect(self.searchClicked)
        self.setStyleSheet('QLineEdit{background-color: #FFF; color: #000; '
                           'border: 1px solid #D6D6D6; padding: 2px}')

    def resizeEvent(self, e):
        size = self.searchButton.sizeHint()
        self.searchButton.move(self.rect().right() - size.width() - 5,
                               (self.height() - size.height())/2)


class GMap(QWidget):
    locationSet = pyqtSignal(str, str, str)
    mapLoaded = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.webView = QWebView()
        self.webView.setUrl(QUrl('file:///home/lg/PycharmProjects/ivy-webchat-chat-advance/widgets/gmap.html'))
        self.api = GMapApi()
        self.mapLoadComplete = False
        self.attachWindowObject()
        self.webView.page().mainFrame().javaScriptWindowObjectCleared.connect(self.attachWindowObject)
        self.webView.page().mainFrame().loadFinished.connect(self.mapLoadOk)
        self.api.locationSet.connect(self.locationSet)

        self.searchInput = SearchBar()
        hLayout = QHBoxLayout()
        hLayout.addWidget(self.searchInput)
        self.searchInput.returnPressed.connect(self.searchPressed)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(hLayout)
        mainLayout.addWidget(self.webView)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        self.api.mapLoaded.connect(self.mapLoaded)
        self.searchInput.searchClicked.connect(self.searchPressed)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    @pyqtSlot()
    def attachWindowObject(self):
        frame = self.webView.page().mainFrame()
        frame.addToJavaScriptWindowObject('api', self.api)

    @pyqtSlot(bool)
    def mapLoadOk(self, ok):
        if ok:
            self.mapLoadComplete = True

    @pyqtSlot()
    def searchPressed(self):
        if not self.mapLoadComplete:
            return
        text = self.searchInput.text()
        if len(text) < 1:
            return
        self.api.searchPressed.emit(text)

    def loadLocation(self, *args):
        if len(args) == 1 and isinstance(args[0], dict):
            self.api.loadLocation.emit(str(args[0]['lng']), str(args[0]['lat']))
        elif len(args) == 2:
            self.api.loadLocation.emit(args[0], args[1])

    def sizeHint(self):
        return QSize(800, 600)

    def minimumSizeHint(self):
        return QSize(0, 0)


class GMapApi(QObject):
    searchPressed = pyqtSignal(str)
    locationSet = pyqtSignal(str, str, str)
    loadLocation = pyqtSignal(str, str)
    mapLoaded = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    @pyqtSlot(float, float, str)
    def setLocation(self, lat, lng, readable):
        self.locationSet.emit(str(round(lng, 6)), str(round(lat, 6)), readable)

    @pyqtSlot()
    def mapLoadOk(self):
        self.mapLoaded.emit()