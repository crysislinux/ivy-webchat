# -*- coding: utf-8 -*-
from test.network_test import Server
from PyQt5.QtWidgets import QApplication
import sys


app = QApplication(sys.argv)
server = Server(22333)
server.start()
app.exec_()