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
    @tornado.gen.engine
    def get(self,sessionkey):
        out_trade_no = self.input_default('out_trade_no', None)
        if(not out_trade_no):
            url = '/view?k=%s&m=%s' % (sessionkey, '支付异常,请重试')
            self.redirect(url)
            return

        alipay = Alipay()
        paystatus = False
        for i in range(10):
            if alipay.query(out_trade_no) is True or alipay.refundallquery(out_trade_no) is True:
                paystatus = True
                break
            yield tornado.gen.sleep(3)

        # order is not paid in 30s , cancel this order
        if paystatus is False:
            alipay.tradecancel(out_trade_no=out_trade_no)
            url = '/view?k=%s&m=%s' % (sessionkey, '支付失败,请重试')
            self.redirect(url)
            return

        # 由down处理付款校验和退款业务处理
        self.redirect('/down?k=%s'% (sessionkey))






