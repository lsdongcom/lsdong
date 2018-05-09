# -*- coding: UTF-8 -*-

import os,os.path,sys
import json
import tornado
from base import BaseHandler
from settings import usertemppath,userdatapath,downloadpath
import uuid
import shutil
from datetime import datetime,timedelta
from safeutils import crypto_helper
from model.userinfo import userinfo
from model.userfile import userfile
from utils.file_helper import getfiletypename,lock_site_notify
from settings import oss,filetypelimit,filesizelimit,isuploadfileoss,userdatapath, downloadpath, downloadurl
from utils.oss_helper import alioss

sys.path.append('..')

class Upload_OSS_Handler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        islock, notify = lock_site_notify()
        if (islock is True):
            ret = {'result': 'error'}
            ret['info'] = notify;
            self.write(ret)
            return

        filename = self.input_default('filename', None)
        filehash = self.input_default('filehash', None)
        filetype = self.input_default('t', None)
        filesize = int(self.input_default('s', '0'))
        password = self.input_default('p', None)

        if (filename == None or filehash == None or filetype == None or password == None):
            ret = {'result': 'error'}
            ret['info'] = '参数异常或缺失';
            self.write(json.dumps(ret))
            return
        if (filesize == 0):
            ret = {'result': 'error'}
            ret['info'] = '参数异常或上传的文件为空文件';
            self.write(json.dumps(ret))
            return

        password = str(password).strip()
        user = self.get_current_user()
        deep_number = self.get_deep_number(user)
        if (deep_number == 1):
            filedata = userfile(user, None, None)
        else:
            filepath, filehash = self.get_deep_dict(user, deep_number - 1)
            filedata = userfile(user, filepath, filehash)
        filelist = filedata.filelist
        for item in filelist:
            if (item[0] == filename and item[1] == filetype and item[3] == filesize):
                ret = {'result': 'error'}
                ret['info'] = '同目录下已存在相同文件';
                self.write(json.dumps(ret))
                return

        passhash = crypto_helper.get_key(password, user.id, filehash, None, False)
        finalname = filedata.add_file(filename, filetype, filesize, filehash, passhash)
        password = crypto_helper.get_key(password, user.id)
        encrpath = os.path.join(userdatapath, finalname)

        if (isuploadfileoss):
            ret = {'result': 'ok'}
            self.write(json.dumps(ret))
        else:
            now = datetime.now()
            nowdir = now.strftime('%Y%m%d')
            downpath = os.path.join(downloadpath, nowdir, filehash, filename)
            if (not os.path.exists(os.path.join(downloadpath, nowdir, filehash))):
                os.makedirs(os.path.join(downloadpath, nowdir, filehash))
            file_metas = self.request.files.get('file', None)  # 提取表单中‘name’为‘file’的文件元数据
            if file_metas:
                temp_file = os.path.join(usertemppath, finalname)
                with open(temp_file, 'wb') as up:
                    up.write(file_metas[0]['body'])

                temp_file = os.path.join(usertemppath, finalname)
                if (not os.path.exists(downpath)):
                    shutil.move(temp_file, downpath)
                else:
                    os.unlink(temp_file)

            if (os.path.exists(encrpath)):
                os.unlink(encrpath)

            crypto_helper.encrypt_file(bytes.fromhex(password), downpath, encrpath)

            if (not user.isexist):
                user.set_isexist(True)
                self.set_current_user(user.get_session())

            ret = {'result': 'ok'}
            self.write(json.dumps(ret))