# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from gmap import GMap
from gps_list import GpsList
from account_list import AccountList
from application import Log, EventManager, Event
import application
from message import Message
import uuid


class SideContainer(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._tooBar = None
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

    def setContentWidget(self, widget):
        self.layout().addWidget(widget)

    def setToolBar(self, toolbar):
        self._tooBar = toolbar
        self.layout().insertWidget(0, toolbar, 0, Qt.AlignTop)

    def toolBar(self):
        return self._tooBar

    def paintEvent(self, e):
        painter = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)


class LocationEdit(QWidget):
    wantSaveLocation = pyqtSignal(dict)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.readableEdit = QLineEdit()
        self.readableEdit.setPlaceholderText(u'地图备注')
        self.readableEdit.setAlignment(Qt.AlignLeft)
        self.saveButton = QPushButton('保存')
        self.lngEdit = QLineEdit()
        self.lngEdit.setReadOnly(True)
        self.lngEdit.setPlaceholderText(u'地图经度')
        self.latEdit = QLineEdit()
        self.latEdit.setReadOnly(True)
        self.latEdit.setPlaceholderText(u'地图纬度')
        editLayout = QHBoxLayout()
        editLayout.setContentsMargins(2, 0, 2, 0)
        editLayout.addWidget(self.readableEdit)
        editLayout.addWidget(self.saveButton)
        posLayout = QHBoxLayout()
        posLayout.setContentsMargins(2, 0, 2, 0)
        posLayout.addWidget(self.lngEdit)
        posLayout.addWidget(self.latEdit)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addLayout(posLayout)
        mainLayout.addLayout(editLayout)
        self.setLayout(mainLayout)
        self.saveButton.clicked.connect(self.handleSaveClicked)

    def handleSaveClicked(self):
        readable = self.readableEdit.text()
        lng = self.lngEdit.text()
        lat = self.latEdit.text()
        if len(lng) > 0 and len(lat) > 0:
            resourceId = uuid.uuid4().hex
            gps = {'id': resourceId, 'desc': readable, 'lng': lng, 'lat': lat}
            self.wantSaveLocation.emit(gps)
            clientId = application.getRandomClientId()
            message = Message(cmd=Message.CMD_ADD_GPS)
            message['gps'] = gps
            if clientId:
                EventManager.trigger(Event('Client.replyReady.' + clientId, message))
                application.addResource(resourceId, clientId)
                toolBarId = application.lookUpToolBarIdByResourceId(resourceId)
                if toolBarId:
                    EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, True))
            else:
                Log.e(u'未找到对应的服务器，增加失败')
        else:
            Log.w(u'经度和纬度均不为空时才能保存')

    def addLocation(self, index, start, end):
        locations = []
        for row in range(start, end+1):
            item = self.gpsModel.gpsItems[row]
            locations.append({'desc': item.description(), 'lat': item.lat(), 'lng': item.lng()})

    def setData(self, *args):
        if len(args) == 1 and isinstance(args[0], dict):
            data = args[0]
            #self.readableEdit.setText(data['desc'])
            self.lngEdit.setText(str(data['lng']))
            self.latEdit.setText(str(data['lat']))
        elif len(args) == 3:
            self.readableEdit.setText(args[2])
            #地图侧的位置详细信息可能需要编辑，所以光标在最后一个字符后边
            #self.readableEdit.setCursorPosition(0)
            self.lngEdit.setText(str(args[0]))
            self.latEdit.setText(str(args[1]))


