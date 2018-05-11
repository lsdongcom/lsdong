# -*- coding: UTF-8 -*-

import os,os.path,sys
from base import BaseHandler
from settings import usertemppath,downloadpath
import shutil
from datetime import datetime,timedelta
from settings import isuploadfileoss,alioss,systaskpwd
from utils.oss_helper import Alioss
sys.path.append('..')

class SysTaskHandler(BaseHandler):

    def get(self):
        filecleartask = self.input_default('t')
        if filecleartask != systaskpwd:
            self.write('ok')
            return

        now = datetime.now()
        nowdir = now.strftime('%Y%m%d')
        beforetime = now - timedelta(days=1)
        beforetimedir = beforetime.strftime('%Y%m%d')
        files = os.listdir(usertemppath)
        for file in files:
            if file != nowdir and file != beforetimedir:
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


