# -*- coding: UTF-8 -*-

import os,os.path,sys
import json
import tornado
from base import BaseHandler
from model.userinfo import userinfo
from utils.file_helper import getfiletypename,lock_site_notify
sys.path.append('..')

class IndexHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        islock, site_notify = lock_site_notify()
        user = self.get_current_user()
        self.render('index.html', username=user.nickname,site_notify = site_notify)

