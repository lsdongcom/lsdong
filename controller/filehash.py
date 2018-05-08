# -*- coding: UTF-8 -*-

import os, os.path, sys
import json
import tornado
from base import BaseHandler
import shutil
import uuid
from datetime import datetime, timedelta
from safeutils import crypto_helper
from model.userinfo import userinfo
from model.userfile import userfile
from utils.file_helper import getfiletypename
from settings import userdatapath, downloadpath, downloadurl
from urllib.parse import urljoin

sys.path.append('..')


class FileHashHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        filename = self.input_default('filename', None)
        filehash = self.input_default('filehash', None)
        filetype = self.input_default('t', None)
        deep_number = self.get_deep_number(user)
        if (deep_number == 1):
            filedata = userfile(user, None, None)
        else:
            filepath, filehash = self.get_deep_dict(user, deep_number - 1)
            filedata = userfile(user, filepath, filehash)
        filelist = filedata.filelist
        for item in filelist:
            if (item[0] == filename and item[1] == filetype and item[3] == filehash):
                ret = {'result': 'error'}
                ret['info'] = '同目录下已存在相同文件';
                self.write(json.dumps(ret))
                return

        now = datetime.now()
        nowdir = now.strftime('%Y%m%d')
        downpath = os.path.join(downloadpath, nowdir, filehash, filename)
        if (os.path.exists(downpath)):
            ret = {'result': '0'}
            self.write(json.dumps(ret))
            return
        else:
            beforetime = now - timedelta(days=1)
            beforetimedir = beforetime.strftime('%Y%m%d')
            beforetimedownpath = os.path.join(downloadpath, beforetimedir, filehash, filename)
            if(os.path.exists(beforetimedownpath)):
                if (not os.path.exists(os.path.join(downloadpath, nowdir, filehash))):
                    os.makedirs(os.path.join(downloadpath, nowdir, filehash))
                shutil.move(beforetimedownpath, downpath)
                ret = {'result': '0'}
                self.write(json.dumps(ret))
                return
            else:
                ret = {'result': '1'}
                self.write(json.dumps(ret))
                return


