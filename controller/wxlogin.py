# -*- coding: UTF-8 -*-

import os, sys
from base import BaseHandler
from settings import wechatapi
import requests
from safeutils.hashids_helper import *
from model.userinfo import userinfo
from safeutils import crypto_helper
import json
from settings import alioss,userinfopath,isuploadfileoss
from utils.oss_helper import Alioss
from utils.file_helper import file_exists,file_read,file_write
sys.path.append('..')

class WXLoginHandler(BaseHandler):
    usertype = 'weixin'
    def get(self):
        code = self.input_default('code')
        if(not code):
            self.redirect('/')
            return

        data = self.get_access_token(code)
        if('errmsg' in data):
            self.write(data['errmsg'])
            return

        unionid, nickname, errmsg = self.get_userinfo(data)
        if (errmsg):
            self.write(errmsg)
            return

        unionid = clear_unionid(unionid)
        idx = self.get_id(unionid)
        idx, isexist = self.check_idx(unionid, idx, self.usertype)
        user = userinfo(idx, unionid, nickname, self.usertype, isexist)
        self.set_current_user(user.get_session())
        self.redirect('/')

    def get_id(self,unionid):
        sid, skey = split_unionid(unionid)
        hashid = get_hashid(sid, skey)
        idx = '%s%s' % (get_key(unionid, hashid, self.usertype), sid)
        return idx

    def check_idx(self,unionid, idx, usertype):
        oss = Alioss()
        if (isuploadfileoss is True):
            userdir = '%s/%s' % (alioss['userinfopath'], usertype)
            filepath = '%s/%s' % (userdir, idx)
        else:
            userdir = os.path.join(userinfopath, usertype)
            filepath = os.path.join(userdir, idx)

        if file_exists(filepath, oss) is False:
            return idx, False
        b_unionid = bytes(unionid, encoding='utf-8')
        filedata = file_read(filepath, oss)
        filedata = crypto_helper.aes_decrypt(str(filedata, encoding='utf-8'), b_unionid)
        filedata = json.loads(filedata)
        if (filedata['userid'] == unionid):
            return idx, True

        for i in range(9):
            newidx = '%s%s' % (idx, str(i))
            if (isuploadfileoss is True):
                newfilepath = '%s%s' % (userdir, newidx)
            else:
                newfilepath = os.path.join(userdir, newidx)
            if file_exists(newfilepath) is False:
                return newidx, False
            filedata = file_read(filepath, oss)
            filedata = crypto_helper.aes_decrypt(str(filedata, encoding='utf-8'), b_unionid)
            filedata = json.loads(filedata)
            if (filedata['userid'] == unionid):
                return idx, True
        print('%s userinfo idx:%s error. please check', usertype, idx)
        return '', False

    def get_access_token(self,code):
        wechat_request = wechatapi['access_token_uri'] % (code)
        data=requests.get(wechat_request).json()
        # 正确的返回：
        # {
        #     "access_token": "ACCESS_TOKEN",
        #     "expires_in": 7200,
        #     "refresh_token": "REFRESH_TOKEN", "openid": "OPENID",
        #     "scope": "SCOPE"
        # }
        # 错误返回样例：
        # {
        #     "errcode": 40029, "errmsg": "invalid code"
        # }
        # data = {
        #     "access_token": "ACCESS_TOKEN123",
        #     "expires_in": 7200,
        #     "refresh_token": "REFRESH_TOKEN", "openid": "OPENIDabc",
        #     "scope": "SCOPE"
        # }
        return data

    def get_userinfo(self,data):
        wechat_request = wechatapi['access_userinfo_uri'] % (data['access_token'].strip(),data['openid'].strip())
        data = requests.get(wechat_request).json()
        if ('errmsg' in data):
            return '', '', data['errmsg']
        # 正确的返回：
        # {
        #     "openid": "OPENID",
        #     "nickname": "NICKNAME",
        #     "sex": 1,
        #     "province": "PROVINCE",
        #     "city": "CITY",
        #     "country": "COUNTRY",
        #     "headimgurl": "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/0",
        #     "privilege": [
        #         "PRIVILEGE1",
        #         "PRIVILEGE2"
        #     ],
        #     "unionid": " o6_bmasdasdsad6_2sgVt7hMZOPfL"
        # }
        # 错误返回样例：
        # {
        #     "errcode": 40003, "errmsg": "invalid openid"
        # }
        # data = {
        #     "openid": "OPENID",
        #     "nickname": "NICKNAME",
        #     "sex": 1,
        #     "province": "PROVINCE",
        #     "city": "CITY",
        #     "country": "COUNTRY",
        #     "headimgurl": "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/0",
        #     "privilege": [
        #         "PRIVILEGE1",
        #         "PRIVILEGE2"
        #     ],
        #     "unionid": " o6_bmasdasdsad6_2sgVt7hMZOPfL"
        # }
        return data['unionid'].strip(), data['nickname'].encode('iso-8859-1').decode('utf-8'), None


