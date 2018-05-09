# -*- coding: UTF-8 -*-

from base import BaseHandler
import sys
import hashlib
import hmac
import mimetypes
import datetime
from calendar import timegm
from email.utils import formatdate
from urllib import parse
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient, HTTPError

sys.path.append('../../')

class Alioss_Notify_Handler(BaseHandler):

    def check_xsrf_cookie(self):
        pass

    def get(self):
        self.OSSNotifyReply()

    def post(self, payhash, filehash, passwordhash):
        self.OSSNotifyReply()

    def OSSNotifyReply(self):
        #response to OSS
        resp_body = '{"Status":"OK"}'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(resp_body)))
        self.end_headers()
        self.write(resp_body)



