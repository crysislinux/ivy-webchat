# -*- coding: utf-8 -*-

from external import ExternalManager
from webchat import WebchatManager
from data_center import DataCenter
from PyQt5.QtCore import *
import sys


app = QCoreApplication(sys.argv)
dC = DataCenter()
s = ExternalManager()
s.start()
w = WebchatManager()
w.start()
app.exec_()