# -*- coding: UTF-8 -*-

import os, os.path, sys
import json
import tornado
from base import BaseHandler
import shutil
from datetime import datetime, timedelta
from model.userfile import userfile
from settings import alioss,filetypelimit,filesizelimit,isuploadfileoss,userdatapath, downloadpath, downloadurl
from utils.oss_helper import Alioss

sys.path.append('..')


class FileHashHandler(BaseHandler):

    access_key_id = alioss['AccessKeyId']
    access_key_secret = alioss['AccessKeySecret']
    bucket_name = alioss['bucket']
    endpoint = alioss['endpoint']
    uploaddir = alioss['usertemppath']

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

        if (isuploadfileoss is True):
            oss = Alioss()
            now = datetime.now()
            nowdir = now.strftime('%Y%m%d')
            downpath =  '%s/%s/%s/%s' % (alioss['downloadpath'], nowdir, filehash, filename)
            if (oss.exists(downpath) is True):
                ret = {'result': '0'}
                self.write(json.dumps(ret))
                return
            else:
                beforetime = now - timedelta(days=1)
                beforetimedir = beforetime.strftime('%Y%m%d')
                beforetimedownpath = '%s/%s/%s/%s' % (alioss['downloadpath'], beforetimedir, filehash, filename)
                if (oss.exists(beforetimedownpath) is True):
                    oss.Bucket.copy_object(beforetimedownpath, downpath)
                    oss.Bucket.delete_object(beforetimedownpath)
                    ret = {'result': '0'}
                    self.write(json.dumps(ret))
                    return

            field_dict = {'result': '1'}
            # object名称
            field_dict['key'] = downpath
            # access key id
            field_dict['OSSAccessKeyId'] = self.access_key_id
            # Policy包括超时时间(单位秒)和限制条件condition
            field_dict['policy'] = oss.build_encode_policy(120, [['eq', '$bucket', self.bucket_name],
                                                                 ['content-length-range', 0, filesizelimit]])
            # 请求签名
            field_dict['signature'] = oss.build_signature(self.access_key_secret, field_dict['policy'])
            # callback，没有回调需求不填该域
            field_dict['callback'] = oss.bulid_callback('http://oss-demo.aliyuncs.com:23450',
                                                        'filename=${object}&size=${size}&mimeType=${mimeType}',
                                                        'application/x-www-form-urlencoded')

            field_dict['url'] = oss.build_post_url(self.endpoint, self.bucket_name)
            field_dict['filetypelimit'] = filetypelimit
            field_dict['filesizelimit'] = filesizelimit
            self.write(json.dumps(field_dict))
            return
        else:
            now = datetime.now()
            nowdir = now.strftime('%Y%m%d')
            downpath = os.path.join(downloadpath, nowdir, filehash, filename)
            if (os.path.exists(downpath) is True):
                ret = {'result': '0'}
                self.write(json.dumps(ret))
                return
            else:
                beforetime = now - timedelta(days=1)
                beforetimedir = beforetime.strftime('%Y%m%d')
                beforetimedownpath = os.path.join(downloadpath, beforetimedir, filehash, filename)
                if (os.path.exists(beforetimedownpath) is True):
                    if (os.path.exists(os.path.join(downloadpath, nowdir, filehash)) is False):
                        os.makedirs(os.path.join(downloadpath, nowdir, filehash))
                    shutil.move(beforetimedownpath, downpath)
                    ret = {'result': '0'}
                    self.write(json.dumps(ret))
                    return
                else:
                    ret = {'result': '1'}
                    self.write(json.dumps(ret))
                    return