# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from application import EventManager
import uuid


class ChoiceBar(QWidget):
    checkedChanged = pyqtSignal(int, bool)
    unchecked = pyqtSignal(int)

    ChoiceBar_Top = 0
    ChoiceBar_Bottom = 1

    def __init__(self, orientation=Qt.Vertical, parent=None):
        QWidget.__init__(self, parent)
        self.autoExclusive = False
        self.buttons = {}
        self.setOrientation(orientation)

    def setAutoExclusive(self, autoExclusive):
        self.autoExclusive = autoExclusive

    def setOrientation(self, orientation):
        try:
            if self.orientation:
                return
        except AttributeError:
            pass
        self.orientation = orientation
        if self.orientation == Qt.Vertical:
            mainLayout = QVBoxLayout()
            mainLayout.setContentsMargins(2, 1, 2, 1)
            mainLayout.setSpacing(4)
            self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding))
        else:
            mainLayout = QHBoxLayout()
            mainLayout.setContentsMargins(28, 2, 28, 1)
            mainLayout.setSpacing(4)
            self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.stretch = QWidget(self)
        self.stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mainLayout.addWidget(self.stretch)
        self.setLayout(mainLayout)

    def unCheckAll(self):
        for button in self.buttons:
            if button.isChecked():
                button.setAutoExclusive(False)
                button.setChecked(False)
                button.update()
                if self.autoExclusive:
                    button.setAutoExclusive(True)

    def isAllUnchecked(self):
        for button in self.buttons:
            if button.isChecked():
                return False
        return True

    def setChecked(self, index):
        """check索引为index的按钮"""
        if 0 <= index < len(self.buttons):
            self.unCheckAll()
            for button in self.buttons:
                if self.buttons[button] == index:
                    button.setChecked(True)
                    break

    def indexOfChecked(self):
        """检查checked状态的按钮索引，如果有按钮按下，返回该按钮的索引，否则返回-1"""
        for button in self.buttons:
            if button.isChecked():
                return self.buttons[button]
        return -1

    def addButton(self, button, position=ChoiceBar_Top):
        button.setOrientation(self.orientation)
        index = self.layout().indexOf(self.stretch)
        if position == self.ChoiceBar_Top:
            self.layout().insertWidget(index, button)
        elif position == self.ChoiceBar_Bottom:
            self.layout().insertWidget(index + 1, button)
        self.buttons[button] = len(self.buttons)
        button.toggled.connect(self.checkButton)
        button.unchecked.connect(self.unCheckButton)
        if self.autoExclusive:
            button.setAutoExclusive(True)

    def addSpacing(self, space):
        self.addSpacing(space)

    def addStretch(self):
        self.layout().addStretch()

    def checkButton(self, checked):
        sender = self.sender()
        for button in self.buttons:
            if button == sender:
                self.checkedChanged.emit(self.buttons[sender], checked)

    def unCheckButton(self):
        sender = self.sender()
        for button in self.buttons:
            if button == sender:
                self.unchecked.emit(self.buttons[sender])

    def paintEvent(self, e):
        painter = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)


class StatusIndicator(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.loadingGif = QMovie('images/busy.gif')
        self.loading = QLabel()
        self.loading.setMovie(self.loadingGif)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 1, 0, 0)
        mainLayout.addWidget(self.loading)
        self.setLayout(mainLayout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(QSize(14, 15))
        self.setStyleSheet(
            'background: transparent'
        )

    def start(self):
        self.loadingGif.start()

    def stop(self):
        self.loadingGif.stop()

    def sizeHint(self):
        return QSize(14, 15)


class ToolBar(QWidget):
    def __init__(self, title=None, parent=None):
        QWidget.__init__(self, parent)
        self._id = uuid.uuid4().hex
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        if title:
            self.setTitle(title)
        self.indicator = StatusIndicator()
        self.indicatorReference = 0
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.label, 0, Qt.AlignVCenter | Qt.AlignLeading)
        mainLayout.addWidget(self.indicator, 0, Qt.AlignVCenter | Qt.AlignLeft)
        mainLayout.addStretch()
        mainLayout.setContentsMargins(4, 4, 4, 4)
        mainLayout.setSpacing(5)
        self.setLayout(mainLayout)
        self.hideIndicator()
        EventManager.bind('ToolBar.changeState.' + self._id, self.changeIndicatorStatus)
        print 'ToolBar.changeState.' + self._id

    def id(self):
        return self._id

    def changeIndicatorStatus(self, show):
        if show:
            self.showIndicator()
            self.indicatorReference += 1
        else:
            self.indicatorReference -= 1
            if self.indicatorReference == 0:
                self.hideIndicator()

    def hideIndicator(self):
        self.indicator.stop()
        self.indicator.setVisible(False)

    def showIndicator(self):
        self.indicator.start()
        self.indicator.setVisible(True)

    def setTitle(self, title):
        self.label.setText(title)

    def addButton(self, button):
        self.layout().insertWidget(self.layout().count(), button)

    def paintEvent(self, e):
        painter = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

    def minimumSizeHint(self):
        return QSize(0, self.sizeHint().height())
