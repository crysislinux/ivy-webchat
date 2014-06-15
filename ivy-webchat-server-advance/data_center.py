# -*- coding: utf-8 -*-
from PyQt5.QtCore import *

from application.database import Database
from application import EventManager, Event


class DataCenter(QObject):
    TABLE_GPS = 'gps'
    TABLE_ACCOUNT = 'account'
    TABLE_USER_ID = 'user_id'

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.workThread = QThread()
        self.worker = self.Worker()
        self.worker.moveToThread(self.workThread)
        self.workThread.start()

        self.controller = self.Controller()
        self.controller.dataCenterSetup.connect(self.worker.setupDatabase)
        self.controller.dataCenterSetup.emit()

        self.controller.wantToAddGps.connect(self.worker.addGps)
        self.controller.wantAllGps.connect(self.worker.loadAllGps)
        self.controller.updateGps.connect(self.worker.updateGps)
        self.controller.deleteGps.connect(self.worker.deleteGps)

        self.controller.addAccount.connect(self.worker.addAccount)
        self.controller.loadAllAccount.connect(self.worker.loadAllAccount)
        self.controller.deleteAccount.connect(self.worker.deleteAccount)

        EventManager.bind('DataCenter.addGps', self.addGps)
        EventManager.bind('DataCenter.loadAllGps', self.loadAllGps)
        EventManager.bind('DataCenter.updateGps', self.updateGps)
        EventManager.bind('DataCenter.deleteGps', self.deleteGps)

        EventManager.bind('DataCenter.addAccount', self.addAccount)
        EventManager.bind('DataCenter.loadAllAccount', self.loadAllAccount)
        EventManager.bind('DataCenter.deleteAccount', self.deleteAccount)

    def addAccount(self, id_, desc, username, password, clientId):
        self.controller.addAccount.emit(id_, desc, username, password, clientId)

    def loadAllAccount(self, clientId):
        self.controller.loadAllAccount.emit(clientId)

    def deleteAccount(self, ids, clientId):
        self.controller.deleteAccount.emit(ids, clientId)

    def deleteGps(self, ids, clientId):
        self.controller.deleteGps.emit(ids, clientId)

    def updateGps(self, gpsId, desc, clientId):
        self.controller.updateGps.emit(gpsId, desc, clientId)

    def addGps(self, uuid_, desc, lng, lat, clientId):
        self.controller.wantToAddGps.emit(uuid_, desc, lng, lat, clientId)

    def loadAllGps(self, clientId):
        self.controller.wantAllGps.emit(clientId)

    class Controller(QObject):
        dataCenterSetup = pyqtSignal()
        wantToAddGps = pyqtSignal(str, str, str, str, str)
        wantAllGps = pyqtSignal(str)
        updateGps = pyqtSignal(str, str, str)
        deleteGps = pyqtSignal(list, str)

        addAccount = pyqtSignal(str, str, str, str, str)
        loadAllAccount = pyqtSignal(str)
        deleteAccount = pyqtSignal(list, str)

        def __init__(self, parent=None):
            QObject.__init__(self, parent)

    class Worker(QObject):
        def __init__(self, parent=None):
            QObject.__init__(self, parent)

        @pyqtSlot()
        def setupDatabase(self):
            from collections import OrderedDict
            self.db = Database('server.db')
            if not self.db.createConnection():
                EventManager.trigger(Event('Database.databaseConnectionFail'))
                return
            if not self.db.isTableExist(DataCenter.TABLE_GPS):
                self.db.createTable(
                    DataCenter.TABLE_GPS, OrderedDict(
                        [('uuid', Database.TYPE_TEXT), ('desc', Database.TYPE_TEXT), ('lng', Database.TYPE_TEXT),
                         ('lat', Database.TYPE_TEXT)]
                    )
                )
            if not self.db.isTableExist(DataCenter.TABLE_ACCOUNT):
                self.db.createTable(
                    DataCenter.TABLE_ACCOUNT, OrderedDict(
                        [('uuid', Database.TYPE_TEXT), ('desc', Database.TYPE_TEXT), ('username', Database.TYPE_TEXT),
                         ('password', Database.TYPE_TEXT)]
                    )
                )

        @pyqtSlot(str, str, str, str, str)
        def addGps(self, uuid_, desc, lng, lat, clientId):
            self.db.addRecord(DataCenter.TABLE_GPS, uuid=uuid_, desc=desc, lng=lng, lat=lat)
            EventManager.trigger(Event('DataCenter.gpsAdded',
                                       {'id': uuid_, 'desc': desc, 'lng': lng, 'lat': lat}, clientId))

        @pyqtSlot(str, str, str, str, str)
        def addAccount(self, id_, desc, username, password, clientId):
            self.db.addRecord(DataCenter.TABLE_ACCOUNT, uuid=id_, desc=desc, username=username, password=password)
            EventManager.trigger(Event('DataCenter.accountAdded',
                                       {'id': id_, 'desc': desc, 'username': username, 'password': password}, clientId))

        @pyqtSlot(str)
        def loadAllGps(self, clientId):
            gps = self.db.load(DataCenter.TABLE_GPS)
            EventManager.trigger(Event('DataCenter.gpsLoaded', gps, clientId))

        @pyqtSlot(str)
        def loadAllAccount(self, clientId):
            accounts = self.db.load(DataCenter.TABLE_ACCOUNT)
            EventManager.trigger(Event('DataCenter.accountLoaded', accounts, clientId))

        @pyqtSlot(str, str, str)
        def updateGps(self, gpsId, desc, clientId):
            self.db.update(DataCenter.TABLE_GPS, 'desc', desc, uuid=gpsId)
            EventManager.trigger(Event('DataCenter.gpsUpdated', gpsId, desc, clientId))

        @pyqtSlot(list, str)
        def deleteGps(self, ids, clientId):
            for id_ in ids:
                self.db.delRecord(DataCenter.TABLE_GPS, uuid=id_)
            EventManager.trigger(Event('DataCenter.gpsDeleted', ids, clientId))

        @pyqtSlot(list, str)
        def deleteAccount(self, ids, clientId):
            for id_ in ids:
                self.db.delRecord(DataCenter.TABLE_ACCOUNT, uuid=id_)
            EventManager.trigger(Event('DataCenter.accountDeleted', ids, clientId))



if __name__ == '__main__':
    from PyQt5.QtWidgets import *
    import sys
    import uuid

    class Test(QTextEdit):

        def __init__(self):
            QTextEdit.__init__(self)

        def test(self):
            EventManager.trigger(Event('DataCenter.addGps', uuid.uuid4().hex, 'gps1', '67.123', '33.434'))
            EventManager.trigger(Event('DataCenter.addGps', uuid.uuid4().hex, 'gps2', '123.345', '32.12'))
            EventManager.trigger(Event('DataCenter.addGps', uuid.uuid4().hex, 'gps3', '123.4345', '53.32'))

        def callback(self, data):
            self.callbacksig.emit(data[0][2].decode('utf-8'))

    app = QApplication(sys.argv)
    d = DataCenter()
    t = Test()
    t.show()
    t.test()
    app.exec_()