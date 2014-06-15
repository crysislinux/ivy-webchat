# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class AllMachineList(QWidget):
    machineRemoved = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.list = QTableWidget()
        self.list.setColumnCount(1)
        self.list.horizontalHeader().setStretchLastSection(True)
        self.list.setHorizontalHeaderLabels(['虚拟机名称'])
        self.list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.label = QLabel(u'所有虚拟机列表')
        self.label.setAlignment(Qt.AlignCenter)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.label)
        mainLayout.addWidget(self.list)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

    @pyqtSlot(str)
    def addMachine(self, name):
        row = self.list.rowCount()
        self.list.insertRow(row)
        self.list.setItem(row, 0, QTableWidgetItem(name))

    @pyqtSlot()
    def removeCurrentMachine(self):
        row = self.list.currentRow()
        if row >= 0:
            name = self.list.item(row, 0).text()
            self.list.removeRow(row)
            self.machineRemoved.emit(name)


class UsedMachineList(QWidget):
    machineRemoved = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.list = QTableWidget()
        self.list.setColumnCount(1)
        self.list.horizontalHeader().setStretchLastSection(True)
        self.list.setHorizontalHeaderLabels(['虚拟机名称'])
        self.list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.label = QLabel(u'已使用虚拟机列表')
        self.label.setAlignment(Qt.AlignCenter)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.label)
        mainLayout.addWidget(self.list)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

    @pyqtSlot(str)
    def addMachine(self, name):
        row = self.list.rowCount()
        self.list.insertRow(row)
        self.list.setItem(row, 0, QTableWidgetItem(name))

    @pyqtSlot()
    def removeCurrentMachine(self):
        row = self.list.currentRow()
        if row >= 0:
            name = self.list.item(row, 0).text()
            self.list.removeRow(row)
            self.machineRemoved.emit(name)


class Chooser(QWidget):
    leftClicked = pyqtSignal()
    rightClicked = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.left = QPushButton('<<')
        self.right = QPushButton('>>')
        mainLayout = QVBoxLayout()
        mainLayout.addStretch()
        mainLayout.addWidget(self.right)
        mainLayout.addSpacing(20)
        mainLayout.addWidget(self.left)
        mainLayout.addStretch()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setFixedWidth(50)
        self.setLayout(mainLayout)
        self.left.clicked.connect(self.leftClicked)
        self.right.clicked.connect(self.rightClicked)


class MachineChooser(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.all = AllMachineList()
        self.used = UsedMachineList()
        self.chooser = Chooser()
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.all)
        mainLayout.addWidget(self.chooser)
        mainLayout.addWidget(self.used)
        self.setLayout(mainLayout)

        self.chooser.leftClicked.connect(self.used.removeCurrentMachine)
        self.chooser.rightClicked.connect(self.all.removeCurrentMachine)
        self.all.machineRemoved.connect(self.used.addMachine)
        self.used.machineRemoved.connect(self.all.addMachine)

    def addMachine(self, name):
        self.all.addMachine(name)

    def addUsedMachine(self, name):
        self.used.addMachine(name)


class MachineInfo(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    b = MachineChooser()
    b.show()
    b.addMachine('machine1')
    b.addMachine('machine2')
    b.addMachine('machine3')
    b.addMachine('machine4')
    #EventManager.trigger(Event('DataCenter.addLocation', '绵阳', '12.234', '122.323'))
    app.exec_()