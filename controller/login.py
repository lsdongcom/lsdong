# -*- coding: UTF-8 -*-

import sys
from base import BaseHandler
from settings import wechatapi
from utils.file_helper import lock_site_notify
from settings import siteinfo
sys.path.append('..')

class LoginHandler(BaseHandler):

    def get(self):
        islock, site_notify = lock_site_notify()
        data = wechatapi
        self.render('login.html', data=data, site_notify = site_notify,siteinfo=siteinfo)

