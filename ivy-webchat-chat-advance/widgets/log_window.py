# -*- coding: utf-8 -*-

import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from application import Log


class LogWindow(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)
        #上下文菜单等待实现，设置contextMenu策略为CustomContextMenu后默认的QTextEdit上下文菜单被覆盖
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    @pyqtSlot(str, int)
    def log(self, log, level):
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        log = now + ': ' + log
        if level == Log.LOG_ERROR:
            self.append('<font color="#DC143C">' + log + '</font>')
        elif level == Log.LOG_WARNING:
            self.append('<font color="#9370DB">' + log + '</font>')
        else:
            self.append('<font color="#2E8B57">' + log + '</font>')
        c = self.textCursor()
        c.movePosition(QTextCursor.End)
        self.setTextCursor(c)

    def event(self, e):
        if e.type() == QEvent.KeyPress or e.type() == QEvent.KeyRelease:
            return True
        return QTextEdit.event(self, e)