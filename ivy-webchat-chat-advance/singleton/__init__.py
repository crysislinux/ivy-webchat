# -*- coding: utf-8 -*-

from gps_model import GpsModel, GpsItem
from vm_model import VMModel, VMItem
from account_model import AccountItem, AccountModel
from PyQt5.QtWidgets import QApplication
import sys

_app = QApplication(sys.argv)
_gpsModel = GpsModel()
_vmModel = VMModel()
_accountModel = AccountModel()


def getGpsModel():
    return _gpsModel


def getVmModel():
    return _vmModel


def getAccountModel():
    return _accountModel


def getApplication():
    return _app