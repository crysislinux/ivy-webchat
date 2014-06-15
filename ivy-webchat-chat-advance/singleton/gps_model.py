# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from application import Log, Event, EventManager
import application


class GpsItem(object):
    def __init__(self, info):
        self._id = info['id']
        self._lng = info['lng']
        self._lat = info['lat']
        self._desc = info['desc']

    def id(self):
        return self._id

    def lng(self):
        return self._lng

    def lat(self):
        return self._lat

    def description(self):
        return self._desc

    def setDescription(self, desc):
        self._desc = desc


class GpsModel(QAbstractTableModel):
    Description = 0
    Lng = 1
    Lat = 2

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.gpsItems = []

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == GpsModel.Description:
                return u'备注'
            elif section == GpsModel.Lng:
                return u'经度'
            elif section == GpsModel.Lat:
                return u'纬度'
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def flags(self, index):
        theFlags = QAbstractTableModel.flags(self, index)
        if index.isValid():
            theFlags |= Qt.ItemIsSelectable | Qt.ItemIsEnabled
            if index.column() == GpsModel.Description:
                theFlags |= Qt.ItemIsEditable
        return theFlags

    def data(self, index, role=None):
        if not index.isValid() or index.column() < 0 or index.column() > self.columnCount():
            return QVariant()
        item = self.gpsItems[index.row()]
        if role == Qt.DisplayRole or role == Qt.EditRole:
            column = index.column()
            if column == GpsModel.Description:
                return item.description()
            elif column == GpsModel.Lng:
                return str(item.lng())
            elif column == GpsModel.Lat:
                return str(item.lat())
            else:
                Log.e('Unknown column index')

        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter

        return QVariant()

    def setData(self, index, value, role=None):
        if not index.isValid() or index.column() != GpsModel.Description:
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

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 3

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.gpsItems)

    def addGpsItems(self, items):
        if len(items) < 1:
            return
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + len(items) - 1)
        for item in items:
            gpsItem = GpsItem(item)
            self.gpsItems.append(gpsItem)
            application.addItemToToolBar(gpsItem.id(), 0, 2)
        self.endInsertRows()

    def deleteGpsItem(self, id_):
        for row, item in enumerate(self.gpsItems):
            if item.id() != id_:
                continue
            self.beginRemoveRows(QModelIndex(), row, row)
            self.gpsItems.remove(item)
            self.endRemoveRows()

    def deleteGpsItems(self, ids):
        if len(ids) < 1:
            return
        for id_ in ids:
            self.deleteGpsItem(id_)

    def itemForIndex(self, index):
        if index.isValid():
            row = index.row()
            if 0 <= row < len(self.gpsItems):
                return self.gpsItems[row]

    def resetGps(self, info):
        gpsId = info['id']
        for row, item in enumerate(self.gpsItems):
            if item.id() == gpsId:
                if 'desc' in info:
                    item.setDescription(info['desc'])
                    index = self.createIndex(row, GpsModel.Description)
                    self.dataChanged.emit(index, index, [Qt.DisplayRole])
                    break