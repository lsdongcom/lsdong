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

class AlipayBackDeepHandler(BaseHandler):

    def check_xsrf_cookie(self):
        pass

    def get(self, userid, code, bodyhash):
            self.paycheck(userid, code, bodyhash)

    def post(self, userid, code, bodyhash):
            self.paycheck(userid, code, bodyhash)

    def paycheck(self, userid, code, bodyhash):
        out_trade_no = self.input_default('out_trade_no', None)
        if (not out_trade_no):
            url = '/filedepth?k=%s&m=%s' % ('1', '支付异常,请重试[01]')
            self.redirect(url)
            return

        keys = self.request.arguments.keys()
        data = {}
        for key in keys:
            data[key] = self.input_default(key)

        alipay = Alipay()
        success = alipay.verifyurl(data)
        if not success:
            url = '/filedepth?k=%s&m=%s' % ('1', '支付异常,请重试[02]')
            self.redirect(url)
            return

        paystatus = False
        for i in range(10):
            time.sleep(3)
            if (alipay.query(out_trade_no)):
                paystatus = True
                break

        # order is not paid in 30s , cancel this order
        if paystatus is False:
            alipay.api_alipay_trade_cancel(out_trade_no=out_trade_no)
            url = '/filedepth?k=%s&m=%s' % ('1', '支付异常,请重试[03]')
            self.redirect(url)
            return

        timestamp = self.input_default('timestamp')
        amount = self.input_default('total_amount')
        if(not timestamp or not amount):
            url = '/filedepth?k=%s&m=%s' % ('1', '支付异常,请重试[04]')
            self.redirect(url)
            return
        timeout = datetime.now() - datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S')
        if (timeout > timedelta(hours=2) ):
            url = '/filedepth?k=%s&m=%s' % ('1', '支付异常,请重试[05]')
            self.redirect(url)
            return

        bodyhashconfim = crypto_helper.get_key(amount, userid, code, out_trade_no)
        if (bodyhash != bodyhashconfim):
            url = '/filedepth?k=%s&m=%s' % ('1', '支付异常,请重试[06]')
            self.redirect(url)
            return

        if(not file_helper.deep_auth_check(userid, code)):
            file_helper.deep_auth_create(userid, code)

        url = '/filedepth?k=0'
        self.redirect(url)