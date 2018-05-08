# -*- coding: UTF-8 -*-

import sys
from base import BaseHandler
from settings import wechatapi
import requests
from safeutils.hashids_helper import *
from model.userinfo import userinfo
from safeutils import crypto_helper
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
        idx, isexist = crypto_helper.check_idx(unionid, idx, self.usertype)
        user = userinfo(idx, unionid, nickname, self.usertype, isexist)
        self.set_current_user(user.get_session())
        self.redirect('/')

    def get_id(self,unionid):
        sid, skey = split_unionid(unionid)
        hashid = get_hashid(sid, skey)
        idx = '%s%s' % (get_key(unionid, hashid, self.usertype), sid)
        return idx

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


