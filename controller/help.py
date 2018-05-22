# -*- coding: UTF-8 -*-

import sys
from base import BaseHandler
from utils.file_helper import lock_site_notify
from settings import siteinfo
from settings import wechatapi
from urllib import parse
sys.path.append('..')

class HelpHandler(BaseHandler):

    def get(self,content):
        islock, site_notify = lock_site_notify()
        user = self.get_current_user()
        data = wechatapi
        if user:
            self.render(content, data=data, returnurl = parse.quote(wechatapi['redirect_uri']), username=user.nickname, site_notify=site_notify, siteinfo=siteinfo)
        else:
            self.render(content, data=data, returnurl = parse.quote(wechatapi['redirect_uri']), username=None, site_notify=site_notify, siteinfo=siteinfo)

