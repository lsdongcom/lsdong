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
from settings import alioss,isuploadfileoss, userdatapath,downloadpath,downloadurl
from utils.file_helper import file_exists,file_read,file_write
from sdk.alipay_pay import Alipay
from utils.oss_helper import Alioss
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
            self.redirect('view?i=%s&t=%s&a=%s&name=%s&m=%s' % (fileindex, filetype, actiontype, actiontype, '参数异常'))
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
        oss = Alioss()
        if (actiontype == '1'):
            filedata.del_file(savename)
            if isuploadfileoss is True:
                encrpath = '%s/%s' % (alioss['userdatapath'], savename)
                oss.Bucket.delete_object(encrpath)
            else:
                encrpath = os.path.join(userdatapath, savename)
                os.unlink(encrpath)
            self.redirect('list?t=%s&m=%s' % (filetype,'删除成功'))
            return
        elif (actiontype == '0'):
            ret = self.getdownurl(user, password, filename, filehash, savename, fileindex, filetype, actiontype, oss)
            self.redirect(ret['url'])



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
            ret['code'] = '1';
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
                    ret['code'] = '1';
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

        oss = Alioss()
        if(passwordhash != keyhash):
            ret = {'result': 'error'}
            ret['code'] = '0';
            ret['info'] = '';
            self.write(json.dumps(ret))
            return
        elif(actiontype == '1'):
            filedata.del_file(savename)
            if isuploadfileoss is True:
                encrpath = '%s/%s' % (alioss['userdatapath'], savename)
                oss.Bucket.delete_object(encrpath)
            else:
                encrpath = os.path.join(userdatapath, savename)
                os.unlink(encrpath)
            ret = {'result': 'delete'}
            self.write(json.dumps(ret))
            return
        elif(actiontype == '0'):
            ret = self.getdownurl(user, password, filename, filehash, savename, fileindex, filetype, actiontype, oss)
            self.write(json.dumps(ret))

    def getdownurl(self, user, password, filename, filehash, savename, fileindex, filetype, actiontype, oss):
        now = datetime.now()
        nowdir = now.strftime('%Y%m%d')
        beforetime = now - timedelta(days=1)
        beforetimedir = beforetime.strftime('%Y%m%d')
        ossencrpath = '%s/%s' % (alioss['userdatapath'], savename)
        localencrpath = os.path.join(userdatapath, savename)
        if isuploadfileoss is True:
            downpath = '%s/%s/%s/%s' % (alioss['downloadpath'], nowdir, filehash, filename)
            beforetimedownpath = '%s/%s/%s/%s' % (alioss['downloadpath'], beforetimedir, filehash, filename)
        else:
            downpath = os.path.join(downloadpath, nowdir, filehash, filename)
            beforetimedownpath = os.path.join(downloadpath, beforetimedir, filehash, filename)

        if file_exists(downpath,oss) is False and file_exists(beforetimedownpath,oss) is False:
            if (os.path.exists(os.path.join(downloadpath, nowdir, filehash)) is False):
                os.makedirs(os.path.join(downloadpath, nowdir, filehash))
            tempfile = '%s%s' % (filename, '.tmp')
            temppath = os.path.join(downloadpath, nowdir, filehash, tempfile)
            if (os.path.exists(temppath) is False):
                decryhash = crypto_helper.get_key(password, user.id)
                if isuploadfileoss is True:
                    oss.Bucket.get_object_to_file(ossencrpath, localencrpath)
                    crypto_helper.decrypt_file(bytes.fromhex(decryhash), localencrpath, temppath)
                    oss.Bucket.put_object_from_file(downpath, temppath)
                    os.unlink(temppath)
                else:
                    crypto_helper.decrypt_file(bytes.fromhex(decryhash), localencrpath, temppath)
                    shutil.move(temppath, downpath)
            else:
                ret = {'result': 'error'}
                ret['code'] = '0';
                ret['url'] = 'view?i=%s&t=%s&a=%s&name=%s&m=%s' % (fileindex, filetype, actiontype, filename, '文件正在解密,请稍候重新获取下载链接');
                ret['info'] = '文件正在解密,请稍候重新获取下载链接';
                return ret
        elif file_exists(beforetimedownpath,oss) is True:
            if isuploadfileoss is True:
                oss.Bucket.copy_object(beforetimedownpath, downpath)
                oss.Bucket.delete_object(beforetimedownpath)
            else:
                if (os.path.exists(os.path.join(downloadpath, nowdir, filehash)) is False):
                    os.makedirs(os.path.join(downloadpath, nowdir, filehash))
                shutil.move(beforetimedownpath, downpath)

        if isuploadfileoss is True:
            downurl = oss.Bucket.sign_url('GET', downpath, 60 * 60 * 8)
        else:
            downurl = '%s/%s/%s/%s' % (downloadurl, nowdir, filehash, filename)
        ret = {'result': 'ok'}
        ret['url'] = downurl;
        ret['info'] = '';
        return ret









