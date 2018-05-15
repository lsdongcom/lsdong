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
from settings import encryptkey
sys.path.append('../../')

class AlipayNotifyHandler(BaseHandler):

    def check_xsrf_cookie(self):
        pass

    def get(self, retcontent):
            self.paycheck(retcontent)

    def post(self, retcontent):
            self.paycheck(retcontent)

    def paycheck(self, retcontent):
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

        retkey = crypto_helper.get_key(str(amount), out_trade_no, str(encryptkey, encoding='utf-8'))
        retkey = ''.join(list(retkey)[:32])
        retkey = bytes(retkey, encoding='utf-8')
        retcontent = crypto_helper.aes_decrypt(retcontent, retkey)
        retcontent = json.loads(retcontent)

        if ('status' in retcontent and retcontent['status'] == '1'):
            result = alipay.refund(refund_amount=amount, out_trade_no=out_trade_no)
        else:
            amount = round(float(amount) * 0.8, 2)
            result = alipay.refund(refund_amount=amount, out_trade_no=out_trade_no)