class MapSidePanel(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.gMap = GMap()
        self.locationEdit = LocationEdit()
        self.gpsList = GpsList()
        gpsLayout = QVBoxLayout()
        gpsLayout.setContentsMargins(0, 2, 0, 0)
        gpsLayout.addWidget(self.locationEdit)
        gpsLayout.addWidget(self.gpsList)

        widget = QWidget()
        widget.setLayout(gpsLayout)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self.gMap)
        self.splitter.addWidget(widget)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(self.splitter)
        self.setLayout(mainLayout)
        self.setStyleSheet(
            'QTableView{border-top: 1px solid #818A9A}'

            'QSplitter{background-color: #818A9A}'
        )
        self.gMap.locationSet.connect(self.locationEdit.setData)
        #self.gpsList.currentLocationChanged.connect(self.locationEdit.setData)
        self.gpsList.currentLocationChanged.connect(self.gMap.loadLocation)
        self.locationEdit.wantSaveLocation.connect(self.gpsList.addGpsItem)
        self.gMap.locationSet.connect(self.registerCurrentLocation)

    def registerCurrentLocation(self, *args):
        if len(args) == 1 and isinstance(args[0], dict):
            current = args[0]
        elif len(args) == 3:
            current = {'desc': args[2], 'lng': args[0], 'lat': args[1]}
        else:
            raise ValueError(u'参数个数不合法')
        EventManager.trigger(Event('Map.locationChanged', current))


class InfoPanel(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.vmName = QLineEdit()
        self.vmName.setPlaceholderText(u'虚拟机名称')
        self.vmDesc = QLineEdit()
        self.vmDesc.setPlaceholderText(u'虚拟机备注')
        self.readable = QLineEdit()
        self.readable.setPlaceholderText(u'详细位置')
        self.lat = QLineEdit()
        self.lat.setPlaceholderText(u'纬度')
        self.lng = QLineEdit()
        self.lng.setPlaceholderText(u'经度')

        for edit in (self.vmName, self.vmDesc, self.readable, self.lat, self.lng):
            edit.setReadOnly(True)

        vmLayout = QHBoxLayout()
        vmLayout.addWidget(self.vmName)
        vmLayout.addWidget(self.vmDesc)
        posLayout = QHBoxLayout()
        posLayout.addWidget(self.lng)
        posLayout.addWidget(self.lat)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(2, 6, 2, 6)
        mainLayout.addLayout(vmLayout)
        mainLayout.addLayout(posLayout)
        mainLayout.addWidget(self.readable)
        self.setLayout(mainLayout)

    def paintEvent(self, e):
        painter = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)


