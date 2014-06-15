# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from singleton import VMItem
import singleton
from application import EventManager, Event
import application
from message import Message


class VMProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)


class RichTextDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.label = QLabel()
        self.label.setStyleSheet(
            'background: white'
        )

    @staticmethod
    def html(text, state):
        if state == VMItem.Status_Invalid:
            return '<s><font color="#F00" >' + text + '</font></s>'
        elif state == VMItem.Status_Idle:
            return '<font color="#1D953F">' + text + '</font>'
        elif state == VMItem.Status_Running:
            return '<font color="#B4533C">' + text + '</font>'
        return text

    def paint(self, painter, option, index):
        selected = option.state & QStyle.State_Selected
        palette_ = QPalette(option.palette)
        palette_.setColor(QPalette.Active, QPalette.Window,
                          option.palette.highlight().color() if selected else option.palette.base().color())
        palette_.setColor(QPalette.Active, QPalette.WindowText,
                          option.palette.highlightedText().color() if selected else option.palette.text().color())
        text = index.model().data(index, Qt.DisplayRole)
        status = index.model().itemForIndex(index).status()
        self.label.setPalette(palette_)
        self.label.setText(self.html(text, status))
        self.label.setFixedSize(QSize(max(0, option.rect.width() - option.fontMetrics.height() - 4),
                                      option.fontMetrics.height()))
        labelRect = QRect(option.rect.x() + option.fontMetrics.height() + 4,
                          option.rect.y() + (option.rect.height() - option.fontMetrics.height())/2,
                          self.label.width(), self.label.height())
        iconRect = QRect(option.rect.x(), option.rect.y() + (option.rect.height() - self.label.height())/2,
                         min(max(0, option.rect.width()), option.fontMetrics.height()), option.fontMetrics.height())
        item = index.model().itemForIndex(index)
        if not item.parent().parent():
            painter.drawPixmap(iconRect, QPixmap('images/virtualbox.png'))
        else:
            painter.drawPixmap(iconRect, QPixmap('images/android.png'))
        pixmap_ = QPixmap(self.label.size())
        self.label.render(pixmap_)
        painter.drawPixmap(labelRect, pixmap_)

    def sizeHint(self, option, index):
        text = index.model().data(index, Qt.DisplayRole)
        return QSize(option.fontMetrics.width(text) + option.fontMetrics.height() + 4, option.fontMetrics.height() + 16)


class VMList(QWidget):
    startOrGotoVm = pyqtSignal(dict)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.createModelAndView()
        #self.createOp()
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(self.treeView)
        self.setLayout(mainLayout)
        self.setStyleSheet(
            'QLineEdit{padding: 0;}'
        )
        EventManager.bind('Message.addVms', self.addVms)
        EventManager.bind('Message.updateVm', self.resetVm)

    def createModelAndView(self):
        self.model = singleton.getVmModel()
        self.proxyModel = VMProxyModel(self)
        self.proxyModel.setSourceModel(self.model)
        self.treeView = QTreeView()
        self.treeView.setAllColumnsShowFocus(True)
        self.treeView.setItemDelegateForColumn(0, RichTextDelegate())
        #self.treeView.setItemDelegateForColumn(1, RichTextDelegate())
        self.treeView.setModel(self.model)
        self.model.rowsInserted.connect(self.expand)
        self.treeView.doubleClicked.connect(self.handleDoubleClickOnItem)
        self.model.dataChanged.connect(self.editVm)

    def editVm(self, index, unused, roles):
        """同步修改到服务器，只能修改虚拟机备注"""
        if Qt.EditRole not in roles:
            self.treeView.update()
            return
        item = self.model.itemForIndex(index)
        resourceId = item.id()
        clientId = application.lookUpClientIdByResourceId(resourceId)
        if clientId:
            message = Message(cmd=Message.CMD_UPDATE_VM)
            message['vmId'] = resourceId
            message['desc'] = item.description()
            EventManager.trigger(Event('Client.replyReady.' + clientId, message))
            toolBarId = application.lookUpToolBarIdByResourceId(resourceId)
            if toolBarId:
                print 'ToolBar.changeState.' + toolBarId
                EventManager.trigger(Event('ToolBar.changeState.' + toolBarId, True))

    def handleDoubleClickOnItem(self, index):
        if index.column() == singleton.VMModel.Description:
            return
        item = self.model.itemForIndex(index)
        if not item.parent().parent():
            return
        info = {'serverId': item.parent().id(), "name": item.name(), "desc": item.description(),
                "vmId": item.id(), 'vmType': item.type(),  "status": item.status()}
        print info
        self.startOrGotoVm.emit(info)

    def resetVm(self, info):
        self.model.resetVm(info)

    def addVms(self, info):
        self.model.addVms(info)

    def expand(self, parent, start_, end):
        for i in range(end-start_+1):
            index = self.model.createIndex(start_, 0, self.model.itemForIndex(parent).childAt(start_+i))
            self.treeView.setExpanded(index, True)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet(
        'QWidget{background-color: #D6D6D6;color: #000;font-size: 13px;}'

        'QScrollBar:horizontal {border-top: 1px solid grey;height: 15px;border-bottom: none;padding: 1px 0;}'

        'QScrollBar:vertical {border-left: 1px solid grey;width: 15px;padding: 0 1px; border-right:none}'

        'QScrollBar::add-line,  QScrollBar::sub-line {width:0;}'

        'QScrollBar::handle:horizontal {border: 1px solid #818A9A; border-radius: 4px;'
        'background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,'
        'stop: 0 #ECECEC, stop: 0.4 #E4E4E4,stop: 0.5 #E0E0E0, stop: 1.0 #D6D6D6);}'

        'QScrollBar::handle:horizontal:hover{background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,'
        'stop: 0 #D6D6D6, stop: 0.5 #A7A7A7, stop: 1.0 #9B9B9B);}'

        'QScrollBar::handle:vertical {border: 1px solid #818A9A; border-radius: 4px;'
        'background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,'
        'stop: 0 #ECECEC, stop: 0.4 #E4E4E4,stop: 0.5 #E0E0E0, stop: 1.0 #D6D6D6);}'

        'QScrollBar::handle:vertical:hover{background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,'
        'stop: 0 #D6D6D6, stop: 0.5 #A7A7A7, stop: 1.0 #9B9B9B);}'

        'QTreeView::item {padding: 20px 0; background:  #F00;}'

        'QTreeView::item:selected {background:  transparent; color: black}'

        'QTabWidget::tab-bar {border-left: 1px solid #818A9A; background-color: #FFF;}'

        'QTabBar::tab {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,'
        'stop: 0 #DEDEDE, stop: 0.4 #D8D8D8,stop: 0.5 #D8D8D8, stop: 1.0 #DEDEDE);'
        'color: #000;border: 1px solid #818A9A;padding: 3px;margin: -1px 0 0 -1px;}'

        'QTabBar::tab:selected {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,'
        'stop: 0 #FFFFFF, stop: 0.4 #F4F4F4,''stop: 0.5 #F4F4F4, stop: 1.0 #D6D6D6);'
        'border-bottom: 1px solid #D6D6D6}'

    )
    b = VMList()
    b.show()
    app.exec_()