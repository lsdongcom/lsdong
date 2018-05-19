# -*- coding: UTF-8 -*-

import os,os.path,sys
import json
import tornado
from base import BaseHandler
import time
import uuid
from datetime import datetime,timedelta
from utils import  tool
from sdk.alipay_pay import Alipay
from safeutils import crypto_helper
from utils import file_helper
from model import userpay

sys.path.append('../../')

class AlipayNotifyDeepHandler(BaseHandler):

    def check_xsrf_cookie(self):
        pass

    def get(self, userid, code, bodyhash):
            self.paycheck(userid, code, bodyhash)

    def post(self, userid, code, bodyhash):
            self.paycheck(userid, code, bodyhash)

    def paycheck(self, userid, code, bodyhash):
        self.write("success")

        out_trade_no = self.input_default('out_trade_no', None)
        if (not out_trade_no):
            return

        keys = self.request.arguments.keys()
        data = {}
        for key in keys:
            data[key] = self.input_default(key)

        alipay = Alipay()
        success = alipay.verifyurl(data)
        if success is False:
            return

        if alipay.query(out_trade_no) is False:
            return

        timestamp = self.input_default('timestamp')
        amount = self.input_default('total_amount')
        if(not timestamp or not amount):
            return
        timeout = datetime.now() - datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S')
        if (timeout > timedelta(minutes=30) ):
            return

        bodyhashconfim = crypto_helper.get_key(amount, userid, code, out_trade_no)
        if (bodyhash != bodyhashconfim):
            return

        if(not file_helper.deep_auth_check(userid, code)):
            file_helper.deep_auth_create(userid, code)



