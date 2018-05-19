# -*- coding: UTF-8 -*-

import re
import json
from safeutils import crypto_helper
import time
from sdk.alipay_pay import Alipay

def getSessionKey(userid,fileindex,filetype,filename):
    return crypto_helper.get_key(str(fileindex), str(filetype), str(filename), str(userid))

def setPaySession(web_handler, sessionkey,payno, userid,fileindex,filetype,actiontype,filename,deep_number,password):
    fileinfo = {}
    fileinfo['payno'] = payno
    fileinfo['userid'] = userid
    fileinfo['i'] = fileindex
    fileinfo['t'] = filetype
    fileinfo['a'] = actiontype
    fileinfo['name'] = filename
    fileinfo['deep_number'] = deep_number
    fileinfo['password'] = password
    fileinfo['status'] = '0'
    web_handler.set_session(sessionkey, json.dumps(fileinfo), expires=time.time() + 60 * 60 * 2)

def getPaySession(web_handler, sessionkey):
    sessioncontent = web_handler.get_session(sessionkey)
    if (sessioncontent):
        fileinfo = json.loads(sessioncontent)
        return fileinfo
    return None

def updatePaySession(web_handler, sessionkey):
    sessioncontent = web_handler.get_session(sessionkey)
    if (sessioncontent):
        fileinfo = json.loads(sessioncontent)
        fileinfo['status'] = '1'
        web_handler.set_session(sessionkey, json.dumps(fileinfo), expires=time.time() + 60 * 60 * 24)

def checkPaySession(web_handler, sessionkey, password=None):
    sessioncontent = web_handler.get_session(sessionkey)
    if (sessioncontent):
        fileinfo = json.loads(sessioncontent)
        alipay = Alipay()
        payno = fileinfo['payno']
        if password is None:
            if (fileinfo['status'] == '1'):
                return True
            if alipay.query(payno) is True or alipay.refundallquery(payno) is True:
                fileinfo['status'] = '1'
                web_handler.set_session(sessionkey, json.dumps(fileinfo), expires=time.time() + 60 * 60 * 24)
                return True
        else:
            ppwd = fileinfo['password']
            if(ppwd != password):
                return False
            if fileinfo['status'] == '1':
                return True
            if alipay.query(payno) is True or alipay.refundallquery(payno) is True:
                fileinfo['status'] = '1'
                web_handler.set_session(sessionkey, json.dumps(fileinfo), expires=time.time() + 60 * 60 * 24)
                return True
    return False

def getPayAmount(filetype,password):
    password = re.sub('[^0-9]+', '', password)
    password = list(password.strip('0'))
    l = len(password)
    if (int(filetype) == 4):
        p = ['0'] * 3
        if(l>3):
            password = password[0:3]
            password = list(''.join(password).strip('0'))
    else:
        p = ['0'] * 5
        if (l > 5):
            password = password[0:5]
            password = list(''.join(password).strip('0'))
    l = len(password)
    d = len(p) - l
    for i in range(l):
        p[i + d] = password[i]
    p.insert(-2,'.')
    amount = float(''.join(p))
    return amount





