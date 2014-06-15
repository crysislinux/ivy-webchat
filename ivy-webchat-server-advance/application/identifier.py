# -*- coding: utf-8 -*-
from globals import Globals
from log import Log


Globals.setAttr('identifiers', {-1: []})


def addResource(resourceId, clientId):
    if clientId == -1:
        Log.w(u'clientId为-1,忽略')
        return
    identifiers = Globals.getAttr('identifiers')
    if clientId in identifiers:
        identifiers[clientId].append(resourceId)
    else:
        identifiers[clientId] = resourceId
    print identifiers


def removeResource(resourceId, clientId=None):
    if clientId == -1:
        Log.w(u'clientId为-1,忽略')
        return
    identifiers = Globals.getAttr('identifiers')
    if clientId:
        if clientId in identifiers:
            if resourceId in identifiers[clientId]:
                identifiers[clientId].remove(resourceId)
                return True
    else:
        for clientId in identifiers:
            if resourceId in identifiers[clientId]:
                identifiers[clientId].remove(resourceId)
                return True
    Log.w(u'未找到对应的资源，删除失败')


def lookUpClientIdByResourceId(resourceId):
    identifiers = Globals.getAttr('identifiers')
    for clientId in identifiers:
        if resourceId in identifiers[clientId]:
            return clientId


def getRandomClientId():
    identifiers = Globals.getAttr('identifiers')
    for clientId in identifiers:
        if clientId != -1:
            return clientId


def addToolBar(toolBarId, position, index):
    toolBars = Globals.getAttr('toolBars')
    if not toolBars:
        Globals.setAttr('toolBars', {position: [{'toolBarId': toolBarId, 'items': []}]})
    else:
        if position in toolBars:
            if len(toolBars[position]) > index:
                toolBars[position][index]['toolBarId'] = toolBarId
            else:
                toolBars[position].append({'toolBarId': toolBarId, 'items': []})
        else:
            toolBars[position] = [{'toolBarId': toolBarId, 'items': []}]
            return


def addItemToToolBar(resourceId, position, index):
    print index
    toolBars = Globals.getAttr('toolBars')
    if not toolBars:
        return
    if position in toolBars:
        toolBars[position][index]['items'].append(resourceId)
    print toolBars


def lookUpToolBarIdByResourceId(resourceId):
    toolBars = Globals.getAttr('toolBars')
    if not toolBars:
        return
    for position in toolBars:
        for index, tmp in enumerate(toolBars[position]):
            items = tmp['items']
            for resourceId_ in items:
                if resourceId_ == resourceId:
                    return toolBars[position][index]['toolBarId']