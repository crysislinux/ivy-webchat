# -*- coding: utf-8 -*-
from application import Log, getExceptionInfo
import binascii
import json


class Message():
    CMD_STATUS_OK = 0
    CMD_STATUS_FAIL = 1

    CMD_START_VM = 0
    CMD_CLOSE_VM = 1
    CMD_RESET_VM = 2
    CMD_QUERY_VMS = 3
    CMD_QUERY_GPS = 4
    CMD_UPDATE_GPS = 5
    CMD_UPDATE_VM = 6
    CMD_ADD_GPS = 7
    CMD_VERIFIED = 8
    CMD_DELETE_GPS = 8

    CMD_VM_START_OK = 1000
    CMD_VM_START_FAIL = 1001
    CMD_VM_CLOSE_OK = 1002
    CMD_VM_CLOSE_FAIL = 1003
    CMD_VM_ABORT = 1004
    CMD_CLIENT_VALIDATED = 1005
    CMD_RESET_VM_OK = 1006
    CMD_RESET_VM_FAIL = 1007
    CMD_VALIDATE_OK = 1008
    CMD_VALIDATE_FAIL = 1009
    CMD_QUERY_VMS_OK = 1010
    CMD_QUERY_VMS_FAIL = 1011
    CMD_QUERY_GPS_OK = 1012
    CMD_QUERY_GPS_FAIL = 1013
    CMD_ADD_GPS_OK = 1014
    CMD_ADD_GPS_FAIL = 1015
    CMD_UPDATE_GPS_OK = 1016
    CMD_UPDATE_GPS_FAIL = 1017
    CMD_UPDATE_VM_OK = 1018
    CMD_UPDATE_VM_FAIL = 1019
    CMD_VERIFIED_OK = 1020
    CMD_VERIFIED_FAIL = 1021
    CMD_VM_UPDATED = 1022
    CMD_GPS_UPDATED = 1023
    CMD_GPS_ADDED = 1024
    CMD_GPS_DELETED = 1025
    CMD_DELETE_GPS_OK = 1026
    CMD_DELETE_GPS_OK = 1027

    #命令执行结果 [2000, 3000)
    CMD_LOGIN_OK = 2000
    CMD_LOGIN_FAIL = 2001
    CMD_LOGOUT_OK = 2002
    CMD_LOGOUT_FAIL = 2003
    CMD_FIND_NEARBY_FRIENDS_OK = 2004
    CMD_FIND_NEARBY_FRIENDS_FAIL = 2005
    CMD_SET_GPS_OK = 2006
    CMD_SET_GPS_FAIL = 2007
    CMD_GO_BACK_OK = 2008
    CMD_ENTER_TEXT_OK = 2009
    CMD_ENTER_TEXT_FAIL = 2010
    CMD_UNIMPLEMENT = 2011
    CMD_TEXT_EDIT_CHANGED = 2012
    CMD_BRIDGE_BOOT_OK = 2013

    #由外部传入需要由Bridge处理的命令 [3000, 4000)
    CMD_BRIDGE_START = 3000
    CMD_SET_GPS_LAT = 3000
    CMD_SET_GPS_LNG = 3001
    CMD_BRIDGE_END = 4000

    #需要转送到Webchat的命令 [4000, 5000)
    CMD_WEBCHAT_START = 4000
    CMD_LOGIN = 4000
    CMD_LOGOUT = 4001
    CMD_FIND_NEARBY_FRIENDS = 4002
    CMD_GO_BACK = 4003
    CMD_ENTER_TEXT = 4004
    CMD_DETECT_TEXT_EDIT = 4005
    CMD_APPEND_TEXT = 4006
    CMD_WEBCHAT_END = 5000

    def __init__(self, **kwargs):
        self.params = {}
        self.setParam(**kwargs)

    def getParam(self, name):
        return self.__getitem__(name)

    def __contains__(self, key):
        return key in self.params

    def __getitem__(self, item):
        param = None
        try:
            param = self.params[item]
        except Exception as e:
            Log.e(getExceptionInfo(e))
        return param

    def __setitem__(self, key, value):
        if key in self.params:
            Log.w('覆盖已有参数: ' + key)
        self.params[key] = value

    def getCMD(self):
        return self.getParam('cmd')

    def setParam(self, **kwargs):
        for name in kwargs:
            self.__setitem__(name, kwargs[name])

    def removeParam(self, *args):
        for name in args:
            if name in self.params:
                del self.params[name]
            else:
                Log.w('试图删除不存在的参数: ' + name)

    def dumps(self):
        if 'cmd' not in self.params:
            Log.e('cmd不存在')
            return None
        message = json.dumps(self.params)
        Log.i('生成Message: ' + message)
        return bytes(message).encode('utf-8')

    def loads(self, message):
        try:
            message = message.decode('utf-8')
        except UnicodeError:
            Log.e('无法使用utf-8解码消息: ' + binascii.hexlify(message))
            return False
        try:
            self.params = json.loads(message)
            Log.i('成功解析Message: ' + str(self.params))
        except Exception as e:
            Log.e(getExceptionInfo(e))
            return False
        return True

    @staticmethod
    def vmStartOk(identifier):
        message = '{{"cmd": {cmd}, "identifier": "{identifier}"}}'
        return message.format(cmd=Message.CMD_VM_START_OK, identifier=identifier)

    @staticmethod
    def vmStartFail(identifier, errorCode):
        message = '{{"cmd": {cmd}, "identifier": "{identifier}", "errorCode": {errorCode}}}'
        return message.format(cmd=Message.CMD_VM_START_FAIL, identifier=identifier, errorCode=errorCode)

    @staticmethod
    def vmCloseOk(identifier):
        message = '{{"cmd": {cmd}, "identifier": "{identifier}"}}'
        return message.format(cmd=Message.CMD_VM_CLOSE_OK, identifier=identifier)

    @staticmethod
    def vmCloseFail(identifier, errorCode):
        message = '{{"cmd": {cmd}, "identifier": "{identifier}", "errorCode": {errorCode}}}'
        return message.format(cmd=Message.CMD_VM_START_FAIL, identifier=identifier, errorCode=errorCode)

if __name__ == '__main__':
    import uuid
    print(Message.vmStartOk(uuid.uuid4().hex))
    print(Message.vmStartFail(uuid.uuid4().hex, 4))
    print(Message.vmCloseOk(uuid.uuid4().hex))
    print(Message.vmCloseFail(uuid.uuid4().hex, 4))