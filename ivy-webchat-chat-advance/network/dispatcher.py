# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from application import Log


class Dispatcher(QObject):
    def __init__(self, clientManager, parent=None):
        QObject.__init__(self, parent)
        self.clientManger = clientManager

    #if has some reply
    def dispatchRequest(self, client):
        request = client.getRequest()
        Log.i('Default dispatcher: ' + str(request))
        Log.w('You need to setDispatcher for the Server')