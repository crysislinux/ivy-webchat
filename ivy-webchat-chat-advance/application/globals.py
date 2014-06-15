# -*- coding: utf-8 -*-
from PyQt5.QtCore import QReadWriteLock


_store = {}
_lock = QReadWriteLock()


class Globals(object):
    @staticmethod
    def getAttr(name):
        _lock.lockForRead()
        attr = _store[name] if name in _store else None
        _lock.unlock()
        return attr

    @staticmethod
    def setAttr(name, value=None):
        _lock.lockForWrite()
        if value:
            _store[name] = value
        elif name in _store:
            del _store[name]
        _lock.unlock()