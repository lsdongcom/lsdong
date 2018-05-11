# -*- coding: UTF-8 -*-

import sys
from base import BaseHandler
from settings import siteinfo
from utils.file_helper import lock_site_notify
sys.path.append('..')

class HelpHandler(BaseHandler):

    def get(self,content):
        islock, site_notify = lock_site_notify()
        self.render(content, site_notify=site_notify, siteinfo=siteinfo)

