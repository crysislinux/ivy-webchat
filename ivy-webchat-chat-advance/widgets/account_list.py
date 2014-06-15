# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import singleton
from application import EventManager, Event, Log
import application
from message import Message


class AccountList(QWidget):
    currentAccountChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.model = singleton.getAccountModel()
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        selectionModel = QItemSelectionModel(self.model)
        self.table.setSelectionModel(selectionModel)
        selectionModel.currentRowChanged.connect(self.loadCurrentAccount)

        header = self.table.horizontalHeader()
        #在针对某个section设置resizeMode前务必保证已经设置了model，否则view不知道有多少列，导致程序崩溃
        #header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        header.setSectionsClickable(False)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.table)
        self.setLayout(mainLayout)
        self.createContextMenu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.model.dataChanged.connect(self.editAccount)
        EventManager.bind('Message.addAccounts', self.addItems)
        EventManager.bind('Message.updateAccount', self.updateItem)
        EventManager.bind('Message.deleteAccounts', self.deleteItems)

    def editAccount(self, index, unused, roles):
        """同步修改到服务器"""
        if Qt.EditRole not in roles:
            self.table.update()
            return
        item = self.model.itemForIndex(index)
        resourceId = item.id()
        clientId = application.lookUpClientIdByResourceId(resourceId)
        if clientId:
            message = Message(cmd=Message.CMD_UPDATE_ACCOUNT)
            message['id'] = resourceId
            message['desc'] = item.description()
            message['username'] = item.username()
            message['password'] = item.password()
            EventManager.trigger(Event('Client.replyReady.' + clientId, message))
            toolBarId = application.lookUpToolBarIdByResourceId(resourceId)
            if toolBarId:
                print 'ToolBar.changeState.' + toolBarId
                EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, True))
        else:
            Log.e(u'未找到对应的服务器，修改失败')

    def loadCurrentAccount(self, current):
        item = self.model.itemForIndex(current)
        if item:
            self.currentAccountChanged.emit(
                {'desc': item.description(), 'username': item.username(), 'password': item.password()}
            )

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
        selection = self.table.selectionModel()
        indexes = selection.selectedRows()
        #uuids: {clientId: [uuid,]}
        uuids = {}
        for index in indexes:
            uuid_ = self.model.items[index.row()].id()
            clientId = application.lookUpClientIdByResourceId(uuid_)
            if clientId in uuids:
                uuids[clientId].append(uuid_)
            else:
                uuids[clientId] = [uuid_]
        if len(uuids) == 0:
            return
        for clientId in uuids:
            message = Message(cmd=Message.CMD_DELETE_ACCOUNT)
            message['ids'] = uuids[clientId]
            EventManager.trigger(Event('Client.replyReady.' + clientId, message))
            self.deleteItems(uuids[clientId])
            for uuid_ in uuids[clientId]:
                toolBarId = application.lookUpToolBarIdByResourceId(uuid_)
                if toolBarId:
                    EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, True))
                else:
                    Log.e(u'未找到对应的ToolBar')

    def addItem(self, item):
        self.addItems([item])

    def addItems(self, items):
        """items为一数组，每个元素是一个包含了一个账户信息的字典"""
        self.model.addItems(items)

    def deleteItems(self, ids):
        self.model.deleteItems(ids)

    def updateItem(self, info):
        self.model.updateItem(info)

    def sizeHint(self):
        return QSize(320, 480)

    def minimumSizeHint(self):
        return QSize(0, 0)


if __name__ == '__main__':
    app = singleton.getApplication()
    b = AccountList()
    b.addItems([{'id': 1, 'desc': '澳门', 'username': 'lg', 'password': '1234'},
                   {'id': 2, 'desc': '美国', 'username': 'lg', 'password': '1234'}])
    b.show()
    app.exec_()