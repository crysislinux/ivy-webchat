# -*- coding: utf-8 -*-
from test.network_test import ClientManager
from PyQt5.QtWidgets import QApplication
import sys


app = QApplication(sys.argv)
cm = ClientManager()
cm.start()
cm.connectToServer(('127.0.0.1', 22333))

app.exec_()