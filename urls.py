# -*- coding: UTF-8 -*-

from controller import index
from controller import login
from controller import logout
from controller import wxlogin
from controller import filelist
from controller import filedepth
from controller import fileadd
from controller import filehash
from controller import upload_nginx
from controller import uploadfile
from controller import fileview
from controller import filedown
from controller import sendmail
from controller import sendsms
from controller import codecheck

from controller.pay.alipay import alipayback
from controller.pay.alipay import alipaynotify
from controller.pay.alipay import alipaybackdeep
from controller.pay.alipay import alipaynotifydeep

from controller import admin

url = [
    (r'/', index.IndexHandler),
    (r'/login', login.LoginHandler),
    (r'/wxlogin', wxlogin.WXLoginHandler),
    (r'/logout', logout.LogoutHandler),
    (r'/filedepth', filedepth.FileDepthHandler),
    (r'/filelist', filelist.FileListHandler),
    (r'/fileadd', fileadd.FileAddHandler),
    (r'/filehash', filehash.FileHashHandler),
    (r'/upload', upload_nginx.Upload_Nginx_Handler),
    (r'/uploadfile', uploadfile.UploadFileHandler),
    (r'/view', fileview.FileViewHandler),
    (r'/down', filedown.FileDownHandler),
    (r'/mail', sendmail.SendMailHandler),
    (r'/sms', sendsms.SendSMSHandler),
    (r'/codecheck', codecheck.CodeCheckHandler),
    (r'/alipayback/(.*)', alipayback.AlipayBackHandler),
    (r'/alipaynotify/(.*)/(.*)/(.*)', alipaynotify.AlipayNotifyHandler),
    (r'/alipaybackdeep/(.*)/(.*)/(.*)', alipaybackdeep.AlipayBackDeepHandler),
    (r'/alipaynotifydeep/(.*)/(.*)/(.*)', alipaynotifydeep.AlipayNotifyDeepHandler),
    (r'/admin', admin.AdminHandler)
]
