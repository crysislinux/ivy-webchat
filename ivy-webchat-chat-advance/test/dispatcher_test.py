# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from application import Log, EventManager, Event
from message import Message


class Dispatcher(QObject):
    def __init__(self, server, parent=None):
        QObject.__init__(self, parent)
        self.server = server

    #if has some reply
    def dispatchRequest(self, client):
        Log.i('Default dispatcher: ' + str(client))
        Log.w('You need to setDispatcher for the Server')
        request = client.getRequest()
        cmd = request.getCMD()
        if cmd == Message.CMD_CLIENT_VALIDATED:
            client.setClientId(request['clientId'])
        message = Message(cmd=Message.CMD_QUERY_GPS, id=1)
        EventManager.trigger(Event('Client.replyReady.' + client.clientId, message))
        message = Message(cmd=Message.CMD_QUERY_GPS, id=2)
        EventManager.trigger(Event('Client.replyReady.' + client.clientId, message))
        message = Message(cmd=Message.CMD_QUERY_GPS, id=3)
        EventManager.trigger(Event('Client.replyReady.' + client.clientId, message))
        message = Message(cmd=Message.CMD_QUERY_GPS, id=4)
        EventManager.trigger(Event('Client.replyReady.' + client.clientId, message))
