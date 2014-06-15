# -*- coding: utf-8 -*-

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from application import Log
import application


class VMItem(object):
    Status_Invalid = 0
    Status_Running = 1
    Status_Idle = 2

    Type_Unknown = -1
    Type_Stand = 0
    Type_Id_Extract = 1

    def __init__(self, name, identifier, _type, description, status, parent=None):
        self._name = name
        self._status = status
        self._description = description
        self._parent = parent
        self._children = []
        self._id = identifier
        self._type = _type
        if self._parent:
            self._parent.addChild(self)

    def name(self):
        return self._name

    def description(self):
        return self._description

    def status(self):
        return self._status

    def id(self):
        return self._id

    def type(self):
        return self._type

    def setName(self, name):
        self._name = name

    def setDescription(self, description):
        self._description = description

    def setStatus(self, status):
        self._status = status

    def parent(self):
        return self._parent

    def childAt(self, row):
        if 0 <= row < len(self._children):
            return self._children[row]
        else:
            return None

    def childCount(self):
        return len(self._children)

    def hasChildren(self):
        return len(self._children) > 0

    def children(self):
        return self._children

    def insertChild(self, row, item):
        item._parent = self
        self._children.insert(row, item)

    def rowOfChild(self, item):
        if item in self._children:
            return self._children.index(item)
        return None

    def addChild(self, item):
        item._parent = self
        self._children.append(item)

    def removeChild(self, row):
        if 0 <= row < len(self._children):
            item = self._children[row]
            item._parent = None
            self._children.remove(item)


class VMModel(QAbstractItemModel):
    Name = 0
    Type = 1
    Description = 2
    ColumnCount = 3

    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self.rootItem = VMItem('root', 'root', 'root, ''root', VMItem.Status_Invalid, None)
        self.serverIcon = QIcon('../images/android.png')
        self.vmIcon = QIcon('../images/virtualbox.png')

    def flags(self, index):
        theFlags = QAbstractItemModel.flags(self, index)
        if index.isValid():
            theFlags |= Qt.ItemIsSelectable | Qt.ItemIsEnabled
            item = self.itemForIndex(index)
            if item and item.parent() == self.rootItem:
                theFlags ^= Qt.ItemIsSelectable
            if index.column() == VMModel.Description:
                theFlags |= Qt.ItemIsEditable

        return theFlags

    def data(self, index, role=None):
        if not self.rootItem or not index.isValid() or index.column() < 0 or index.column() > VMModel.ColumnCount:
            return QVariant()
        item = self.itemForIndex(index)
        if role == Qt.DisplayRole or role == Qt.EditRole:
            column = index.column()
            if column == VMModel.Name:
                return item.name()
            elif column == VMModel.Type:
                return ('站街/聊天', '提取id')[item.type()] if item.type() != -1 else ''
            elif column == VMModel.Description:
                return item.description()
            else:
                Log.e('Unknown column index')

        if role == Qt.TextAlignmentRole:
            if index.column() == VMModel.Name:
                return Qt.AlignLeft | Qt.AlignVCenter
            else:
                return Qt.AlignCenter

        #if role == Qt.DecorationRole:
        #    if index.column() == VMModel.Name:
        #        if item.parent() == self.rootItem and self.serverIcon:
        #            return self.serverIcon
        #        elif self.vmIcon:
        #            return self.vmIcon

    def itemForIndex(self, index):
        if index.isValid():
            item = index.internalPointer()
            return item
        return self.rootItem

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == VMModel.Name:
                return u'服务器/虚拟机'
            elif section == VMModel.Type:
                return u'类型'
            elif section == VMModel.Description:
                return u'备注'
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QVariant()

    def rowCount(self, parent=None, *args, **kwargs):
        if parent.isValid() and parent.column() != 0:
            return 0
        parentItem = self.itemForIndex(parent)

        return parentItem.childCount() if parentItem else 0

    def columnCount(self, parent=None, *args, **kwargs):
        return 0 if parent.isValid() and parent.column() != 0 else VMModel.ColumnCount

    def index(self, row, column, parent=None, *args, **kwargs):
        if not self.rootItem or row < 0 or column < 0 or column >= VMModel.ColumnCount or \
                (parent.isValid() and parent.column() != 0):
            return QVariant()
        parentItem = self.itemForIndex(parent)
        item = parentItem.childAt(row)
        if item:
            return self.createIndex(row, column, item)
        return QModelIndex()

    def parent(self, index=None):
        if not index.isValid():
            return QModelIndex()
        childItem = self.itemForIndex(index)
        if childItem:
            parentItem = childItem.parent()
            if parentItem:
                if parentItem == self.rootItem:
                    return QModelIndex()
                grandParentItem = parentItem.parent()
                if grandParentItem:
                    row = grandParentItem.rowOfChild(parentItem)
                    return self.createIndex(row, 0, parentItem)
        return QModelIndex()

    def setData(self, index, value, role=None):
        if not index.isValid() or index.column() != VMModel.Description:
            return False
        item = self.itemForIndex(index)
        if item:
            if role == Qt.EditRole:
                item.setDescription(value)
            else:
                return False
            self.dataChanged.emit(index, index, [Qt.EditRole])
            return True
        return False

    def findServerById(self, serverId):
        servers = self.rootItem.children()
        for server in servers:
            if serverId == server.id():
                return server

    def findVmById(self, serverId, vmId):
        server = self.findServerById(serverId)
        if server:
            for vm in server.children():
                if vm.id() == vmId:
                    return vm

    def addVms(self, info):
        parent = QModelIndex()
        self.beginInsertRows(parent, self.rootItem.childCount(), self.rootItem.childCount())
        server = self.findServerById(info['serverId'])
        if not server:
            server = VMItem(info['name'], info['serverId'], -1, info['desc'] if 'desc' in info else '',
                            VMItem.Status_Idle, self.rootItem)
        vms = info['vms']
        for name in vms:
            VMItem(name, vms[name]['vmId'], vms[name]['vmType'], vms[name]['desc'] if 'desc' in vms[name] else '',
                   vms[name]['status'] if 'status' in vms[name] else VMItem.Status_Invalid, server)
        self.endInsertRows()

    def resetVm(self, info):
        serverId = info['serverId']
        vmId = info['vmId']
        servers = self.rootItem.children()
        for serverRow, server in enumerate(servers):
            if server.id() == serverId:
                vms = server.children()
                for vmRow, vm in enumerate(vms):
                    if vm.id() == vmId:
                        if 'status' in info:
                            vm.setStatus(info['status'])
                        if 'desc' in info:
                            vm.setDescription(info['desc'])
                        index = self.createIndex(vmRow, 0, vm)
                        self.dataChanged.emit(index, index, [Qt.DisplayRole])
                        break
                break
