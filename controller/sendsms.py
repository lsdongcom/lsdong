# -*- coding: UTF-8 -*-


import sys
import json
import tornado
from base import BaseHandler
import uuid
from utils import  tool
from sdk import aliyun_sms
from settings import aliyun
sys.path.append('..')

class SendSMSHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        teladdr = self.input_default('tel', None)
        if (not teladdr):
            ret = {'result': 'error'}
            ret['info'] = '手机号码不能为空';
            self.write(json.dumps(ret))
            return

        if(aliyun['debug'] is True):
            self.set_session('telcode', '111111')
            ret = {'result': 'ok'}
            self.write(json.dumps(ret))
            return

        checkcode = tool.random_number(6)
        business_id = uuid.uuid1()
        params = "{\"code\":\"" + checkcode + "\"}"

        status = aliyun_sms.send_sms(business_id, teladdr, "老树洞", "SMS_129740057", params)
        status = json.loads(status)
        if(status['Code'] == 'OK'):
            self.set_session('telcode', checkcode)
            ret = {'result': 'ok'}
            self.write(json.dumps(ret))
        else:
            print(status)
            ret = {'result': 'error'}
            ret['info'] = '短信发送失败，请稍候重新获取';
            self.write(json.dumps(ret))

