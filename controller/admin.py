# -*- coding: UTF-8 -*-

# -*- coding: UTF-8 -*-

import os,os.path,sys
import json
import tornado
from base import BaseHandler
from settings import usertemppath,downloadpath
import uuid
import shutil
from datetime import datetime,timedelta
from safeutils import crypto_helper
from model.userinfo import userinfo
from model.userfile import userfile
from settings import adminids,lockfile
sys.path.append('..')

class AdminHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        if(user.id not in adminids):
            self.redirect('/')
            return

        lock = self.input_default('l')
        unlock = self.input_default('u')
        fileclear = self.input_default('c')
        if(lock):
            if (not os.path.exists(lockfile)):
                with open(lockfile, 'w+') as up:
                    up.write(user.nickname)
        if(unlock):
            if (os.path.exists(lockfile)):
                os.unlink(lockfile)
        if(fileclear):
            now = datetime.now()
            nowdir = now.strftime('%Y%m%d')
            beforetime = now - timedelta(days=1)
            beforetimedir = beforetime.strftime('%Y%m%d')
            files = os.listdir(usertemppath)
            for file in files:
                if file!=nowdir and file!=beforetimedir:
                    fullpath = os.path.join(usertemppath, file)
                    if (os.path.isdir(fullpath)):
                        shutil.rmtree(fullpath)

            files = os.listdir(downloadpath)
            for file in files:
                if file != nowdir and file != beforetimedir:
                    fullpath = os.path.join(downloadpath, file)
                    if (os.path.isdir(fullpath)):
                        shutil.rmtree(fullpath)

        self.write('success')


