# -*- coding: utf-8 -*-
from network import Server
from dispatcher import Dispatcher
from PyQt5.QtCore import *
from application import Log, Event, EventManager
from message import Message


class WebchatDispatcher(Dispatcher):
    def __init__(self, server, parent=None):
        Dispatcher.__init__(self, server, parent)

    def dispatchRequest(self, request):
        cmd = request.getCMD()
        if not cmd:
            Log.i('缺少cmd参数')
        identifier = request.getParam('identifier')
        EventManager.trigger(Event('Socket.addReply.' + identifier,
                                   request))


class WebchatManager(QObject):
    WEBCHAT_SERVER_PORT = 22334

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.server = Server(self.WEBCHAT_SERVER_PORT)
        self.dispatcher = WebchatDispatcher(self.server)
        self.server.setDispatcher(self.dispatcher)

    def start(self):
        self.server.start()


if __name__ == '__main__':
    from PyQt5.QtCore import *
    import sys
    app = QCoreApplication(sys.argv)
    s = WebchatManager()
    s.start()
    app.exec_()