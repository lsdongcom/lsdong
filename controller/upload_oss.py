# -*- coding: UTF-8 -*-

import os,os.path,sys
import json
import tornado
from base import BaseHandler
from datetime import datetime
from safeutils import crypto_helper
from model.userfile import userfile
from utils.file_helper import lock_site_notify
from settings import alioss,userdatapath, downloadpath
from utils.oss_helper import Alioss

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

        oss = Alioss()
        now = datetime.now()
        nowdir = now.strftime('%Y%m%d')
        ossdownpath = '%s/%s/%s/%s' % (alioss['downloadpath'], nowdir, filehash, filename)
        localdownpath = os.path.join(downloadpath, nowdir, filehash, filename)
        ossencrpath = '%s/%s' % (alioss['userdatapath'], finalname)
        localencrpath = os.path.join(userdatapath, finalname)
        if (oss.exists(ossdownpath) is False):
            filedata.del_file(finalname)
            ret = {'result': 'error'}
            ret['info'] = '文件上传失败';
            self.write(json.dumps(ret))
            return
        else:
            if (os.path.exists(os.path.join(downloadpath, nowdir, filehash)) is False):
                os.makedirs(os.path.join(downloadpath, nowdir, filehash))
            if(os.path.exists(localdownpath) is False):
                oss.Bucket.get_object_to_file(ossdownpath, localdownpath)

            # 此处下载到本地进行解码的文件处理完后多长时间删除的逻辑处理需要更多的思考，目前采取48小时删除方式清理磁盘，systask定时任务每天定时执行
            # 下载的逻辑处理与此处相同
            crypto_helper.encrypt_file(bytes.fromhex(password), localdownpath, localencrpath)
            oss.Bucket.put_object_from_file(ossencrpath, localencrpath)
            if (os.path.exists(localencrpath) is True):
                os.unlink(localencrpath)
            if (user.isexist is False):
                user.set_isexist(True)
                self.set_current_user(user.get_session())
            ret = {'result': 'ok'}
            self.write(json.dumps(ret))