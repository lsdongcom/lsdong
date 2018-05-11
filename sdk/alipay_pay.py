# -*- coding: utf-8 -*-

import unittest
import json
import subprocess

from alipay import AliPay, ISVAliPay
from alipay.exceptions import AliPayValidationError
from settings import alipay
from urllib import parse
from safeutils import crypto_helper

alipay_debug = alipay['debug']
alipay_id = alipay['appid']
alipay_url = alipay['alipay_url']
app_private_key_path = alipay['app_private_key_path']
app_public_key_path = alipay['app_public_key_path']
app_return_url = alipay['app_return_url']
app_notify_url = alipay['app_notify_url']

class Alipay():
    def __init__(self):
        self._alipay = AliPay(
            appid=alipay_id,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=app_private_key_path,
            alipay_public_key_path=app_public_key_path,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=alipay_debug  # 默认False
        )
        if alipay_debug is True:
            self._gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self._gateway = "https://openapi.alipay.com/gateway.do"

    def getpaycheckurl(self,sessionkey, out_trade_no, subject, total_amount, payhash, filehash, passwordhash):
        returnurl = '%s/%s' % (app_return_url, sessionkey)
        notify_url = '%s/%s/%s/%s' % (app_notify_url, payhash, filehash, passwordhash)
        if (len(notify_url) > 190):
            nlen = len(notify_url) - 190
            passwordhash = ''.join(list(passwordhash)[nlen:])
            notify_url = '%s/%s/%s/%s' % (app_notify_url, payhash, filehash, passwordhash)

        order_string = self._alipay.api_alipay_trade_page_pay(
            out_trade_no=out_trade_no,
            total_amount=total_amount,
            subject=subject,
            return_url=returnurl,
            notify_url=notify_url  # 可选, 不填则使用默认notify url
        )
        alipay_request = '%s?%s' % (self._gateway, order_string)
        return alipay_request

    def getpaydeepurl(self, out_trade_no, subject, total_amount, userid, code):
        bodyhash = crypto_helper.get_key(str(total_amount), userid, str(code), out_trade_no)
        returnurl = '%s%s/%s/%s/%s' % (app_return_url, 'deep', userid, code, bodyhash)
        notify_url = '%s%s/%s/%s/%s' % (app_return_url, 'deep', userid, code, bodyhash)
        order_string = self._alipay.api_alipay_trade_page_pay(
            out_trade_no=out_trade_no,
            total_amount=total_amount,
            subject=subject,
            return_url=returnurl,
            notify_url=notify_url  # 可选, 不填则使用默认notify url
        )
        alipay_request = '%s?%s' % (self._gateway, order_string)
        return alipay_request

    def verifyurl(self,data):
        signature = data.pop("sign")
        success = self._alipay.verify(data, signature)
        return success


    def query(self,out_trade_no):
        result = self._alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
        if result.get("trade_status", "") == "TRADE_SUCCESS":
            return True
        return False

    def refund(self, refund_amount, out_trade_no):
        result = self._alipay.api_alipay_trade_refund(refund_amount=refund_amount, out_trade_no=out_trade_no,
                                                      trade_no=None, out_request_no=out_trade_no)
        print('refund', result)
        if result["code"] == "10000":
            return True
        return False

    def refundquery(self,out_trade_no):
        result = self._alipay.api_alipay_trade_fastpay_refund_query(out_request_no=out_trade_no,out_trade_no=out_trade_no)
        print('refundquery',result)
        if result["code"] == "10000":
            return True
        return False