# -*- coding: UTF-8 -*-

import sys
import tornado
from base import BaseHandler
from utils.file_helper import lock_site_notify
from settings import siteinfo
from settings import wechatapi
sys.path.append('..')

class IndexHandler(BaseHandler):

    def get(self):
        islock, site_notify = lock_site_notify()
        user = self.get_current_user()
        if user:
            self.render('index.html', username=user.nickname,site_notify = site_notify,siteinfo=siteinfo)
        else:
            data = wechatapi
            self.render('login.html', data=data, site_notify=site_notify, siteinfo=siteinfo)

