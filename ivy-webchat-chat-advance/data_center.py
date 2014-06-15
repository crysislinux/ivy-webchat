# -*- coding: utf-8 -*-
from PyQt5.QtCore import *

from application.database import Database
from application import EventManager, Event


class DataCenter(QObject):
    TABLE_SERVERS = 'servers'

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.workThread = QThread()
        self.worker = self.Worker()
        self.worker.moveToThread(self.workThread)
        self.workThread.start()

        self.controller = self.Controller()
        self.controller.dataCenterSetup.connect(self.worker.setupDatabase)
        self.controller.dataCenterSetup.emit()

        self.controller.addVM.connect(self.worker.addServer)
        self.controller.delVM.connect(self.worker.delServer)
        self.controller.loadAllVMs.connect(self.worker.loadAllServers)

        EventManager.bind('DataCenter.addServer', self.addServer)
        EventManager.bind('DataCenter.delServer', self.delServer)
        EventManager.bind('DataCenter.loadAllServers', self.loadAllServers)

    def addServer(self, name, desc):
        self.controller.addServer.emit(name, desc)

    def delServer(self, name):
        self.controller.delServer.emit(name)

    def loadAllServers(self):
        self.controller.loadAllServers.emit()

    class Controller(QObject):
        dataCenterSetup = pyqtSignal()

        addServer = pyqtSignal(str, str)
        delServer = pyqtSignal(int)
        loadAllServers = pyqtSignal()

        def __init__(self, parent=None):
            QObject.__init__(self, parent)

    class Worker(QObject):
        def __init__(self, parent=None):
            QObject.__init__(self, parent)

        @pyqtSlot()
        def setupDatabase(self):
            from collections import OrderedDict
            self.db = Database('chat-advance.db')
            if not self.db.createConnection():
                EventManager.trigger(Event('Database.databaseConnectionFail'))
                return
            if not self.db.isTableExist(DataCenter.TABLE_FRIENDS):
                self.db.createTable(DataCenter.TABLE_SERVERS, OrderedDict([('name', Database.TYPE_TEXT),
                                    ('url', Database.TYPE_TEXT), ('port', Database.TYPE_TEXT)]))

        @pyqtSlot(str, str)
        def addServer(self, name, desc):
            self.db.addRecord(DataCenter.TABLE_VMS, name=name, desc=desc)
            index = self.db.lastInsertRowId()
            EventManager.trigger(Event('DataCenter.ServerAdded', index, (name, desc)))

        @pyqtSlot(int)
        def delServer(self, index):
            self.db.delRecord(DataCenter.TABLE_VMS, id=index)

        @pyqtSlot()
        def loadAllServers(self):
            items = self.db.load(DataCenter.TABLE_VMS)
            EventManager.trigger(Event('DataCenter.allServersLoaded', items))


if __name__ == '__main__':
    from PyQt5.QtWidgets import *
    import sys

    class Test(QTextEdit):
        callbacksig = pyqtSignal(str)

        def __init__(self):
            QTextEdit.__init__(self)
            self.callbacksig.connect(self.setText)

        def test(self):
            EventManager.bind('DataCenter.settingLoaded.geo', self.callback)
            EventManager.trigger(Event('DataCenter.saveSetting', 'geo', '我们'))
            EventManager.trigger(Event('DataCenter.loadSetting', 'geo'))

        def callback(self, data):
            print(data)
            self.callbacksig.emit(data[0][2].decode('utf-8'))

    app = QApplication(sys.argv)
    d = DataCenter()
    t = Test()
    t.show()
    t.test()
    app.exec_()