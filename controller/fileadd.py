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
from utils.file_helper import getfiletypename,lock_site_notify,checkfilename
from settings import isuploadfilenginx,filesizelimit
sys.path.append('..')

class FileAddHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        islock, site_notify = lock_site_notify()
        if(islock is True):
            self.write(site_notify)
            return

        user = self.get_current_user()
        filetype = self.input_default('t')
        istxt = self.input_default('c')
        if filetype:
            filetypename = getfiletypename(int(filetype))
            if istxt:
                self.render('fileaddtxt_' + filetype + '.html', username=user.nickname, filetype=filetype,
                            filetypename=filetypename, site_notify=site_notify)
            else:
                self.render('fileadd_' + filetype + '.html', username=user.nickname, filetype=filetype, filetypename=filetypename,
                            isuploadfilenginx=isuploadfilenginx, filesizelimit=filesizelimit, site_notify=site_notify)

    @tornado.web.authenticated
    def post(self):
        islock, site_notify = lock_site_notify()
        if (islock is True):
            ret = {'result': 'error'}
            ret['info'] = site_notify;
            self.write(ret)
            return

        filename = self.input_default('filename', None)
        filecontent = self.input_default('filecontent', None)
        filehash = self.input_default('filehash', None)
        filetype = self.input_default('t', None)

        password = self.input_default('p', None)

        if (filename == None or filecontent == None or filehash == None or filetype == None or password == None):
            ret = {'result': 'error'}
            ret['info'] = '参数异常或缺失';
            self.write(json.dumps(ret))
            return

        filesize = len(filecontent)
        if (filesize == 0):
            ret = {'result': 'error'}
            ret['info'] = '参数异常或上传的文件为空文件';
            self.write(json.dumps(ret))
            return

        if (filesize > 10240):
            ret = {'result': 'error'}
            ret['info'] = '上传的文件超过长度限制';
            self.write(json.dumps(ret))
            return

        if not checkfilename(filename):
            ret = {'result': 'error'}
            ret['info'] = '文件名含有特殊字符';
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
            if (item[0] == filename and item[1] == filetype and item[3] == filehash):
                ret = {'result': 'error'}
                ret['info'] = '同目录下已存在相同文件';
                self.write(json.dumps(ret))
                return

        passhash = crypto_helper.get_key(password, user.id, filehash, None, False)
        finalname = filedata.add_file(filename, filetype, filesize, filehash, passhash)
        password = crypto_helper.get_key(password, user.id)
        encrpath = os.path.join(userdatapath, finalname)

        now = datetime.now()
        nowdir = now.strftime('%Y%m%d')
        downpath = os.path.join(downloadpath, nowdir, filehash, filename)
        if (os.path.exists(os.path.join(downloadpath, nowdir, filehash)) is False):
            os.makedirs(os.path.join(downloadpath, nowdir, filehash))

        temp_file = os.path.join(usertemppath, finalname)
        with open(temp_file, 'w') as up:
            up.write(filecontent)

        if (os.path.exists(downpath) is False):
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