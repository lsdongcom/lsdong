# -*- coding: UTF-8 -*-

import sys
from base import BaseHandler
from settings import wechatapi
sys.path.append('..')

class LoginHandler(BaseHandler):

    def get(self):
        data = wechatapi
        self.render('login.html', data=data, tips='', error='',site_notify = '')

