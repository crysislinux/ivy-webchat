# -*- coding: utf-8 -*-
from PyQt5.QtCore import *


class LogRaw(QObject):
    log = pyqtSignal(str, int)
    LOG_INFO = 0
    LOG_WARNING = 1
    LOG_ERROR = 2

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    def e(self, log):
        log = str(log)
        self.log.emit(log, self.LOG_ERROR)
        print('ERROR: ' + log)

    def w(self, log):
        log = str(log)
        self.log.emit(log, self.LOG_WARNING)
        print('WARNING: ' + log)

    def i(self, log):
        log = str(log)
        self.log.emit(log, self.LOG_INFO)
        print('INFO: ' + log)


__logRaw = LogRaw()


class Log():
    LOG_INFO = 0
    LOG_WARNING = 1
    LOG_ERROR = 2

    def __init__(self):
        pass

    @staticmethod
    def i(log):
        log = log
        logRaw = getLogRaw()
        logRaw.i(log)

    @staticmethod
    def w(log):
        log = log
        logRaw = getLogRaw()
        logRaw.w(log)

    @staticmethod
    def e(log):
        log = log
        logRaw = getLogRaw()
        logRaw.e(log)

    @staticmethod
    def connect(logObject):
        logRaw = getLogRaw()
        logRaw.log.connect(logObject.log)


def getLogRaw():
    return __logRaw
