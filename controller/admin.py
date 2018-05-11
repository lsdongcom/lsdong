# -*- coding: UTF-8 -*-

import os,os.path,sys
import tornado
from base import BaseHandler
from settings import usertemppath,downloadpath
import shutil
from datetime import datetime,timedelta
from settings import adminids,lockfile,isuploadfileoss,alioss
from utils.oss_helper import Alioss
sys.path.append('..')

class AdminHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        if(user.id not in adminids):
            self.write('ok')
            return

        lock = self.input_default('l')
        unlock = self.input_default('u')
        fileclear = self.input_default('c')
        if(lock):
            if (os.path.exists(lockfile) is False):
                with open(lockfile, 'w+') as up:
                    up.write(user.nickname)
        if(unlock):
            if (os.path.exists(lockfile) is True):
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

            if isuploadfileoss is True:
                oss = Alioss()
                deltemppath = '%s/%s' % (alioss['usertemppath'], '20')
                temppath = '%s/%s' % (alioss['usertemppath'], nowdir)
                beforetimetemppath = '%s/%s' % (alioss['usertemppath'], beforetimedir)
                deldownpath = '%s/%s' % (alioss['downloadpath'], '20')
                downpath = '%s/%s' % (alioss['downloadpath'], nowdir)
                beforetimedownpath = '%s/%s' % (alioss['downloadpath'], beforetimedir)
                oss.del_dir(deltemppath, temppath, beforetimetemppath)
                oss.del_dir(deldownpath, downpath, beforetimedownpath)

        self.write('success')


