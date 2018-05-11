# -*- coding: UTF-8 -*-

import os.path
import re
from datetime import datetime,timedelta
from settings import siteinfo,lockfile,usertemppath,isuploadfileoss

def getfiletypename(filetype):
    if (filetype is 1): return '邮箱校验'
    if (filetype is 2): return '短信校验'
    if (filetype is 3): return '密码加密'
    if (filetype is 4): return '金融支付校验'
    if (filetype is 5): return '金融支付强校验'

def file_name(path):
    return os.path.split(path)[1]

def file_extension(filename):
    finfo = os.path.splitext(filename)
    if (len(finfo) < 2):
        return ''
    else:
        return finfo[1]

def lock_site_notify():
    if (os.path.exists(lockfile) is True):
        return True,siteinfo['locknotify']
    return False,siteinfo['sitenotify']

def deep_auth_create(userid, code):
    filename = '%s_%s' % (userid, code)
    nowdir = datetime.now().strftime('%Y%m%d')
    nowpath = os.path.join(usertemppath, nowdir, filename)
    if (os.path.exists(nowpath) is False):
        if (os.path.exists(os.path.join(usertemppath, nowdir)) is False):
            os.makedirs(os.path.join(usertemppath, nowdir))
        with open(nowpath, 'w+') as up:
            up.write(filename)

def deep_auth_check(userid, code):
    filename = '%s_%s' % (userid, code)
    now = datetime.now()
    nowdir = now.strftime('%Y%m%d')
    if (os.path.exists(os.path.join(usertemppath, nowdir, filename)) is True):
        return True
    beforetime = now - timedelta(days=1)
    beforetimedir = beforetime.strftime('%Y%m%d')
    if (os.path.exists(os.path.join(usertemppath, beforetimedir, filename)) is True):
        return True
    return False

def checkfilename(filename):
    filter_rule = '[^\u2E80-\u9FFFa-zA-Z0-9_.]+'
    if (re.search(filter_rule, filename)):
        return False
    else:
        return True

def file_exists(filepath,oss=None):
    if isuploadfileoss is True:
        return oss.exists(filepath)
    else:
        return os.path.exists(filepath)

def file_read(filepath,oss=None):
    if isuploadfileoss is True:
        filedata = oss.Bucket.get_object(filepath).read()
    else:
        with open(filepath, 'r') as f:
            filedata = f.readlines()
    return filedata

def file_write(filepath,filedata,oss=None):
    if isuploadfileoss is True:
        oss.Bucket.put_object(filepath, filedata)
    else:
        with  open(filepath, 'w', encoding='utf-8') as f:
            f.write(filedata)


