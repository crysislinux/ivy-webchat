# -*- coding: utf-8 -*-
from network import Server
from PyQt5.QtCore import *
from dispatcher import Dispatcher
from message import Message
from application import Log, EventManager, Event, getExceptionInfo
from virtualbox import VmManager, VirtualMachine


class ExternalDispatcher(Dispatcher):
    def __init__(self, server, parent=None):
        Dispatcher.__init__(self, server, parent)
        self.vm = VmManager()
        self.vm.loadAllMachines()
        #externalToVm --> {clientId: [(vmId, vmInfo),]}
        self.externalToVm = {}
        self.callbacks = {
            Message.CMD_START_VM: self.startVM,
            Message.CMD_CLOSE_VM: self.closeVM,
            Message.CMD_RESET_VM: self.resetVM,
            Message.CMD_QUERY_VMS: self.queryVms,
            Message.CMD_QUERY_GPS: self.queryGPS,
            Message.CMD_UPDATE_VM: self.updateVm,
            Message.CMD_UPDATE_GPS: self.updateGps,
            Message.CMD_ADD_GPS: self.addGps,
            Message.CMD_DELETE_GPS: self.deleteGps,
            Message.CMD_ADD_ACCOUNT: self.addAccount,
            Message.CMD_QUERY_ACCOUNT: self.queryAccount,
            Message.CMD_DELETE_ACCOUNT: self.deleteAccount,
        }
        self.server.clientDisconnected.connect(self.clearVmForClient)
        EventManager.bind('DataCenter.gpsLoaded', self._sendGpsData)
        EventManager.bind('DataCenter.gpsUpdated', self._updateGpsData)
        EventManager.bind('DataCenter.gpsAdded', self._addGpsData)
        EventManager.bind('DataCenter.gpsDeleted', self._deleteGpsData)

        EventManager.bind('DataCenter.accountAdded', self._addAccountData)
        EventManager.bind('DataCenter.accountLoaded', self._sendAccountData)
        EventManager.bind('DataCenter.accountDeleted', self._deleteAccountData)

    def _deleteAccountData(self, ids, clientId):
        message = Message(cmd=Message.CMD_DELETE_ACCOUNT_OK, ids=ids)
        EventManager.trigger(Event('Socket.addReply.' + clientId, message))
        message = Message(cmd=Message.CMD_ACCOUNT_DELETED)
        message['ids'] = ids
        EventManager.trigger(Event('Message.broadcast', message, (clientId,)))

    def deleteAccount(self, request):
        clientId = request.getParam('clientId')
        if not clientId:
            Log.e('ExternalDispatcher.deleteAccount: 权限不足')
            return
        if clientId not in self.server.clients:
            Log.e('ExternalDispatcher.deleteAccount: 该客户端在服务器中不存在')
            return
        EventManager.trigger(Event('DataCenter.deleteAccount', request['ids'], clientId))

    def _sendAccountData(self, data, clientId):
        accounts = []
        for account in data:
            accounts.append({'id': account[1], 'desc': account[2], 'username': account[3], 'password': account[4]})
        message = Message(cmd=Message.CMD_QUERY_ACCOUNT_OK)
        message['accounts'] = accounts
        EventManager.trigger(Event('Socket.addReply.' + clientId, message))

    def queryAccount(self, request):
        clientId = request.getParam('clientId')
        if not clientId:
            Log.e('ExternalDispatcher.queryAccount: 权限不足')
            return
        if clientId not in self.server.clients:
            Log.e('ExternalDispatcher.queryAccount: 该客户端在服务器中不存在')
            return
        EventManager.trigger(Event('DataCenter.loadAllAccount', clientId))

    def _addAccountData(self, params, clientId):
        message = Message(cmd=Message.CMD_ADD_ACCOUNT_OK, id=params['id'])
        EventManager.trigger(Event('Socket.addReply.' + clientId, message))
        message = Message(cmd=Message.CMD_ACCOUNT_ADDED)
        accounts = [{'id': params['id'], 'desc': params['desc'], 'username': params['username'],
                    'password': params['password']}]
        message['accounts'] = accounts
        EventManager.trigger(Event('Message.broadcast', message, (clientId,)))

    def addAccount(self, request):
        clientId = request.getParam('clientId')
        account = request['account']
        if not clientId:
            Log.e('ExternalDispatcher.addAccount: 权限不足')
            return
        if clientId not in self.server.clients:
            Log.e('ExternalDispatcher.addAccount: 该客户端在服务器中不存在')
            return
        EventManager.trigger(
            Event('DataCenter.addAccount', account['id'], account['desc'], account['username'],
                  account['password'], clientId)
        )

    def _deleteGpsData(self, ids, clientId):
        message = Message(cmd=Message.CMD_DELETE_GPS_OK, ids=ids)
        EventManager.trigger(Event('Socket.addReply.' + clientId, message))
        message = Message(cmd=Message.CMD_GPS_DELETED)
        message['ids'] = ids
        EventManager.trigger(Event('Message.broadcast', message, (clientId,)))

    def deleteGps(self, request):
        clientId = request.getParam('clientId')
        if not clientId:
            Log.e('ExternalDispatcher.deleteGps: 权限不足')
            return
        if clientId not in self.server.clients:
            Log.e('ExternalDispatcher.deleteGps: 该客户端在服务器中不存在')
            return
        EventManager.trigger(Event('DataCenter.deleteGps', request['ids'], clientId))

    def _addGpsData(self, params, clientId):
        message = Message(cmd=Message.CMD_ADD_GPS_OK, id=params['id'])
        EventManager.trigger(Event('Socket.addReply.' + clientId, message))
        message = Message(cmd=Message.CMD_GPS_ADDED)
        gps = [{'id': params['id'], 'desc': params['desc'], 'lng': params['lng'], 'lat': params['lat']}]
        message['gps'] = gps
        EventManager.trigger(Event('Message.broadcast', message, (clientId,)))

    def addGps(self, request):
        clientId = request.getParam('clientId')
        gps = request['gps']
        if not clientId:
            Log.e('ExternalDispatcher.updateGps: 权限不足')
            return
        if clientId not in self.server.clients:
            Log.e('ExternalDispatcher.updateGps: 该客户端在服务器中不存在')
            return
        EventManager.trigger(
            Event('DataCenter.addGps', gps['id'], gps['desc'], gps['lng'], gps['lat'], clientId)
        )

    def _updateGpsData(self, gpsId, desc, clientId):
        message = Message(cmd=Message.CMD_UPDATE_GPS_OK, id=gpsId)
        EventManager.trigger(Event('Socket.addReply.' + clientId, message))
        message = Message(cmd=Message.CMD_GPS_UPDATED, id=gpsId, desc=desc)
        EventManager.trigger(Event('Message.broadcast', message, (clientId,)))

    def updateGps(self, request):
        clientId = request.getParam('clientId')
        if not clientId:
            Log.e('ExternalDispatcher.updateGps: 权限不足')
            return
        if clientId not in self.server.clients:
            Log.e('ExternalDispatcher.updateGps: 该客户端在服务器中不存在')
            return
        EventManager.trigger(Event('DataCenter.updateGps', request['id'], request['desc'], clientId))

    def updateVm(self, request):
        clientId = request.getParam('clientId')
        if not clientId:
            Log.e('ExternalDispatcher.updateVm: 权限不足')
            return
        if clientId not in self.server.clients:
            Log.e('ExternalDispatcher.updateVm: 该客户端在服务器中不存在')
        vmId = request['vmId']
        self.vm.setGuestPropertyValue(vmId, 'desc', request['desc'])
        message = Message(cmd=Message.CMD_UPDATE_VM_OK, vmId=vmId)
        EventManager.trigger(Event('Socket.addReply.' + clientId, message))
        message = Message(cmd=Message.CMD_VM_UPDATED, vmId=vmId, desc=request['desc'])
        EventManager.trigger(Event('Message.broadcast', message, (clientId,)))

    def _sendGpsData(self, data, clientId):
        gps_ = []
        for gps in data:
            gps_.append({'id': gps[1], 'desc': gps[2], 'lng': gps[3], 'lat': gps[4]})
        message = Message(cmd=Message.CMD_QUERY_GPS_OK)
        message['gps'] = gps_
        EventManager.trigger(Event('Socket.addReply.' + clientId, message))

    def queryGPS(self, request):
        clientId = request.getParam('clientId')
        if not clientId:
            Log.e('ExternalDispatcher.queryGps: 权限不足')
            return
        if clientId not in self.server.clients:
            Log.e('ExternalDispatcher.queryGps: 该客户端在服务器中不存在')
            return
        EventManager.trigger(Event('DataCenter.loadAllGps', clientId))

    def queryVms(self, request):
        clientId = request.getParam('clientId')
        if not clientId:
            Log.e('ExternalDispatcher.queryVms: 权限不足')
            return
        if clientId not in self.server.clients:
            Log.e('ExternalDispatcher.queryVms: 该客户端在服务器中不存在')
            return
        vms = self.vm.getAllMachines()
        vms_ = {}
        for index, vmId in enumerate(vms):
            vm = vms[vmId]
            vms_[vm['name']] = {'status': vm['status'], 'vmId': vmId, 'vmType': vm['type'], 'desc': vm['desc']}
        message = Message(cmd=Message.CMD_QUERY_VMS_OK)
        message['vms'] = {'name': '服务器', 'serverId': clientId, 'desc': '', 'vms': vms_}
        EventManager.trigger(Event('Socket.addReply.' + clientId, message))

    def clearVmForClient(self, clientId):
        if clientId in self.externalToVm:
            for vm in self.externalToVm[clientId]:
                success, vmInfo = self.vm.closeMachine(vm[0])
                if not success:
                    Log.e('关闭虚拟机失败:' + vm[1]['name'])
                    continue
                message = Message(cmd=Message.CMD_VM_UPDATED, vmId=vm[0], status=VirtualMachine.Status_Idle)
                EventManager.trigger(Event('Message.broadcast', message, ()))
            del self.externalToVm[clientId]

    def dispatchRequest(self, request):
        cmd = request.getCMD()
        if cmd in self.callbacks:
            self.callbacks[cmd](request)
        elif Message.CMD_BRIDGE_START <= cmd < Message.CMD_WEBCHAT_END:
            try:
                webchatId = request.getParam('webchatId')
                EventManager.trigger(Event('Socket.addReply.' + webchatId, request))
            except Exception as e:
                Log.e(getExceptionInfo(e))
        else:
            Log.w('未实现的命令: ' + str(cmd))

    def startVM(self, request):
        clientId = request.getParam('clientId')
        if not clientId:
            Log.e('ExternalDispatcher.startVM: 权限不足')
            return
        if clientId not in self.server.clients:
            Log.e('ExternalDispatcher.startVM: 该客户端在服务器中不存在')
            return

        vmId = request['vmId']
        success, vmInfo = self.vm.startMachine(vmId)
        if not success:
            Log.e("启动虚拟机失败")
            EventManager.trigger(Event('Socket.addReply.' + clientId,
                                       Message(cmd=Message.CMD_VM_START_FAIL, vmId=vmId)))
            return
        else:
            Log.i('成功启动虚拟机: ' + str(vmInfo['name']))
            if clientId in self.externalToVm:
                self.externalToVm[clientId].append((vmId, vmInfo))
            else:
                self.externalToVm[clientId] = [(vmId, vmInfo)]
            EventManager.trigger(Event('Socket.addReply.' + clientId,
                                       Message(cmd=Message.CMD_VM_START_OK, vmId=vmId, port=vmInfo['port'],
                                               password=vmInfo['password'])))
            message = Message(cmd=Message.CMD_VM_UPDATED, vmId=vmId, status=VirtualMachine.Status_Running)
            EventManager.trigger(Event('Message.broadcast', message, ()))

    def closeVM(self, request):
        clientId = request.getParam('clientId')
        if not clientId:
            Log.e('ExternalDispatcher.closeVM: 权限不足')
            return
        if clientId not in self.server.clients:
            Log.e('ExternalDispatcher.closeVM: 该客户端在服务器中不存在')
            return

        vmId = request.getParam('vmId')
        if not vmId:
            Log.e('ExternalDispatcher.closeVM: 缺少虚拟机Id参数')
            return

        for vm in self.externalToVm[clientId]:
            if vm[0] == vmId:
                success, vmInfo = self.vm.closeMachine(vmId)
                if not success:
                    break
                self.externalToVm[clientId].remove(vm)
                message = Message(cmd=Message.CMD_VM_UPDATED, vmId=vmId, status=VirtualMachine.Status_Idle)
                EventManager.trigger(Event('Message.broadcast', message, ()))
                return True
        Log.e("关闭虚拟机失败")

    def resetVM(self, request):
        clientId = request.getParam('clientId')
        if not clientId:
            Log.e('ExternalDispatcher.resetVM: 权限不足')
            return
        if clientId not in self.server.clients:
            Log.e('ExternalDispatcher.closeVM: 该客户端在服务器中不存在')
            return

        vmId = request.getParam('vmId')
        if not vmId:
            Log.e('ExternalDispatcher.resetVM: 缺少虚拟机Id参数')
            return

        for vm in self.externalToVm[clientId]:
            if vm[1] == vmId:
                if not self.vm.resetMachine(vmId):
                    break
                EventManager.trigger(Event('Socket.addReply.' + clientId,
                                           Message(cmd=Message.CMD_RESET_VM_OK)))
                return True
        Log.e("重启虚拟机失败")


class ExternalManager(QObject):
    EXTERNAL_SERVER_PORT = 22333

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.server = Server(self.EXTERNAL_SERVER_PORT)
        self.dispatcher = ExternalDispatcher(self.server)
        self.server.setDispatcher(self.dispatcher)

    def start(self):
        self.server.start()


if __name__ == '__main__':
    from PyQt5.QtCore import *
    import sys
    from data_center import DataCenter
    app = QCoreApplication(sys.argv)
    dC = DataCenter()
    s = ExternalManager()
    s.start()
    app.exec_()