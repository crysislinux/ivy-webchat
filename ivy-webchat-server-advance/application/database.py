# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtSql import *
from application import Log


class Database(QObject):
    TYPE_NULL = 'NULL'
    TYPE_INT = 'INTEGER'
    TYPE_REAL = 'REAL'
    TYPE_TEXT = 'TEXT'
    TYPE_BLOB = 'BLOB'
    TYPES = (TYPE_NULL, TYPE_INT, TYPE_REAL, TYPE_TEXT, TYPE_BLOB)

    def __init__(self, name, parent=None):
        QObject.__init__(self, parent)
        self.name = name

    def createConnection(self):
        self.db = QSqlDatabase('QSQLITE')
        self.db.setHostName('localhost')
        homeDir = QDir().home()
        if not homeDir.exists('.ivy-common/'):
            homeDir.mkdir('.ivy-common/')
        self.db.setDatabaseName(QDir().homePath() + '/.ivy-common/' + self.name)
        self.db.setUserName('arch')
        self.db.setPassword('arch')

        if not self.db.open():
            Log.e('数据库打开失败，请重启程序')
            return False
        return True

    def createTable(self, table, fields):
        if not hasattr(self, 'db'):
            Log.e('数据库未连接')
            return False

        if self.isTableExist(table):
            Log.w(table + ' 已存在')
            return

        query = QSqlQuery(self.db)
        sql = 'CREATE TABLE ' + table + '(id INTEGER PRIMARY KEY'
        for field in fields:
            if fields[field] not in Database.TYPES:
                raise TypeError
            else:
                sql += ', ' + field + ' ' + fields[field]
        sql += ')'
        if not query.exec_(sql):
            Log.e('数据库' + table + '创建失败')
            return False

    def isTableExist(self, name):
        query = QSqlQuery(self.db)
        query.exec_('SELECT * FROM sqlite_master WHERE name ="' + name + '" AND type="table"')
        if query.next():
            return True
        return False

    def addRecord(self, table, **kwargs):
        model = QSqlTableModel(self, self.db)
        model.setTable(table)
        record = model.record()
        for field in kwargs:
            record.setValue(field, kwargs[field])
        if not model.insertRecord(-1, record):
            Log.e('添加记录失败')
            return False
        else:
            model.submitAll()

    def delRecord(self, table, **kwargs):
        if len(kwargs) == 0:
            return
        model = QSqlTableModel(self, self.db)
        model.setTable(table)
        modelFilter = ''
        for key in kwargs:
            if len(modelFilter) != 0:
                modelFilter += 'and'
            if isinstance(kwargs[key], str) or isinstance(kwargs[key], unicode):
                newFilter = key + "={value}".format(value="'" + kwargs[key] + "'")
            else:
                newFilter = key + "={value}".format(value=kwargs[key])
            modelFilter += newFilter
        model.setFilter(modelFilter)
        model.select()
        for index in reversed(range(model.rowCount())):
            if not model.removeRow(index):
                Log.e('删除记录失败')
                return
        model.submitAll()

    def lastInsertRowId(self):
        query = QSqlQuery(self.db)
        if not query.exec_('SELECT last_insert_rowid()'):
            Log.e('获取最后插入id失败')
            return False
        if not query.next():
            Log.e('获取最后插入id失败')
            return False
        return query.value(0)

    def update(self, table, name, value, **kwargs):
        model = QSqlTableModel(self, self.db)
        model.setTable(table)
        modelFilter = ''
        for key in kwargs:
            if len(modelFilter) != 0:
                modelFilter += 'and'
            if isinstance(kwargs[key], str) or isinstance(kwargs[key], unicode):
                newFilter = key + "={value}".format(value="'" + kwargs[key] + "'")
            else:
                newFilter = key + "={value}".format(value=kwargs[key])
            modelFilter += newFilter
        model.setFilter(modelFilter)
        model.select()
        if model.rowCount() == 1:
            record = model.record(0)
            record.setValue(name, value)
            model.setRecord(0, record)
            if not model.submitAll():
                Log.e('更新记录失败')
                return False
            return True
        elif model.rowCount() == 0:
            Log.w('没找到相关记录, 添加新记录')
            self.addRecord(table, **{name: value})
        else:
            Log.e('更新失败')
            return False

    def load(self, table, **kwargs):
        model = QSqlTableModel(self, self.db)
        model.setTable(table)
        modelFilter = ''
        for key in kwargs:
            if len(modelFilter) != 0:
                modelFilter += ' and '
            if isinstance(kwargs[key], str) or isinstance(kwargs[key], unicode):
                newFilter = key + "={value}".format(value="'" + kwargs[key] + "'")
            else:
                newFilter = key + "={value}".format(value=kwargs[key])
            modelFilter += newFilter
        model.setFilter(modelFilter)
        model.select()
        columnCount = model.columnCount()
        items = []
        for index in range(model.rowCount()):
            record = model.record(index)
            items.append([record.value(pos) for pos in range(columnCount)])
        return items


if __name__ == '__main__':
    db = Database('chat.db')
    db.createConnection()
    #db.createConnection()
    #db.createTable('test', filed2='REAL')
    #db.addRecord('test', filed2=1.3234)
    #db.delRecord('test', filed2=1.3234)
    print db.load('settings', value='我们', name='geo')