# -*- coding: UTF-8 -*-

import sys
import tornado
from base import BaseHandler
from  model import userpay
from utils.file_helper import getfiletypename,lock_site_notify
from settings import siteinfo
sys.path.append('..')

class FileViewHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        islock, site_notify = lock_site_notify()
        sessionkey = self.input_default('k')
        if (sessionkey):
            fileinfo = userpay.getPaySession(self, sessionkey)
            if not fileinfo:
                fileindex = '999999'
                filetype = '4'
                actiontype = '0'
                filename = '未知文件'
            else:
                fileindex = int(fileinfo['i'])
                filetype = fileinfo['t']
                actiontype = fileinfo['a']
                filename = fileinfo['name']
        else:
            fileindex = self.input_default('i')
            filetype = self.input_default('t')
            actiontype = self.input_default('a')
            filename = self.input_default('name')

        user = self.get_current_user()
        message = self.input_default('m',None)
        if filetype:
            filetypename = getfiletypename(int(filetype))
            self.render('fileview_' + filetype + '.html', username=user.nickname, filetype=filetype, filetypename=filetypename,
                        fileindex=fileindex, actiontype=actiontype, filename=filename, message=message,site_notify=site_notify, siteinfo=siteinfo)

















