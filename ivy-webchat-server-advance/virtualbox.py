# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from vboxapi import *
import time
from application import Log, getExceptionInfo
import uuid


class VmManager(QObject):
    Status_Invalid = 0
    Status_Running = 1
    Status_Idle = 2

    mgr = VirtualBoxManager(None, None)
    vbox = mgr.vbox
    Port_Begin = 5810
    Port_End = 5890
    Attr_Mutable = {'desc': ('vm_desc', '')}

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        #vmStore --> {vmId: {status: xx, type: xx, name: xx, desc: xx, password:xx, port:xx,
        # obj: VirtualMachine object}}
        self.vmsStore = {}

    def getIdlePort(self):
        for port in range(VmManager.Port_Begin, VmManager.Port_End):
            idle = True
            for vm in self.vmsStore:
                if port == self.vmsStore[vm]['port']:
                    idle = False
                    break
            if idle:
                return port

    def getAllMachines(self):
        return self.vmsStore

    def loadAllMachines(self):
        """遍历所有的虚拟机"""
        for m in self.mgr.getArray(self.vbox, 'machines'):
            vm = VirtualMachine()
            vmId = uuid.uuid4().hex
            vmInfo = vm.load(m.name, vmId, self.getIdlePort(), vmId[0:16])
            if vmInfo:
                self.vmsStore[vmId] = vmInfo

    def startMachine(self, vmId):
        success = False
        if vmId in self.vmsStore:
            if self.vmsStore[vmId]['status'] == VirtualMachine.Status_Idle:
                if self.vmsStore[vmId]['obj'].start():
                    self.vmsStore[vmId]['status'] = VirtualMachine.Status_Running
                    success = True
                else:
                    Log.e(u'虚拟机启动失败')
            else:
                Log.e(u'虚拟机不处于空闲状态')
        else:
            Log.e(u'未找到对应的虚拟机')
        return success, self.vmsStore[vmId]

    def closeMachine(self, vmId):
        success = False
        if vmId in self.vmsStore:
            if self.vmsStore[vmId]['status'] == VirtualMachine.Status_Running:
                if self.vmsStore[vmId]['obj'].close():
                    self.vmsStore[vmId]['status'] = VirtualMachine.Status_Idle
                    success = True
                else:
                    Log.e(u'虚拟机关闭失败')
            else:
                Log.e(u'虚拟机不处于运行状态')
        else:
            Log.e(u'未找到对应的虚拟机')
        return success, self.vmsStore[vmId]

    def resetMachine(self, vmId):
        success = False
        if vmId in self.vmsStore:
            if self.vmsStore[vmId]['status'] == VirtualMachine.Status_Running:
                if self.vmsStore[vmId]['obj'].reset():
                    success = True
                else:
                    Log.e(u'虚拟机关闭失败')
            else:
                Log.e(u'虚拟机不处于运行状态')
        else:
            Log.e(u'未找到对应的虚拟机')
        return success, self.vmsStore[vmId]

    def setGuestPropertyValue(self, vmId, key, value=None):
        if key not in VmManager.Attr_Mutable:
            return
        if vmId in self.vmsStore:
            if self.vmsStore[vmId]['obj'].setGuestPropertyValue(VmManager.Attr_Mutable[key][0], value):
                if key in self.vmsStore[vmId]:
                    self.vmsStore[vmId][key] = value if value else VmManager.Attr_Mutable[key][1]

    def getGuestPropertyValue(self, vmId, key):
        if vmId in self.vmsStore:
            if key in self.vmsStore[vmId]:
                return self.vmsStore[vmId][key]


