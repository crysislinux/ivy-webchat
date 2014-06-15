# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import singleton
from application import EventManager, Event, Log
import application
from message import Message


class GpsList(QWidget):
    currentLocationChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.gpsModel = singleton.getGpsModel()
        self.gpsTable = QTableView()
        self.gpsTable.setModel(self.gpsModel)
        self.gpsTable.setSelectionBehavior(QTableView.SelectRows)
        self.gpsTable.setFocusPolicy(Qt.NoFocus)
        self.gpsTable.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        selectionModel = QItemSelectionModel(self.gpsModel)
        self.gpsTable.setSelectionModel(selectionModel)
        selectionModel.currentRowChanged.connect(self.loadCurrentPosition)

        header = self.gpsTable.horizontalHeader()
        #在针对某个section设置resizeMode前务必保证已经设置了model，否则view不知道有多少列，导致程序崩溃
        #header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        header.setSectionsClickable(False)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.gpsTable)
        self.setLayout(mainLayout)
        self.createContextMenu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.gpsModel.dataChanged.connect(self.editLocation)
        EventManager.bind('Message.addGps', self.addGpsItems)
        EventManager.bind('Message.updateGps', self.resetGps)
        EventManager.bind('Message.deleteGps', self.deleteGpsItems)

    def editLocation(self, index, unused, roles):
        """同步修改到服务器，对于GPS坐标来说，客户端只能更改坐标备注"""
        if Qt.EditRole not in roles:
            self.gpsTable.update()
            return
        item = self.gpsModel.itemForIndex(index)
        resourceId = item.id()
        clientId = application.lookUpClientIdByResourceId(resourceId)
        if clientId:
            message = Message(cmd=Message.CMD_UPDATE_GPS)
            message['id'] = resourceId
            message['desc'] = item.description()
            EventManager.trigger(Event('Client.replyReady.' + clientId, message))
            toolBarId = application.lookUpToolBarIdByResourceId(resourceId)
            if toolBarId:
                print 'ToolBar.changeState.' + toolBarId
                EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, True))
        else:
            Log.e(u'未找到对应的服务器，修改失败')

    def loadCurrentPosition(self, current):
        item = self.gpsModel.itemForIndex(current)
        if item:
            self.currentLocationChanged.emit({'desc': item.description(), 'lng': item.lng(), 'lat': item.lat()})

    def showContextMenu(self, pos):
        self.contextMenu.exec_(self.mapToGlobal(pos))

    def createContextMenu(self):
        self.contextMenu = QMenu()
        delete = QAction(QIcon('./images/delete.png'), u'删除', self)
        delete.triggered.connect(self.deleteSelectedItems)
        refresh = QAction(QIcon('./images/refresh.png'), u'刷新', self)
        self.contextMenu.addActions([delete, refresh])
        #self.addGpsItems([{'id': 1, 'desc': '澳门', 'lat': '27.059126', 'lng': 110.390625},
        #                  {'id': 2, 'desc': '美国', 'lat': 36.597889, 'lng': 90.351563}])

    def deleteSelectedItems(self):
        selection = self.gpsTable.selectionModel()
        indexes = selection.selectedRows()
        #uuids: {clientId: [uuid,]}
        uuids = {}
        for index in indexes:
            uuid_ = self.gpsModel.gpsItems[index.row()].id()
            clientId = application.lookUpClientIdByResourceId(uuid_)
            if clientId in uuids:
                uuids[clientId].append(uuid_)
            else:
                uuids[clientId] = [uuid_]
        if len(uuids) == 0:
            return
        for clientId in uuids:
            message = Message(cmd=Message.CMD_DELETE_GPS)
            message['ids'] = uuids[clientId]
            EventManager.trigger(Event('Client.replyReady.' + clientId, message))
            self.deleteGpsItems(uuids[clientId])
            for uuid_ in uuids[clientId]:
                toolBarId = application.lookUpToolBarIdByResourceId(uuid_)
                if toolBarId:
                    EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, True))
                else:
                    Log.e(u'未找到对应的ToolBar')

    def addGpsItem(self, item):
        self.addGpsItems([item])

    def addGpsItems(self, items):
        """items为一数组，每个元素是一个包含了一个gps坐标信息的字典"""
        self.gpsModel.addGpsItems(items)

    def deleteGpsItems(self, ids):
        self.gpsModel.deleteGpsItems(ids)

    def resetGps(self, info):
        self.gpsModel.resetGps(info)

    def sizeHint(self):
        return QSize(320, 480)

    def minimumSizeHint(self):
        return QSize(0, 0)


if __name__ == '__main__':
    app = singleton.getApplication()
    b = GpsList()
    b.addGpsItems([{'id': 1, 'desc': '澳门', 'lat': 234.123, 'lng': 212.124},
                   {'id': 2, 'desc': '美国', 'lat': 234.123, 'lng': 212.124}])
    b.show()
    app.exec_()