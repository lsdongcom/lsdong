# -*- coding: UTF-8 -*-

import os
import tornado
import time
import settings
import json
import copy
from tornado import escape
from settings import encryptkey
from safeutils import crypto_helper
from model.userinfo import userinfo
from datetime import datetime,timedelta



class BaseHandler(tornado.web.RequestHandler):
    # def __init__(self, *argc, **argkw):
    #     self.xsrf_token

    def set_default_headers(self):
        self.set_header('x-frame-options', 'SAMEORIGIN')  # 防止网页被Frame
        self.set_header('X-XSS-Protection', '1;mode=block')  # 当检测到跨站脚本攻击 (XSS)时，浏览器将停止加载页面
        self.set_header('cache-control', 'max-age=5')  # 浏览器缓存设置 http://www.cnblogs.com/micro-chen/p/6547049.html
        self.set_header('server', settings.setting['servers'])

    def input(self, *args, **kwargs):
        """客户端参数获取"""
        return self.get_argument(*args, **kwargs)

    def input_default(self, name, default=None, strip=True):
        """客户端参数获取"""
        return self.get_argument(name, default=default, strip=strip)

    def get_session(self, name):
        session = self.get_secure_cookie(name)
        if (session):
            session = crypto_helper.aes_decrypt(str(session, encoding='utf-8'), encryptkey)
            return session
        else:
            return None

    def set_session(self, name,value, expires=time.time() + 10 * 60):
        self.set_secure_cookie(name, crypto_helper.aes_encrypt(value, encryptkey),expires=expires)

    def get_current_user(self):
        sessionuser = self.get_session('session_id')
        if (sessionuser):
            sessionuser = tornado.escape.json_decode(sessionuser)
            user = userinfo()
            user.get_userinfo_from_session(sessionuser)
            return user
        else:
            return None

    def set_current_user(self, user):
        if user:
            self.set_session('session_id', escape.json_encode(user), expires=time.time() + 60 * 60 * 2)
        else:
            self.clear_cookie('session_id')

    def get_filepath(self, user,filename,filehash):
        nowdir = datetime.now().strftime('%Y%m%d')
        hashkey = crypto_helper.get_key(filehash, filename, user.id, nowdir)
        sessionfile = self.get_session(hashkey)
        if (sessionfile):
            return sessionfile
        else:
            return None

    def set_filepath(self, user,filename,filehash,filepath):
        nowdir = datetime.now().strftime('%Y%m%d')
        hashkey = crypto_helper.get_key(filehash, filename, user.id, nowdir)
        self.set_session(hashkey, filepath, expires=time.time() + 60 * 60 * 24)

    def get_deep_dict(self, user, deepnumber):
        deepnumber = deepnumber - 1
        deepstep = int((deepnumber - deepnumber % 5) / 5 + 2)
        session_name = '%s_%s_%s' % (user.id, 'session_deep', deepstep)
        deepdict = self.get_session(session_name)
        if (deepdict):
            deepdict = escape.json_decode(deepdict)
            deeplist = deepdict[str(deepnumber)].split('/t')
            return deeplist[0], deeplist[1]
        else:
            return None, None

    def set_deep_dict(self, user, deepnumber, deeppath, deephash):
        deepnumber = deepnumber -1
        deepstep = int((deepnumber - deepnumber % 5) / 5 + 2)
        deepdict = {}
        session_name = '%s_%s_%s' % (user.id, 'session_deep', deepstep)
        sessiondeepdict = self.get_session(session_name)
        if (sessiondeepdict):
            sessiondeepdict = escape.json_decode(sessiondeepdict)
            deepdict = copy.deepcopy(sessiondeepdict)
        deepdict[deepnumber] = '%s/t%s' % (deeppath, deephash)
        self.set_session(session_name, escape.json_encode(deepdict), expires=time.time() + 60 * 60 * 24)

    def get_deep_number(self, user):
        session_name = '%s%s' % (user.id, 'session_deep_number')
        deep_number = self.get_session(session_name)
        if (deep_number):
            return int(deep_number)
        else:
            self.set_deep_number(user, '1')
            return 1

    def set_deep_number(self, user, number):
        deepnumber = int(number)
        if (deepnumber < 1): deepnumber = 1
        session_name = '%s%s' % (user.id, 'session_deep_number')
        deep_number = self.set_session(session_name, str(deepnumber), expires=time.time() + 60 * 60 * 2)