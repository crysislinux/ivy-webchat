# -*- coding: utf-8 -*-
from network import ClientManager
from PyQt5.QtCore import *
from dispatcher import Dispatcher
from message import Message
from application import Log, EventManager, Event
import application


class ExternalDispatcher(Dispatcher):
    def __init__(self, clientManager, parent=None):
        Dispatcher.__init__(self, clientManager, parent)
        self.callbacks = {
            Message.CMD_CLIENT_VALIDATED: self.loadResources,

            Message.CMD_QUERY_VMS_OK: self.loadVms,
            Message.CMD_UPDATE_VM_OK: self.handleUpdateVmOk,
            Message.CMD_VM_START_OK: self.handleVmStartOk,
            Message.CMD_VM_START_FAIL: self.handleVmStartFail,
            Message.CMD_VM_UPDATED: self.updateVm,

            Message.CMD_QUERY_GPS_OK: self.loadGps,
            Message.CMD_ADD_GPS_OK: self.handleAddGpsOk,
            Message.CMD_UPDATE_GPS_OK: self.handleUpdateGpsOk,
            Message.CMD_GPS_UPDATED: self.updateGps,
            Message.CMD_GPS_ADDED: self.loadGps,
            Message.CMD_GPS_DELETED: self.deleteGps,
            Message.CMD_DELETE_GPS_OK: self.handleDeleteGpsOk,

            Message.CMD_ACCOUNT_ADDED: self.loadAccounts,
            Message.CMD_QUERY_ACCOUNT: self.loadAccounts,
            Message.CMD_QUERY_ACCOUNT_OK: self.loadAccounts,
            Message.CMD_ADD_ACCOUNT_OK: self.handleAddAccountOk,
            Message.CMD_DELETE_ACCOUNT_OK: self.handleDeleteAccountsOk,
            Message.CMD_ACCOUNT_DELETED: self.deleteAccounts
        }

    def handleUpdateAccountOk(self, request):
        pass

    def handleDeleteAccountsOk(self, request):
        ids = request['ids']
        for id_ in ids:
            toolBarId = application.lookUpToolBarIdByResourceId(id_)
            if toolBarId:
                EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, False))
            else:
                Log.e(u'未找到需要改变状态的ToolBar')
            application.delItemFromToolBar(id_)

    def handleAddAccountOk(self, request):
        toolBarId = application.lookUpToolBarIdByResourceId(request['id'])
        if toolBarId:
            EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, False))
        else:
            Log.e(u'未找到需要改变状态的ToolBar')

    def updateAccount(self, request):
        pass

    def deleteAccounts(self, request):
        ids = request['ids']
        EventManager.trigger(Event('Message.deleteAccounts', ids))

    def loadAccounts(self, request):
        accounts = request['accounts']
        clientId = request['clientId']
        for item in accounts:
            application.addResource(item['id'], clientId)
        EventManager.trigger(Event('Message.addAccounts', accounts))

    def handleDeleteGpsOk(self, request):
        ids = request['ids']
        for id_ in ids:
            toolBarId = application.lookUpToolBarIdByResourceId(id_)
            if toolBarId:
                EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, False))
            else:
                Log.e(u'未找到需要改变状态的ToolBar')
            application.delItemFromToolBar(id_)

    def handleUpdateGpsOk(self, request):
        toolBarId = application.lookUpToolBarIdByResourceId(request['id'])
        if toolBarId:
            EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, False))
        else:
            Log.e(u'未找到需要改变状态的ToolBar')

    def handleUpdateVmOk(self, request):
        toolBarId = application.lookUpToolBarIdByResourceId(request['vmId'])
        if toolBarId:
            EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, False))
        else:
            Log.e(u'未找到需要改变状态的ToolBar')

    def handleAddGpsOk(self, request):
        toolBarId = application.lookUpToolBarIdByResourceId(request['id'])
        if toolBarId:
            EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, False))
        else:
            Log.e(u'未找到需要改变状态的ToolBar')

    def deleteGps(self, request):
        ids = request['ids']
        EventManager.trigger(Event('Message.deleteGps', ids))

    def updateGps(self, request):
        EventManager.trigger(Event('Message.updateGps', request))

    def updateVm(self, request):
        request['serverId'] = request['clientId']
        EventManager.trigger(Event('Message.updateVm', request))

    def handleVmStartFail(self, request):
        EventManager.trigger(Event('Message.vmStartFail', request))
        Log.w(u'虚拟机启动失败')

    def handleVmStartOk(self, request):
        EventManager.trigger(Event('Message.vmStarted', request))

    def loadResources(self, request):
        """加载GPS坐标，虚拟机信息，账户，用户id"""
        clientId = request['clientId']
        vmMessage = Message(cmd=Message.CMD_QUERY_VMS)
        EventManager.trigger(Event('Client.replyReady.'+clientId, vmMessage))
        gpsMessage = Message(cmd=Message.CMD_QUERY_GPS)
        EventManager.trigger(Event('Client.replyReady.'+clientId, gpsMessage))
        accountMessage = Message(cmd=Message.CMD_QUERY_ACCOUNT)
        EventManager.trigger(Event('Client.replyReady.'+clientId, accountMessage))

    def loadGps(self, request):
        gps = request['gps']
        clientId = request['clientId']
        for item in gps:
            application.addResource(item['id'], clientId)
        EventManager.trigger(Event('Message.addGps', gps))

    def loadVms(self, request):
        vms = request['vms']
        clientId = request['clientId']
        pureVms = vms['vms']
        for name in pureVms:
            application.addResource(pureVms[name]['vmId'], clientId)
            application.addItemToToolBar(pureVms[name]['vmId'], 0, 0)
        EventManager.trigger(Event('Message.addVms', vms))

    def dispatchRequest(self, client):
        request = client.getRequest()
        cmd = request.getCMD()
        if cmd == Message.CMD_CLIENT_VALIDATED:
            client.setClientId(request['clientId'])
        if cmd in self.callbacks:
            request.setParam(clientId=client.clientId)
            funcs = self.callbacks[cmd]
            if isinstance(funcs, list):
                for index, func in enumerate(funcs):
                    if index == len(funcs) - 1:
                        return func(request)
                    else:
                        func(request)
            else:
                return self.callbacks[cmd](request)
        else:
            Log.w('未实现的命令: ' + str(cmd))


class ExternalManager(QObject):

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.clientManager = ClientManager()
        self.dispatcher = ExternalDispatcher(self.clientManager)
        self.clientManager.setDispatcher(self.dispatcher)

    def start(self):
        self.clientManager.start()
        self.loadServers()

    def loadServers(self):
        from application import Globals
        servers = Globals.getAttr('servers')
        if servers:
            for name in servers:
                self.clientManager.connectToServer(servers[name])


if __name__ == '__main__':
    from PyQt5.QtCore import *
    import sys
    from data_center import DataCenter
    app = QCoreApplication(sys.argv)
    dC = DataCenter()
    s = ExternalManager()
    s.start()
    app.exec_()