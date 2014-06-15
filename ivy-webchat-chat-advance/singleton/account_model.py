# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from application import Log, Event, EventManager
import application


class AccountItem(object):
    def __init__(self, info):
        self._id = info['id']
        self._username = info['username']
        self._password = info['password']
        self._desc = info['desc']

    def id(self):
        return self._id

    def username(self):
        return self._username

    def password(self):
        return self._password

    def description(self):
        return self._desc

    def setDescription(self, desc):
        self._desc = desc

    def setUsername(self, username):
        self._username = username

    def setPassword(self, password):
        self._password = password


class AccountModel(QAbstractTableModel):
    Description = 0
    Username = 1
    Password = 2

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.items = []

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == AccountModel.Description:
                return u'备注'
            elif section == AccountModel.Username:
                return u'用户名'
            elif section == AccountModel.Password:
                return u'密码'
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def flags(self, index):
        theFlags = QAbstractTableModel.flags(self, index)
        if index.isValid():
            theFlags |= Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return theFlags

    def data(self, index, role=None):
        if not index.isValid() or index.column() < 0 or index.column() > self.columnCount():
            return QVariant()
        item = self.items[index.row()]
        if role == Qt.DisplayRole or role == Qt.EditRole:
            column = index.column()
            if column == AccountModel.Description:
                return item.description()
            elif column == AccountModel.Username:
                return str(item.username())
            elif column == AccountModel.Password:
                return str(item.password())
            else:
                Log.e('Unknown column index')

        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter

        return QVariant()

    def setData(self, index, value, role=None):
        if not index.isValid() | role == Qt.EditRole:
            return False
        item = self.itemForIndex(index)
        if not item:
            return False

        if index.column() == AccountModel.Description:
            item.setDescription(value)
        elif index.column() == AccountModel.Username:
            item.setUsername(value)
        elif index.column() == AccountModel.Password:
            item.setPassword(value)
        else:
            return False
        self.dataChanged.emit(index, index, [Qt.EditRole])
        return True

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 3

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.items)

    def addItems(self, items):
        if len(items) < 1:
            return
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + len(items) - 1)
        for item in items:
            item_ = AccountItem(item)
            self.items.append(item_)
            application.addItemToToolBar(item_.id(), 1, 0)
        self.endInsertRows()

    def deleteItem(self, id_):
        for row, item in enumerate(self.items):
            if item.id() != id_:
                continue
            self.beginRemoveRows(QModelIndex(), row, row)
            self.items.remove(item)
            self.endRemoveRows()

    def deleteItems(self, ids):
        if len(ids) < 1:
            return
        for id_ in ids:
            self.deleteItem(id_)

    def itemForIndex(self, index):
        if index.isValid():
            row = index.row()
            if 0 <= row < len(self.items):
                return self.items[row]

    def updateItem(self, info):
        id_ = info['id']
        for row, item in enumerate(self.gpsItems):
            if item.id() == id_:
                if 'desc' in info:
                    item.setDescription(info['desc'])
                    index = self.createIndex(row, AccountModel.Description)
                    self.dataChanged.emit(index, index, [Qt.DisplayRole])
                if 'username' in info:
                    item.setUsername(info['username'])
                    index = self.createIndex(row, AccountModel.Username)
                    self.dataChanged.emit(index, index, [Qt.DisplayRole])
                if 'password' in info:
                    item.setPassword(info['password'])
                    index = self.createIndex(row, AccountModel.Password)
                    self.dataChanged.emit(index, index, [Qt.DisplayRole])
                break