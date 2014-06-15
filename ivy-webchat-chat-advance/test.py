# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json


def testJson():
    params = {'ab': 1, 'array': [1, 2, '234'], 'dict': {'name': 'fasdf', 'id': 4}}
    print json.dumps(params)





if __name__ == '__main__':
    import sys
    #app = QApplication(sys.argv)
    #b = MainWindow()
    #b.show()
    #app.exec_()
    print type(testJson)