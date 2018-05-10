# -*- coding: UTF-8 -*-

import os
import shutil
import oss2
from datetime import datetime
import time
import json
import base64
import hmac
import hashlib
from settings import alioss

class Alioss():
    _access_key_id = alioss['AccessKeyId']
    _access_key_secret = alioss['AccessKeySecret']
    _bucket_name = alioss['bucket']
    _endpoint = alioss['endpoint']
    _uploaddir = alioss['usertemppath']
    def __init__(self):
        self._bucket = oss2.Bucket(oss2.Auth(self._access_key_id, self._access_key_secret), self._endpoint, self._bucket_name)

    @property
    def AccessKeyId(self):
        return self._access_key_id

    @property
    def Bucket(self):
        return self._bucket

    def build_gmt_expired_time(self, expire_time):
        """生成GMT格式的请求超时时间
        :param int expire_time: 超时时间，单位秒
        :return str GMT格式的超时时间
        """
        now = int(time.time())
        expire_syncpoint = now + expire_time

        expire_gmt = datetime.fromtimestamp(expire_syncpoint).isoformat()
        expire_gmt += 'Z'

        return expire_gmt

    def build_encode_policy(self, expired_time, condition_list):
        """生成policy
        :param int expired_time: 超时时间，单位秒
        :param list condition_list: 限制条件列表
        """
        policy_dict = {}
        policy_dict['expiration'] = self.build_gmt_expired_time(expired_time)
        policy_dict['conditions'] = condition_list

        policy = json.dumps(policy_dict).strip()
        policy_encode = base64.b64encode(policy.encode(encoding='utf-8'))

        return str(policy_encode, encoding='utf-8')

    def build_signature(self, access_key_secret, encode_policy):
        """生成签名
        :param str access_key_secret: access key secret
        :param str encode_policy: 编码后的Policy
        :return str 请求签名
        """
        h = hmac.new(access_key_secret.encode(encoding='utf-8'), encode_policy.encode(encoding='utf-8'), hashlib.sha1)
        signature = base64.encodebytes(h.digest()).strip()
        return str(signature, encoding='utf-8')

    def bulid_callback(self, cb_url, cb_body, cb_body_type=None, cb_host=None):
        """生成callback字符串
        :param str cb_url: 回调服务器地址，文件上传成功后OSS向此url发送回调请求
        :param str cb_body: 发起回调请求的Content-Type，默认application/x-www-form-urlencoded
        :param str cb_body_type: 发起回调时请求body
        :param str cb_host: 发起回调请求时Host头的值
        :return str 编码后的Callback
        """
        callback_dict = {}

        callback_dict['callbackUrl'] = cb_url

        callback_dict['callbackBody'] = cb_body
        if cb_body_type is None:
            callback_dict['callbackBodyType'] = 'application/x-www-form-urlencoded'
        else:
            callback_dict['callbackBodyType'] = cb_body_type

        if cb_host is not None:
            callback_dict['callbackHost'] = cb_host

        callback_param = json.dumps(callback_dict).strip()
        base64_callback = base64.b64encode(callback_param.encode(encoding='utf-8'));

        return str(base64_callback, encoding='utf-8')

    def build_post_url(self, endpoint, bucket_name):
        """生成POST请求URL
        :param str endpoint: endpoint
        :param str bucket_name: bucket name
        :return str POST请求URL
        """
        if endpoint.startswith('http://'):
            return endpoint.replace('http://', 'http://{0}.'.format(bucket_name))
        elif endpoint.startswith('https://'):
            return endpoint.replace('https://', 'https://{0}.'.format(bucket_name))
        else:
            return 'http://{0}.{1}'.format(bucket_name, endpoint)

    def exists(self,filepath):
        return self._bucket.object_exists(filepath)

    def del_dir(self,dirpath,excludepath=None,excludepath1=None):
        if dirpath is None or dirpath =="":
            return
        if alioss["usertemppath"] not in dirpath and alioss["downloadpath"] not in dirpath:
            return

        for obj in oss2.ObjectIterator(self._bucket, prefix=dirpath, delimiter='/', max_keys=1000):
            if(excludepath in obj.key or excludepath1 in obj.key):
                continue
            elif obj.is_prefix():
                self.del_dir(obj.key,excludepath,excludepath1)
            else:
                self._bucket.delete_object(obj.key)