class VirtualMachine(QObject):
    Status_Invalid = 0
    Status_Running = 1
    Status_Idle = 2

    Type_Stand = 0
    Type_Id_Extract = 1

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.mach = None
        self.session = None
        self.console = None
        self.vmInfo = None
        self.mgr = VirtualBoxManager(None, None)
        self.vbox = self.mgr.vbox

    def load(self, name, vmId, port, password):
        self.vmInfo = {'name': name, 'port': port, 'password': password, 'obj': self}
        try:
            self.mach = self.vbox.findMachine(name)
            desc = self.mach.getGuestPropertyValue('vm_desc')
            self.vmInfo['desc'] = str(desc) if desc else ''
            type_ = self.mach.getGuestPropertyValue('vm_type')
            if not type_ or int(type_) not in (VirtualMachine.Type_Stand, VirtualMachine.Type_Id_Extract):
                self.vmInfo['status'] = VirtualMachine.Status_Invalid
                self.vmInfo['type'] = -1
                return self.vmInfo
            self.vmInfo['type'] = int(type_)
            if self.mach.state == self.mgr.constants.MachineState_Running:
                self.vmInfo['status'] = VirtualMachine.Status_Running
                return self.vmInfo
            self.session = self.mgr.mgr.getSessionObject(self.vbox)
            self.mach.lockMachine(self.session, self.mgr.constants.LockType_Write)
            mutable = self.session.machine
            mutable.setGuestPropertyValue('vm_vmId', vmId)
            mutable.VRDEServer.setVRDEProperty('VNCPassword', str(password))
            mutable.VRDEServer.setVRDEProperty('TCP/Ports', str(port))
            mutable.VRDEServer.enabled = True
            mutable.saveSettings()
            self.session.unlockMachine()
        except Exception, e:
            Log.e(getExceptionInfo(e))
            return
        self.vmInfo['status'] = VirtualMachine.Status_Idle
        return self.vmInfo

    def setGuestPropertyValue(self, key, value=None):
        if not self.mach:
            return
        try:
            self.session = self.mgr.mgr.getSessionObject(self.vbox)
            self.mach.lockMachine(self.session, self.mgr.constants.LockType_Shared)
            mutable = self.session.machine
            mutable.setGuestPropertyValue(key, value)
            mutable.saveSettings()
            self.session.unlockMachine()
            return True
        except Exception, e:
            Log.e(getExceptionInfo(e))

    def getGuestPropertyValue(self, key):
        if not self.mach:
            return
        return self.mach.getGuestPropertyValue(key)

    def start(self):
        if self.mach is None:
            print u'虚拟机分配失败，无法启动'
        elif self.mach.state == self.mgr.constants.MachineState_Running:
            print u'虚拟机已经在运行中，不能重复启动'
        else:
            try:
                self.session = self.mgr.mgr.getSessionObject(self.vbox)
                self.progress = self.mach.launchVMProcess(self.session, "headless", "")
                self.progress.waitForCompletion(-1)
                self.console = self.session.console
                return True
            except Exception, e:
                Log.e(getExceptionInfo(e))

    def close(self):
        if self.session is None:
            print u'虚拟机未启动，无法关闭'
        elif self.console is not None:
            self.console.powerDown()
            time.sleep(1)
            self.session = None
            self.console = None
            print u'虚拟机关闭'
            return True
        else:
            print u'关闭错误'

    def reset(self):
        if self.session is None:
            print u'虚拟机未启动，无法重启'
        elif self.console is not None:
            self.console.reset()
            time.sleep(1)
            print u'虚拟机重启'
            return True
        else:
            print u'重启错误'

    def pause(self):
        if self.session is None:
            print u'虚拟机未启动，无法暂停'
        elif self.console is not None:
            if self.console.state == self.mgr.constants.MachineState_Running:
                self.console.pause()
            else:
                if self.console.state == self.mgr.constants.MachineState_Paused:
                    print u'虚拟机已经处于暂停状态'
                else:
                    print u'虚拟机不处于运行状态，无法暂停'
        else:
            print u'暂停错误'

    def resume(self):
        if self.session is None:
            print u'虚拟机未启动，无法恢复'
        elif self.console is not None:
            if self.console.state == self.mgr.constants.MachineState_Paused:
                self.console.resume()
            else:
                if self.console.state == self.mgr.constants.MachineState_Running:
                    print u'虚拟机已经处于运行状态'
                else:
                    print u'虚拟机不处于暂停状态，无法恢复'

        else:
            print u'恢复错误'
        pass


if __name__ == '__main__':
    from PyQt5.QtWidgets import *
    import sys
    app = QApplication(sys.argv)
    w = QWidget()
    w.show()
    vm = VmManager()
    vm.loadAllMachines()
    for index, vmId in enumerate(vm.vmsStore):
        if vm.vmsStore[vmId]['name'] == 'extract_id_test Clone':
            vm.setGuestPropertyValue(vmId, 'desc', u'english description 1')
            pass
    for index, vmId in enumerate(vm.vmsStore):
        if vm.vmsStore[vmId]['name'] == 'extract_id_test Clone':
            print vm.vmsStore[vmId]
    app.exec_()