# -*- coding: UTF-8 -*-

import os,os.path,sys
import json
import tornado
from base import BaseHandler
import shutil
import uuid
from datetime import datetime,timedelta
from safeutils import crypto_helper
import time
from  model import userpay
from model.userinfo import userinfo
from model.userfile import userfile
from utils.file_helper import getfiletypename,lock_site_notify
from settings import userdatapath,downloadpath,downloadurl
from urllib.parse import urljoin

sys.path.append('..')

class FileViewHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        islock, site_notify = lock_site_notify()
        sessionkey = self.input_default('k')
        if (sessionkey):
            fileinfo = userpay.getPaySession(self, sessionkey)
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
                        fileindex=fileindex, actiontype=actiontype, filename=filename, message=message,site_notify = site_notify)

















