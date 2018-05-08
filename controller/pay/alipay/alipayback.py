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

class AlipayBackHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self,sessionkey):
        out_trade_no = self.input_default('out_trade_no', None)
        if(not out_trade_no):
            url = '/view?k=%s&m=%s' % (sessionkey, '支付异常,请重试')
            self.redirect(url)
            return

        alipay = Alipay()
        paystatus = False
        for i in range(10):
            time.sleep(3)
            if (alipay.query(out_trade_no)):
                paystatus = True
                break

        # order is not paid in 30s , cancel this order
        if paystatus is False:
            alipay.api_alipay_trade_cancel(out_trade_no=out_trade_no)
            url = '/view?k=%s&m=%s' % (sessionkey, '支付失败,请重试')
            self.redirect(url)
            return

        self.redirect('/down?k=%s'% (sessionkey))






