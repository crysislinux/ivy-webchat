# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class ConfirmOperationDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)
        self.setWindowIcon(QIcon('../images/logo.png'))

    def setMessage(self):
        pass

    def setDetailMessage(self):
        pass


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    b = ConfirmOperationDialog()
    b.show()
    app.exec_()