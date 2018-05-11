# -*- coding: UTF-8 -*-

import sys
import tornado
from base import BaseHandler
from utils.file_helper import lock_site_notify
from settings import siteinfo
sys.path.append('..')

class IndexHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        islock, site_notify = lock_site_notify()
        user = self.get_current_user()
        self.render('index.html', username=user.nickname,site_notify = site_notify,siteinfo=siteinfo)

