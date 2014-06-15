# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from application import Log, getExceptionInfo, Event, EventManager
import socket
import select
import uuid
from Queue import Queue
from dispatcher_test import Dispatcher
from message_test import Message
import copy


class Server(QThread):
    clientIn = pyqtSignal(socket.socket)
    clientDisconnected = pyqtSignal(str)

    def __init__(self, port, parent=None):
        QThread.__init__(self, parent)
        self.port = port
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind(('', self.port))
        self.serverSocket.listen(5)
        self.serverSocket.setblocking(False)
        self.dispatcher = Dispatcher(self)
        #clients --> {clientId: Socket object}
        self.clients = {}
        EventManager.bind('Message.broadcast', self.broadcast)

    def broadcast(self, message, exception=()):
        for clientId in self.clients:
            if clientId not in exception:
                EventManager.trigger(Event('Socket.addReply.' + clientId, message))

    def setDispatcher(self, dispatcher):
        self.dispatcher = dispatcher

    def stop(self):
        self.serverSocket.shutdown(socket.SHUT_RDWR)
        self.serverSocket.close()

    def getFd(self):
        return self.serverSocket

    def run(self):
        while True:
            brokenClients = []
            readers, writers = self.setFs()
            rList, wList, eList = select.select(readers, writers, [], 0.2)
            if self.getFd() in rList:
                self.acceptNewClient()
            for identifier in self.clients:
                if self.clients[identifier].getFd() in rList:
                    status = self.clients[identifier].read()
                    if status == Socket.ReadError:
                        Log.e('Socket read error')
                        brokenClients.append(identifier)

                    elif status == Socket.NoMessage:
                        Log.i('No Message')
                        brokenClients.append(identifier)

                    elif status == Socket.NoMessage:
                        Log.i('New Message')

                if self.clients[identifier].hasRequests():
                    self.treatMessage(self.clients[identifier])

                if self.clients[identifier].getFd() in wList:
                    status = self.clients[identifier].reply()
                    if status == Socket.WriteError:
                        Log.e('Socket write error with socket %s' % (identifier, ))
                        if identifier not in brokenClients:
                            brokenClients.append(identifier)
                    elif status == Socket.WriteSuccess:
                        Log.i('Send Message success')

            for identifier in brokenClients:
                Log.i('删除客户端: ' + str(identifier))
                self.clients[identifier].close()
                del self.clients[identifier]
                self.clientDisconnected.emit(identifier)
                Log.i(self.clients)

    def acceptNewClient(self):
        Log.i('connect in')
        s, addr = self.serverSocket.accept()
        if not s:
            Log.e('Cannot accept connection')
            return
        identifier = uuid.uuid4().hex
        self.clients[identifier] = Socket(s, identifier)
        self.clients[identifier].addReply(Message(cmd=Message.CMD_CLIENT_VALIDATED, clientId=identifier))
        Log.i(self.clients)

    def setFs(self):
        readFs = []
        writeFs = []
        readFs.append(self.getFd())
        for identifier in self.clients:
            readFs.append(self.clients[identifier].getFd())
            if self.clients[identifier].hasReplies():
                writeFs.append(self.clients[identifier].getFd())
        return readFs, writeFs

    def treatMessage(self, client):
        request = client.getRequest()
        client.addReply(self.dispatcher.dispatchRequest(request))


class Socket(QObject):
    ReadError = 0
    NoMessage = 1
    NewMessage = 2
    UnknownMessage = 3
    WriteError = 4
    WriteSuccess = 5
    UnCompleteMessage = 6

    def __init__(self, inSocket, identifier, parent=None):
        QObject.__init__(self, parent)
        self.socket = inSocket
        self.replies = Queue()
        self.requests = Queue()
        self.identifier = identifier
        self.buf = bytes()
        EventManager.bind('Socket.addReply.' + self.identifier, self.addReply)

    def addReply(self, reply):
        if reply:
            self.replies.put(reply)

    def hasReplies(self):
        if self.replies.qsize() > 0:
            return True
        else:
            return False

    def getFd(self):
        return self.socket

    def hasRequests(self):
        if self.requests.qsize() > 0:
            return True
        else:
            return False

    def getRequest(self):
        return self.requests.get()

    def close(self):
        EventManager.unbind('Socket.addReply.' + self.identifier)
        self.socket.close()

    def read(self):
        try:
            message = self.socket.recv(4096)
        except Exception as e:
            Log.e(getExceptionInfo(e))
            return Socket.ReadError

        if len(message) == 0:
            return Socket.NoMessage

        self.buf += message

        while len(self.buf) > 4:
            length = int(self.buf[0:4])
            if not len(self.buf) >= length + 4:
                break
            msg = self.buf[4: length + 4]
            self.buf = self.buf[length + 4:]
            message = Message()
            if not message.loads(msg):
                Log.w(u'Unknown Message')
            else:
                self.requests.put(message)

        return Socket.NewMessage

    def reply(self):
        reply = self.replies.get()
        data = reply.dumps()
        if data:
            try:
                self.socket.send(bytes(str(len(data)).zfill(4)) + data)
                return self.WriteSuccess
            except Exception as e:
                Log.e("Can't send reply: " + getExceptionInfo(e))
                return self.WriteError


if __name__ == '__main__':
    from PyQt5.QtCore import *
    import sys
    app = QCoreApplication(sys.argv)
    s = Server(22333)
    s.start()
    app.exec_()