# -*- coding: UTF-8 -*-

import os.path
import re
from datetime import datetime,timedelta
from settings import sitenotify,lockfile,usertemppath

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
    if (os.path.exists(lockfile)):
        return True,'站点即将在1小时后更新,为防止数据丢失及支付异常,系统将关闭文件上传和支付功能,敬请谅解'
    return False,sitenotify

def deep_auth_create(userid, code):
    filename = '%s_%s' % (userid, code)
    nowdir = datetime.now().strftime('%Y%m%d')
    nowpath = os.path.join(usertemppath, nowdir, filename)
    if (not os.path.exists(nowpath)):
        if (not os.path.exists(os.path.join(usertemppath, nowdir))):
            os.makedirs(os.path.join(usertemppath, nowdir))
        with open(nowpath, 'w+') as up:
            up.write(filename)

def deep_auth_check(userid, code):
    filename = '%s_%s' % (userid, code)
    now = datetime.now()
    nowdir = now.strftime('%Y%m%d')
    if (os.path.exists(os.path.join(usertemppath, nowdir, filename))):
        return True
    beforetime = now - timedelta(days=1)
    beforetimedir = beforetime.strftime('%Y%m%d')
    if (os.path.exists(os.path.join(usertemppath, beforetimedir, filename))):
        return True
    return False

def checkfilename(filename):
    filter_rule = '[^\u2E80-\u9FFFa-zA-Z0-9_.]+'
    if (re.search(filter_rule, filename)):
        return False
    else:
        return True
