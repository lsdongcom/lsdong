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
from model import userpay
sys.path.append('../../')

class AlipayNotifyHandler(BaseHandler):

    def check_xsrf_cookie(self):
        pass

    def get(self, payhash, filehash, passwordhash):
            self.paycheck(payhash, filehash, passwordhash)

    def post(self, payhash, filehash, passwordhash):
            self.paycheck(payhash, filehash, passwordhash)

    def paycheck(self, payhash, filehash, passwordhash):
        self.write("success")
        keys = self.request.arguments.keys()
        data = {}
        for key in keys:
            data[key] = self.input_default(key)

        alipay = Alipay()
        success = alipay.verifyurl(data)
        if success is False or data["trade_status"] not in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            return

        out_trade_no = data['out_trade_no']
        amount = data['total_amount']
        if alipay.refundquery(out_trade_no) is True:
            return

        keyhash = crypto_helper.get_key(payhash, filehash, None, None, False)
        nlen = len(keyhash) - len(passwordhash)
        keyhash = ''.join(list(keyhash)[nlen:])
        if (passwordhash != keyhash):
            amount = round(float(amount) * 0.8, 2)
            result = alipay.refund(refund_amount=amount, out_trade_no=out_trade_no)
        else:
            result = alipay.refund(refund_amount=amount,out_trade_no=out_trade_no)
