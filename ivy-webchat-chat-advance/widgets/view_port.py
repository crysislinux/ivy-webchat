# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.vncview import VncView


class ViewPort(QWidget):
    actionApplied = pyqtSignal()
    mouseLeftButtonClicked = pyqtSignal()

    def __init__(self, url=None, parent=None):
        QWidget.__init__(self, parent)
        self.vncView = VncView(None, QUrl(url))
        self.vncView.installEventFilter(self)
        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(self.vncView)
        self.setLayout(mainLayout)
        self.setFixedSize(QSize(320, 480))
        self.vncView.mouseLeftButtonClicked.connect(self.mouseLeftButtonClicked)
        #self.vncView.mouseLeftButtonClicked.connect(self.actionApplied)
        #self.vncView.keyPressed.connect(self.actionApplied)
        #self.actionApplied.connect(self.actionAppliedTest)

    def actionAppliedTest(self):
        print("action")

    def setUrl(self, url):
        self.vncView.setUrl(url)

    def restart(self):
        self.vncView.restart()

    def start(self):
        self.vncView.start()

    def sizeHint(self):
        return QSize(320, 480)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    v = ViewPort("vnc://:1234@127.0.0.1:1234")
    v.show()
    v.start()
    app.exec_()