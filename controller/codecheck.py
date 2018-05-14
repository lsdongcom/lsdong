# -*- coding: UTF-8 -*-

import sys
import json
import tornado
from base import BaseHandler
sys.path.append('..')

class CodeCheckHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        code = self.input('c')
        codetype = self.input('t')
        if(codetype == '0'):
            sessioncode = self.get_session('mailcode')
        else:
            sessioncode = self.get_session('telcode')
        if (code in sessioncode):
            ret = {'result': 'ok'}
            self.write(json.dumps(ret))
        elif (not code):
            ret = {'result': 'error'}
            ret['info'] = '客户端session读取失败,请刷新页面后重试';
            self.write(json.dumps(ret))
        else:
            ret = {'result': 'error'}
            ret['info'] = '校验码错误,请重新输入'
            self.write(json.dumps(ret))

