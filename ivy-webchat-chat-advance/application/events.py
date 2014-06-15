# -*- coding: utf-8 -*-
from log import Log
from PyQt5.QtCore import *
import inspect


class Event(object):
    def __init__(self, source, *args, **kwargs):
        self.source = source
        self.args = args
        self.kwargs = kwargs


class RawEventManager(QObject):
    triggerCalled = pyqtSignal(Event)
    bindCalled = pyqtSignal(str, object)
    unbindCalled = pyqtSignal(str, object)

    blockingTriggerCalled = pyqtSignal(Event)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.handlers = []
        self.bindCalled.connect(self.handleBind, Qt.QueuedConnection)
        self.triggerCalled.connect(self.handleTrigger, Qt.QueuedConnection)
        self.unbindCalled.connect(self.handleUnbind, Qt.QueuedConnection)
        self.blockingTriggerCalled.connect(self.handleTrigger, Qt.DirectConnection)

    def bind(self, source, function):
        self.bindCalled.emit(source, function)

    def unbind(self, source, function=None):
        self.unbindCalled.emit(source, function)

    def trigger(self, event):
        self.triggerCalled.emit(event)

    def blockingTrigger(self, event):
        self.blockingTriggerCalled.emit(event)

    @pyqtSlot(str, object)
    def handleBind(self, source, function):
        for handler in self.handlers:
            if handler[0] == source and handler[1] == function:
                Log.i('%s has bind to %s' % (function.__name__, source))
                return
        self.handlers.append((source, function))

    @pyqtSlot(str, object)
    def handleUnbind(self, source, function=None):
        if function:
            for handler in self.handlers:
                if handler[0] == source and handler[1] == function:
                    self.handlers.remove(handler)
        else:
            for handler in self.handlers:
                if handler[0] == source:
                    self.handlers.remove(handler)

    @pyqtSlot(Event)
    def handleTrigger(self, event):
        source = event.source
        for handler in self.handlers:
            if handler[0] == source:
                function = handler[1]
                funcSpec = inspect.getargspec(function)
                if 'self' in funcSpec.args:
                    funcSpec.args.remove('self')
                arguments = []
                if len(event.args) < len(funcSpec.args):
                    Log.e('arguments too short')
                    return
                arguments.extend(event.args[0: len(funcSpec.args)])
                if funcSpec.varargs is not None:
                    arguments.extend(event.args[len(funcSpec.args):])
                if funcSpec.keywords is None:
                    function(*arguments)
                else:
                    function(*arguments, **event.kwargs)

__rawEventManager = RawEventManager()


def getRawEventManager():
    return __rawEventManager


class EventManager(QObject):
    @staticmethod
    def bind(source, function):
        getRawEventManager().bind(source, function)

    @staticmethod
    def unbind(source, function=None):
        getRawEventManager().unbind(source, function)

    @staticmethod
    def trigger(event):
        getRawEventManager().trigger(event)

    @staticmethod
    def blockingTrigger(event):
        getRawEventManager().blockingTrigger(event)


if __name__ == '__main__':

    class TestClass():
        def __init__(self):
            EventManager.bind('testEvent', self.testFunc)
            pass

        def testFunc(self, arg1, arg2):
            print('---------------')
            print(arg1, arg2)

    t = TestClass()
    t1 = TestClass()
    EventManager.unbind('testEvent')
    EventManager.trigger(Event('testEvent', 'arg1', 'arg2', 'arg4', arg3='arg3'))
    #EventManager.trigger(Event('testEvent', 'arg1', 'arg2', 'arg4', arg3='arg3'))