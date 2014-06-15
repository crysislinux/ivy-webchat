# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from application import Log, getExceptionInfo, EventManager
import socket
import select
from Queue import Queue
from dispatcher_test import Dispatcher
from message import Message
import copy
import application


class Client(QObject):
    ReadError = 0
    NoMessage = 1
    NewMessage = 2
    UnknownMessage = 3
    WriteError = 4
    WriteSuccess = 5
    UnCompleteMessage = 6

    def __init__(self, inSocket, clientId, parent=None):
        QObject.__init__(self, parent)
        self.socket = inSocket
        self.replies = Queue()
        self.requests = Queue()
        self.clientId = clientId
        self.buf = bytes()

    def setClientId(self, clientId):
        """服务器与客户端之间的约定为仅设置clientId一次，否则需要修改资源管理器的行为"""
        self.clientId = clientId
        if self.clientId != -1:
            EventManager.bind('Client.replyReady.' + self.clientId, self.addReply)
            application.addResource([], self.clientId)

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
        if self.clientId != -1:
            EventManager.unbind('Client.replyReady.' + self.clientId)
        self.socket.close()

    def read(self):
        try:
            message = self.socket.recv(4096)
        except Exception as e:
            Log.e(getExceptionInfo(e))
            return Client.ReadError

        if len(message) == 0:
            return Client.NoMessage

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

        return Client.NewMessage

    def reply(self):
        reply = self.replies.get()
        reply.setParam(clientId=self.clientId)
        data = reply.dumps()
        if data:
            try:
                self.socket.send(bytes(str(len(data)).zfill(4)) + data)
                return self.WriteSuccess
            except Exception as e:
                Log.e("Can't send reply: " + getExceptionInfo(e))
                return self.WriteError


class ClientManager(QThread):
    clientDisconnected = pyqtSignal(str)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.address = None
        #clients --> {socket object: (address, identifier), }
        self.clients = {}
        self.dispatcher = Dispatcher(self)

    def setDispatcher(self, dispatcher):
        self.dispatcher = dispatcher

    def hasConnected(self, address):
        for client in self.clients:
            if self.clients[client][0] == address:
                return True

    def connectToServer(self, address):
        """address格式为(url, port)"""
        if self.hasConnected(address):
            Log.w('已经连接到服务器')
            return
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            clientSocket.connect(address)
            client = Client(clientSocket, -1)
            self.clients[client] = (address, -1)
            Log.i('成功连接到服务器')
            return True
        except Exception as e:
            Log.e(getExceptionInfo(e))

    def disConnectToServer(self, address):
        for client in self.clients:
            if self.clients[client][0] == address:
                client.close()
                del self.clients[client]
                Log.i('删除客户端: ' + str(self.clients[client][0]))

    def run(self):
        while True:
            brokenClients = []
            readers, writers = self.setFs()
            rList, wList, eList = select.select(readers, writers, [], 0.2)

            for client in self.clients:

                if client.getFd() in rList:
                    status = client.read()
                    if status == Client.ReadError:
                        Log.e('Socket read error')
                        brokenClients.append(client)

                    elif status == Client.NoMessage:
                        Log.i('No Message')
                        brokenClients.append(client)

                    elif status == Client.NewMessage:
                        Log.i('New Message')

                    else:
                        Log.e('Unknown socket status')

                if client.hasRequests():
                    self.treatMessage(client)

                if client.getFd() in wList:
                    status = client.reply()
                    if status == Client.WriteError:
                        Log.e('Socket write error with socket %s' % (self.clients[client][0], ))
                        if client not in brokenClients:
                            brokenClients.append(client)
                    elif status == Client.WriteSuccess:
                        Log.i('Send Message success')

            for client in brokenClients:
                Log.i('删除客户端: ' + str(self.clients[client][0]))
                client.close()
                del self.clients[client]
                self.clientDisconnected.emit(str(client.clientId))
                Log.i(self.clients)

    def setFs(self):
        readFs = []
        writeFs = []
        for client in self.clients:
            readFs.append(client.getFd())
            if client.hasReplies():
                writeFs.append(client.getFd())
        return readFs, writeFs

    def treatMessage(self, client):
        client.addReply(self.dispatcher.dispatchRequest(client))


from PyQt5.QtWidgets import *
class TestWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        cB1 = QPushButton(u'连接到22333')
        cB2 = QPushButton(u'连接到22334')
        layout = QHBoxLayout()
        layout.addWidget(cB1)
        layout.addWidget(cB2)
        self.cM = ClientManager()
        self.setLayout(layout)
        cB1.clicked.connect(self.connectToS1)
        cB2.clicked.connect(self.connectToS2)
        self.cM.start()

    def connectToS1(self):
        self.cM.connectToServer(('127.0.0.1', 22333))

    def connectToS2(self):
        self.cM.connectToServer(('127.0.0.1', 22334))

if __name__ == '__main__':
    from PyQt5.QtCore import *
    import sys
    app = QApplication(sys.argv)
    s = TestWindow()
    s.show()
    app.exec_()