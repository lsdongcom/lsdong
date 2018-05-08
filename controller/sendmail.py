# -*- coding: UTF-8 -*-

import os,os.path,sys
import json
import tornado
from base import BaseHandler
import time
from utils import  tool
sys.path.append('..')

class SendMailHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        mailaddr = self.input_default('mail', None)
        if (not mailaddr):
            ret = {'result': 'error'}
            ret['info'] = '邮箱地址不能为空';
            self.write(json.dumps(ret))
            return
        checkcode = tool.random_number(6)
        status, e = tool.send_email(mailaddr, '老树洞邮箱校验码：' + checkcode, '老树洞邮箱校验', '老树洞管理员')
        if(status):
            self.set_session('mailcode', checkcode)
            ret = {'result': 'ok'}
            self.write(json.dumps(ret))
        else:
            ret = {'result': 'error'}
            ret['info'] = str(e);
            self.write(json.dumps(ret))

