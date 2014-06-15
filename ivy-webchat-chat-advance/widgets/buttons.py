# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class ChoiceButton(QAbstractButton):
    unchecked = pyqtSignal()

    def __init__(self, text, icon=None, parent=None):
        QAbstractButton.__init__(self, parent)
        self.setCheckable(True)
        self.setText(text)
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(self.fontMetrics().height(), self.fontMetrics().height()))
        self.orientation = Qt.Vertical
        self.hover = False
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.vPadding = 8
        self.hPadding = 20

    def setOrientation(self, orientation):
        if orientation == self.orientation:
            return
        self.orientation = orientation
        if self.isVisible():
            self.update()
            self.updateGeometry()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self.isChecked():
            painter.setBrush(QBrush(QColor('#BDBDBD'), Qt.SolidPattern))
            painter.drawRect(self.rect())
            painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.MiterJoin))
            painter.drawRect(1, 1, self.width()-1, self.height()-1)

        elif self.hover:
            painter.setPen(QPen(Qt.gray, 2, Qt.SolidLine, Qt.RoundCap, Qt.MiterJoin))
            painter.drawRect(self.rect())

        if self.orientation == Qt.Horizontal:
            textXOffset = 0
            if not self.icon().isNull():
                painter.drawPixmap(6, (self.height() - self.iconSize().height())/2,
                                   self.icon().pixmap(self.iconSize()))
                textXOffset += self.iconSize().width()
            painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.MiterJoin))
            painter.drawText(textXOffset, 0, self.width() - textXOffset,
                             self.height(), Qt.AlignCenter, self.text())
        else:
            transform = QTransform()
            transform.translate(0, self.height()-1)
            transform.rotate(-90.0)
            painter.setTransform(transform)
            textXOffset = 0
            if not self.icon().isNull():
                painter.drawPixmap(6, (self.width() - self.iconSize().height())/2,
                                   self.icon().pixmap(self.iconSize()))
                textXOffset += self.iconSize().width()
            painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.MiterJoin))
            painter.drawText(textXOffset, 0, self.height() - textXOffset,
                             self.width(), Qt.AlignCenter, self.text())

    def enterEvent(self, e):
        self.hover = True
        self.update()

    def leaveEvent(self, e):
        self.hover = False
        self.update()

    def mousePressEvent(self, e):
        if self.isChecked():
            if self.autoExclusive():
                self.setAutoExclusive(False)
                self.setChecked(False)
                self.setAutoExclusive(True)
            else:
                self.setChecked(False)
            self.unchecked.emit()
        else:
            self.setChecked(True)
        self.update()

    def sizeHint(self):
        if self.orientation == Qt.Horizontal:
            width = self.fontMetrics().width(self.text()) + self.hPadding
            height = self.fontMetrics().height() + self.vPadding
            if not self.icon().isNull():
                width += self.iconSize().width()
            return QSize(width, height)
        else:
            width = self.fontMetrics().height() + self.vPadding
            height = self.fontMetrics().width(self.text()) + self.hPadding
            if not self.icon().isNull():
                height += self.iconSize().width()
            return QSize(width, height)


class ToolButton(QAbstractButton):
    def __init__(self, text, icon, parent=None):
        QAbstractButton.__init__(self, parent)
        self.setText(text)
        self.setIcon(icon)
        self.setIconSize(QSize(self.fontMetrics().height(), self.fontMetrics().height()))
        self.hover = False
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

    def enterEvent(self, e):
        self.hover = True
        self.update()

    def leaveEvent(self, e):
        self.hover = False
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self.hover:
            image = self.icon().pixmap(self.iconSize()).toImage()
            painter.setCompositionMode(QPainter.CompositionMode_HardLight)
            painter.drawImage(0, (self.height() - self.iconSize().height())/2, image)
        else:
            painter.drawPixmap(0, (self.height() - self.iconSize().height())/2, self.icon().pixmap(self.iconSize()))

    def sizeHint(self):
        return QSize(self.fontMetrics().height(), self.fontMetrics().height())