class OpPanel(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.restart = QPushButton(u'重启')
        self.detect = QPushButton(u'探测输入框')
        l1 = QHBoxLayout()
        l1.addWidget(self.restart)
        l1.addWidget(self.detect)
        l1.setContentsMargins(0, 0, 0, 0)
        w1 = QWidget()
        w1.setLayout(l1)

        self.readable = QLineEdit()
        self.readable.setPlaceholderText(u'详细位置')
        self.setLocation = QPushButton(u'设置位置')
        self.lat = QLineEdit()
        self.lat.setPlaceholderText(u'纬度')
        self.lng = QLineEdit()
        self.lng.setPlaceholderText(u'经度')

        for edit in (self.readable, self.lat, self.lng):
            edit.setReadOnly(True)
        l2 = QHBoxLayout()
        l2.addWidget(self.lng)
        l2.addWidget(self.lat)
        l3 = QHBoxLayout()
        l3.addWidget(self.readable)
        l3.addWidget(self.setLocation)
        locationLayout = QVBoxLayout()
        locationLayout.addLayout(l2)
        locationLayout.addLayout(l3)
        locationLayout.setContentsMargins(0, 0, 0, 0)
        w2 = QWidget()
        w2.setLayout(locationLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(w1)
        mainLayout.addWidget(w2)
        mainLayout.setContentsMargins(2, 10, 2, 6)
        self.setLayout(mainLayout)
        EventManager.bind('Map.locationChanged', self.syncLocationToMap)

    def syncLocationToMap(self, location):
        self.readable.setText(location['desc'])
        #这个位置的坐标详细位置为只读，所以光标初始设置在第一个字符前面
        self.readable.setCursorPosition(0)
        self.lng.setText(location['lng'])
        self.lat.setText(location['lat'])


class ControlInfo(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.infoPanel = InfoPanel()
        self.opPanel = OpPanel()
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.infoPanel)
        layout.addWidget(self.opPanel)
        layout.addStretch()
        self.setLayout(layout)

    def minimumSizeHint(self):
        return QSize(0, 0)

    def sizeHint(self):
        return QSize(0, 300)


class AccountEdit(QWidget):
    wantSaveAccount = pyqtSignal(dict)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.readableEdit = QLineEdit()
        self.readableEdit.setPlaceholderText(u'账户备注')
        self.readableEdit.setAlignment(Qt.AlignLeft)
        self.saveButton = QPushButton(u'保存')
        self.nameEdit = QLineEdit()
        self.nameEdit.setPlaceholderText(u'用户名')
        self.passwordEdit = QLineEdit()
        self.passwordEdit.setPlaceholderText(u'密码')
        editLayout = QHBoxLayout()
        editLayout.setContentsMargins(2, 0, 2, 0)
        editLayout.addWidget(self.readableEdit)
        editLayout.addWidget(self.saveButton)
        posLayout = QHBoxLayout()
        posLayout.setContentsMargins(2, 0, 2, 0)
        posLayout.addWidget(self.nameEdit)
        posLayout.addWidget(self.passwordEdit)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addLayout(posLayout)
        mainLayout.addLayout(editLayout)
        self.setLayout(mainLayout)
        self.saveButton.clicked.connect(self.handleSaveClicked)

    def handleSaveClicked(self):
        readable = self.readableEdit.text()
        username = self.nameEdit.text()
        password = self.passwordEdit.text()
        if len(username) > 0 and len(password) > 0:
            resourceId = uuid.uuid4().hex
            account = {'id': resourceId, 'desc': readable, 'username': username, 'password': password}
            self.wantSaveAccount.emit(account)
            clientId = application.getRandomClientId()
            message = Message(cmd=Message.CMD_ADD_ACCOUNT)
            message['account'] = account
            if clientId:
                EventManager.trigger(Event('Client.replyReady.' + clientId, message))
                application.addResource(resourceId, clientId)
                toolBarId = application.lookUpToolBarIdByResourceId(resourceId)
                if toolBarId:
                    EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, True))
            else:
                Log.e(u'未找到对应的服务器，增加失败')
        else:
            Log.w(u'用户名和密码均不为空时才能保存')

    def setData(self, *args):
        if len(args) == 1 and isinstance(args[0], dict):
            data = args[0]
            #self.readableEdit.setText(data['desc'])
            self.lngEdit.setText(str(data['lng']))
            self.latEdit.setText(str(data['lat']))
        elif len(args) == 3:
            self.readableEdit.setText(args[2])
            #地图侧的位置详细信息可能需要编辑，所以光标在最后一个字符后边
            #self.readableEdit.setCursorPosition(0)
            self.lngEdit.setText(str(args[0]))
            self.latEdit.setText(str(args[1]))


class ControlSidePanel(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.controlInfo = ControlInfo()

        self.accountEdit = AccountEdit()
        self.accountList = AccountList()
        accountLayout = QVBoxLayout()
        accountLayout.setContentsMargins(0, 2, 0, 0)
        accountLayout.addWidget(self.accountEdit)
        accountLayout.addWidget(self.accountList)
        w = QWidget()
        w.setLayout(accountLayout)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self.controlInfo)
        self.splitter.addWidget(w)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(self.splitter)
        self.setLayout(mainLayout)
        self.setStyleSheet(
            'InfoPanel {border-bottom: 1px solid #818A9A}'
            'QTableView{border-top: 1px solid #818A9A}'
        )
        self.currentWebchat = None
        EventManager.bind('Webchat.currentChanged', self.setCurrentWebchat)
        self.accountEdit.wantSaveAccount.connect(self.accountList.addItem)

    def setCurrentWebchat(self, webchat):
        if self.currentWebchat == webchat:
            return
        self.currentWebchat = webchat
        print 'set webchat', webchat


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    m = MapSidePanel()
    m.show()
    app.exec_()