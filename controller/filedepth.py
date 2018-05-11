# -*- coding: UTF-8 -*-

import sys
import re
import json
import tornado
import uuid
from datetime import datetime
from base import BaseHandler
from model.userfile import userfile
import numpy as np
from sdk.alipay_pay import Alipay
from utils.file_helper import getfiletypename,lock_site_notify
from utils import file_helper
from settings import siteinfo
sys.path.append('..')


class FileDepthHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        islock, site_notify = lock_site_notify()
        user = self.get_current_user()
        deep_number = self.get_deep_number(user)
        message = self.input_default('m', None)

        if(self.input_default('k')  is None or not message is None):
            self.render('filedepth.html', username=user.nickname, deep_number=deep_number, message=message, site_notify=site_notify, siteinfo=siteinfo)
            return

        password = self.get_session('%s_%s' % (user.id, 'auth'))
        if(not password):
            self.render('filedepth.html', username=user.nickname, deep_number=deep_number, message=message, site_notify=site_notify, siteinfo=siteinfo)
            return

        self.clear_cookie('%s_%s' % (user.id, 'auth'))
        if (deep_number == 1):
            filedata = userfile(user, None, None)
        else:
            filepath, filehash = self.get_deep_dict(user, deep_number - 1)
            filedata = userfile(user, filepath, filehash)

        ret = self.go_deep_path(user, deep_number, password, '2', filedata)
        if(ret['result'] == 'error'):
            message = ret['info']
            self.render('filedepth.html', username=user.nickname, deep_number=deep_number, message=message, site_notify=site_notify, siteinfo=siteinfo)

        self.redirect('/filedepth')
        return

    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        password = str(self.input_default('p', None)).strip()
        requesttype = self.input_default('t', None)
        code = self.input_default('c', None)
        amount = self.input_default('a', None)
        deep_number = self.get_deep_number(user)
        if(code and amount):
            self.set_session('%s_%s' % (user.id, 'auth'), password)
            self.getpayurl(user.id, code, amount, deep_number)
            return

        if (deep_number > 1 and requesttype == '0'):
            self.set_deep_number(user, deep_number - 1)
            ret = {'result': 'ok'}
            self.write(json.dumps(ret))
            return

        deep_number = self.get_deep_number(user)
        if (deep_number == 1):
            filedata = userfile(user, None, None)
        else:
            filepath, filehash = self.get_deep_dict(user, deep_number - 1)
            filedata = userfile(user, filepath, filehash)
        ret = self.go_deep_path(user, deep_number, password, requesttype, filedata)
        self.write(json.dumps(ret))

    def go_deep_path(self,user,deep_number,password,requesttype,filedata):
        if (filedata.deep_path):
            deeppath, deephash = filedata.get_deep_path(password)
            if (not deeppath):
                ret = {'result': 'error'}
                ret['code'] = '0'
                ret['info'] = '密码错误,请重试'
                return ret
            self.set_deep_dict(user, deep_number, deeppath, deephash)
        else:
            if (deep_number >= 50):
                ret = {'result': 'error'}
                ret['code'] = '0'
                ret['info'] = '非常抱歉,目前嵌套层最高只能创建到50层'
                return ret
            if (requesttype=='1'):
                ret = {'result': '?'}
                return ret
            else:
                filelist = filedata.filelist
                openauth = file_helper.deep_auth_check(user.id,'1')
                if(not openauth):
                    if (len(filelist) <= 0):
                        ret = {'result': 'error'}
                        ret['code'] = '1'
                        ret['info'] = '非常抱歉,您还没有使用本层任何加密方式,无法开启下一嵌套层,您可付款不低于1分钱的任意金额解除此类限制,付款后24小时内有效,如需解锁请确认后再次提交'
                        return ret

                    alist = np.array(filelist)
                    for i in range(5):
                        l = len(alist[np.where(alist[:, 1] == str(i + 1))])
                        if (l <= 0):
                            filetypename = getfiletypename(i + 1)
                            ret = {'result': 'error'}
                            ret['code'] = '1'
                            ret['info'] = '非常抱歉,您还没有使用本层“%s”的加密方式,无法开启下一嵌套层,您可付款不低于1分钱的任意金额解除此类限制,付款后24小时内有效,如需解锁请确认后再次提交' % (
                            filetypename)
                            return ret
                topdeep =  int((deep_number - deep_number % 5) / 5 + 2)
                deepauth = file_helper.deep_auth_check(user.id, str(topdeep))
                if (deep_number >= 5 and not deepauth):
                    ret = {'result': 'error'}
                    ret['code'] = '2'
                    ret['info'] = '非常抱歉,目前仅开放前5层嵌套层,您可付款1元解除后续5层限制,付款后24小时内有效,存储的文件长期有效,如需解锁请确认后再次提交'
                    return ret

                deeppath, deephash = filedata.create_deep_path(password)
                self.set_deep_dict(user, deep_number, deeppath, deephash)

        self.set_deep_number(user, deep_number + 1)

        ret = {'result': 'ok'}
        return ret

    def getpayurl(self,userid,code,amount,deep_number):
        if(code == '1'):
            subject = '嵌套层开启限制解锁'
        else:
            amount = '1.00'
            subject = '嵌套层等级限制解锁'
            code = int((deep_number - deep_number % 5) / 5 + 2)

        if len(amount)>13:
            ret = {'result': 'error'}
            ret['info'] = '您输入的金额超过限制'
            self.write(json.dumps(ret))
            return

        filter_rule = '^([1-9]\d{0,9}|0)([.]?|(\.\d{1,2})?)$'
        if not re.search(filter_rule, amount):
            ret = {'result': 'error'}
            ret['info'] = '您输入的金额无效'
            self.write(json.dumps(ret))
            return

        if float(amount) < 0.01:
            ret = {'result': 'error'}
            ret['info'] = '您输入的金额小于0.01元'
            self.write(json.dumps(ret))
            return

        out_trade_no = '%s%s' % (datetime.now().strftime('%Y%m%d%H%M%S'), uuid.uuid1())
        out_trade_no = out_trade_no.replace('-', '')
        amount = '%.2f' % float(amount)
        code = '%d' % int(code)
        payurl = Alipay().getpaydeepurl(out_trade_no, subject, amount, userid, code)
        ret = {'result': 'pay'}
        ret['url'] = payurl;
        self.write(json.dumps(ret))
        return

