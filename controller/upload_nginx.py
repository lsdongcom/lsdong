# -*- coding: UTF-8 -*-

import os,os.path,sys
import json
import tornado
from base import BaseHandler
from settings import userdatapath,downloadpath
import shutil
from datetime import datetime
from safeutils import crypto_helper
from model.userfile import userfile
from utils.file_helper import lock_site_notify
sys.path.append('..')

class Upload_Nginx_Handler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        islock, notify = lock_site_notify()
        if (islock is True):
            ret = {'result': 'error'}
            ret['info'] = notify;
            self.write(ret)
            return

        keys = self.request.arguments.keys()
        if "file.path" not in keys and "userfile.path" not in keys:
            self.set_status(status_code=400, reason="file field not exist.")
            self.write("400")
            return
        files = list()
        if "file.path" in keys:
            file_path = self.request.arguments['file.path']
            for index in range(len(file_path)):
                file = {}
                file['name'] = str(self.request.arguments['file.name'][index], encoding='utf-8')
                file['content_type'] = str(self.request.arguments['file.content_type'][index], encoding='utf-8')
                file['path'] = str(self.request.arguments['file.path'][index], encoding='utf-8')
                file['md5'] = str(self.request.arguments['file.md5'][index], encoding='utf-8')
                file['size'] = str(self.request.arguments['file.size'][index], encoding='utf-8')
                files.append(file)
        else:
            file_path = self.request.arguments['userfile.path']
            for index in range(len(file_path)):
                file = {}
                file['name'] = str(self.request.arguments['userfile.name'][index], encoding='utf-8')
                file['content_type'] = str(self.request.arguments['userfile.content_type'][index], encoding='utf-8')
                file['path'] = str(self.request.arguments['userfile.path'][index], encoding='utf-8')
                file['md5'] = str(self.request.arguments['userfile.md5'][index], encoding='utf-8')
                file['size'] = str(self.request.arguments['userfile.size'][index], encoding='utf-8')
                files.append(file)


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
        userdata = self.get_user_data(user, deep_number)
        userfilelist = userdata.filelist
        for item in userfilelist:
            if (item[0] == filename and item[1] == filetype and item[3] == filehash):
                ret = {'result': 'error'}
                ret['info'] = '同目录下已存在相同文件';
                self.write(json.dumps(ret))
                return

        passhash = crypto_helper.get_key(password, user.id, filehash, None, False)
        finalname = userdata.add_file(filename, filetype, filesize, filehash, passhash)
        password = crypto_helper.get_key(password, user.id)
        encrpath = os.path.join(userdatapath, finalname)

        temp_file = files[0]['path']
        now = datetime.now()
        nowdir = now.strftime('%Y%m%d')
        downpath = os.path.join(downloadpath, nowdir, filehash, filename)
        if (os.path.exists(downpath) is False):
            if (os.path.exists(os.path.join(downloadpath, nowdir, filehash)) is False):
                os.makedirs(os.path.join(downloadpath, nowdir, filehash))
            shutil.move(temp_file, downpath)
        else:
            os.unlink(temp_file)

        if (os.path.exists(encrpath) is True):
            os.unlink(encrpath)

        crypto_helper.encrypt_file(bytes.fromhex(password), downpath, encrpath)

        if (not user.isexist):
            user.set_isexist(True)
            self.set_current_user(user.get_session())

        ret = {'result': 'ok'}
        self.write(json.dumps(ret))
