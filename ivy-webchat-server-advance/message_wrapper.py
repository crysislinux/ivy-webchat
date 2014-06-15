# -*- coding: utf-8 -*-
from application import Log, getExceptionInfo
import json
import binascii


class Request():
    def __init__(self):
        self.request = {}

    def getParam(self, name):
        param = None
        try:
            param = self.request[name]
        except Exception as e:
            Log.e(getExceptionInfo(e))
        return param

    def getCMD(self):
        return self.getParam('cmd')

    def loads(self, message):
        try:
            message = message.decode('utf-8')
        except UnicodeError:
            Log.e('无法使用utf-8解码消息: ' + binascii.hexlify(message))
            return False
        try:
            self.request = json.loads(message)
            Log.i('成功解析Request: ' + str(self.request))
        except Exception as e:
            Log.e(getExceptionInfo(e))
            return False
        return True

    def dumps(self):
        reply = '{'
        if 'cmd' not in self.request:
            Log.e('cmd不存在')
            return None
        else:
            for count, name in enumerate(self.request):
                if count > 0:
                    reply += ', '
                reply += '"{name}": '.format(name=name)
                value = self.request[name]
                if isinstance(value, basestring):
                    reply += '"{value}"'.format(value=value)
                else:
                    reply += str(value)
        reply.rstrip(' ')
        reply += '}'
        Log.i('生成Reply: ' + reply)
        self.reply = bytes(reply).encode('utf-8')
        return self.reply


class Reply():
    def __init__(self, **kwargs):
        self.params = {}
        self.reply = None
        self.setParam(**kwargs)

    def setParam(self, **kwargs):
        for name in kwargs:
            if name in self.params:
                Log.w('覆盖已有参数: ' + name)
            self.params[name] = kwargs[name]

    def removeParam(self, *args):
        for name in args:
            if name in self.params:
                del self.params[name]
            else:
                Log.w('试图删除不存在的参数: ' + name)

    def dumps(self):
        reply = '{'
        if 'cmd' not in self.params:
            Log.e('cmd不存在')
            return None
        else:
            for count, name in enumerate(self.params):
                if count > 0:
                    reply += ', '
                reply += '"{name}": '.format(name=name)
                value = self.params[name]
                if isinstance(value, str) or isinstance(value, unicode):
                    reply += '"{value}"'.format(value=value)
                else:
                    reply += str(value)
        reply.rstrip(' ')
        reply += '}'
        Log.i('生成Reply: ' + reply)
        self.reply = bytes(reply).encode('utf-8')
        return self.reply

    def loadFromMessage(self, message):
        self.reply = bytes(message).encode('utf-8')

    def getData(self):
        if self.reply:
            return self.reply

if __name__ == '__main__':
    r = Reply()
    r.setParam(cmd=1, test='test')
    r.setParam(cmd=1, test='test1')
    rq = Request()
    rq.loads(r.dumps())
    print rq.getCMD()
    print rq.getParam('test2')