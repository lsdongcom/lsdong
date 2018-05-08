# -*- coding: UTF-8 -*-


import os,os.path,sys
import json
import tornado
from base import BaseHandler
from utils.file_helper import getfiletypename,lock_site_notify
sys.path.append('..')

class LogoutHandler(BaseHandler):
    def get(self):
        if(self.input_default('c')):
            self.clear_all_cookies()
        else:
            self.clear_cookie('session_id')
        self.redirect('/login')