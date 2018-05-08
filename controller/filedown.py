# -*- coding: UTF-8 -*-

import os,os.path,sys
import json
import tornado
from base import BaseHandler
import shutil
import uuid
from datetime import datetime,timedelta
from safeutils import crypto_helper
from model.userinfo import userinfo
from model.userfile import userfile
from  model import userpay
from utils.file_helper import getfiletypename,lock_site_notify
from settings import userdatapath,downloadpath,downloadurl
from urllib.parse import urljoin
from sdk.alipay_pay import Alipay
sys.path.append('..')

class FileDownHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        sessionkey = self.input_default('k')
        if (not userpay.checkPaySession(self, sessionkey)):
            url = '/view?k=%s&m=%s' % (sessionkey, '支付失败,请重试')
            self.redirect(url)
            return

        user = self.get_current_user()
        fileinfo = userpay.getPaySession(self, sessionkey)

        payno = fileinfo['payno']
        fileindex = int(fileinfo['i'])
        filetype = fileinfo['t']
        actiontype = fileinfo['a']
        password = fileinfo['password']
        deep_number = fileinfo['deep_number']
        if (deep_number == 1):
            filedata = userfile(user, None, None)
        else:
            filepath, filehash = self.get_deep_dict(user, deep_number - 1)
            filedata = userfile(user, filepath, filehash)
        filelist = filedata.filelist
        data = []
        for item in filelist:
            if (item[1] == filetype):
                data.append([item[0], item[1], item[2], item[3], item[4], item[5], item[6]])

        if (fileindex > len(data)):
            ret = {'result': 'error'}
            ret['info'] = '参数异常'
            self.write(json.dumps(ret))
            return

        selectitem = data[fileindex]
        filename = selectitem[0]
        filehash = selectitem[3]
        passwordhash = selectitem[4]
        savename = selectitem[5]
        amount = userpay.getPayAmount(filetype, password)
        keyhash = crypto_helper.get_key(password, user.id, filehash, None, False)

        alipay = Alipay()
        if not alipay.refundquery(payno):
            if (passwordhash != keyhash):
                amount = round(float(amount) * 0.8, 2)
                result = alipay.refund(refund_amount=amount, out_trade_no=data['out_trade_no'])
                self.redirect('view?i=%s&t=%s&a=%s&name=%s&m=%s' % (fileindex, filetype,actiontype,actiontype, '密码错误，请重试'))
                return
            else:
                result = alipay.refund(refund_amount=amount, out_trade_no=data['out_trade_no'])

        if (actiontype == '1'):
            filedata.del_file(savename)
            encrpath = os.path.join(userdatapath, savename)
            os.unlink(encrpath)
            self.redirect('list?t=%s&m=%s' % (filetype,'删除成功'))
            return
        elif (actiontype == '0'):
            downurl = self.get_filepath(user, filename, filehash)
            if (downurl):
                self.redirect(downurl)
                return
            else:
                now = datetime.now()
                nowdir = now.strftime('%Y%m%d')
                downpath = os.path.join(downloadpath, nowdir, filehash, filename)
                if (not os.path.exists(downpath)):
                    if (not os.path.exists(os.path.join(downloadpath, nowdir, filehash))):
                        os.makedirs(os.path.join(downloadpath, nowdir, filehash))

                    beforetime = now - timedelta(days=1)
                    beforetimedir = beforetime.strftime('%Y%m%d')
                    beforetimedownpath = os.path.join(downloadpath, beforetimedir, filehash, filename)
                    if (os.path.exists(beforetimedownpath)):
                        shutil.move(beforetimedownpath, downpath)
                    else:
                        tempfile = '%s%s' % (filename, '.tmp')
                        temppath = os.path.join(downloadpath, nowdir, filehash, tempfile)
                        if (not os.path.exists(temppath)):
                            encrpath = os.path.join(userdatapath, savename)
                            decryhash = crypto_helper.get_key(password, user.id)
                            crypto_helper.decrypt_file(bytes.fromhex(decryhash), encrpath, temppath)
                            shutil.move(temppath, downpath)

                downurl = '%s/%s/%s/%s' % (downloadurl, nowdir, filehash, filename)
                self.set_filepath(user, filename, filehash, downurl)
                self.redirect(downurl)

    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        fileindex = int(self.input_default('i'))
        filetype = self.input_default('t')
        actiontype = self.input_default('a')
        password = str(self.input_default('p', None)).strip()
        deep_number = self.get_deep_number(user)

        if (deep_number == 1):
            filedata = userfile(user, None, None)
        else:
            filepath, filehash = self.get_deep_dict(user, deep_number - 1)
            filedata = userfile(user, filepath, filehash)
        filelist = filedata.filelist
        data = []
        for item in filelist:
            if (item[1] == filetype):
                data.append([item[0], item[1], item[2], item[3], item[4], item[5], item[6]])

        if (fileindex > len(data)):
            ret = {'result': 'error'}
            ret['info'] = '参数异常'
            self.write(json.dumps(ret))
            return

        selectitem = data[fileindex]
        filename = selectitem[0]
        filehash = selectitem[3]
        passwordhash = selectitem[4]
        savename = selectitem[5]
        keyhash = crypto_helper.get_key(password, user.id, filehash, None, False)

        if (int(filetype) > 3):
            sessionkey = userpay.getSessionKey(user.id, fileindex, filetype, filename)
            if(not userpay.checkPaySession(self, sessionkey)):
                islock, site_notify = lock_site_notify()
                if (islock is True):
                    ret = {'result': 'error'}
                    ret['info'] = site_notify;
                    self.write(ret)
                    return

                trade_no = '%s%s' % (datetime.now().strftime('%Y%m%d%H%M%S'), uuid.uuid1())
                trade_no = trade_no.replace('-', '')
                subject = '%s%s' % (filename, '权限校验')
                userpay.setPaySession(self, sessionkey,trade_no, user.id, fileindex, filetype, actiontype, filename, deep_number,
                                      password)
                amount = userpay.getPayAmount(filetype, password)
                payhash = crypto_helper.get_key(password, user.id, None, None, False)
                payurl = Alipay().getpaycheckurl(sessionkey, trade_no, subject, amount, payhash, filehash, passwordhash)
                ret = {'result': 'pay'}
                ret['url'] = payurl;
                self.write(json.dumps(ret))
                return

        if(passwordhash != keyhash):
            ret = {'result': 'error'}
            ret['info'] = '密码错误，请重试';
            self.write(json.dumps(ret))
            return
        elif(actiontype == '1'):
            filedata.del_file(savename)
            encrpath = os.path.join(userdatapath, savename)
            os.unlink(encrpath)
            ret = {'result': 'ok'}
            self.write(json.dumps(ret))
            return
        elif(actiontype == '0'):
            downurl = self.get_filepath(user, filename, filehash)
            if(downurl):
                ret = {'result': downurl}
                self.write(json.dumps(ret))
                return
            else:
                now = datetime.now()
                nowdir = now.strftime('%Y%m%d')
                downpath = os.path.join(downloadpath, nowdir, filehash, filename)
                if (not os.path.exists(downpath)):
                    if (not os.path.exists(os.path.join(downloadpath, nowdir, filehash))):
                        os.makedirs(os.path.join(downloadpath, nowdir, filehash))

                    beforetime = now - timedelta(days=1)
                    beforetimedir = beforetime.strftime('%Y%m%d')
                    beforetimedownpath = os.path.join(downloadpath, beforetimedir, filehash, filename)
                    if (os.path.exists(beforetimedownpath)):
                        shutil.move(beforetimedownpath, downpath)
                    else:
                        tempfile = '%s%s' % (filename, '.tmp')
                        temppath = os.path.join(downloadpath, nowdir, filehash, tempfile)
                        if (not os.path.exists(temppath)):
                            encrpath = os.path.join(userdatapath, savename)
                            decryhash = crypto_helper.get_key(password, user.id)
                            crypto_helper.decrypt_file(bytes.fromhex(decryhash), encrpath, temppath)
                            shutil.move(temppath, downpath)

                downurl = '%s/%s/%s/%s' % (downloadurl, nowdir, filehash, filename)
                self.set_filepath(user, filename, filehash, downurl)
                ret = {'result': downurl}
                self.write(json.dumps(ret))









