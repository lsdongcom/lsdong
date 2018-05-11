# -*- coding: UTF-8 -*-


import sys
from base import BaseHandler
sys.path.append('..')

class LogoutHandler(BaseHandler):
    def get(self):
        if(self.input_default('c')):
            self.clear_all_cookies()
        else:
            self.clear_cookie('session_id')
        self.redirect('/login')