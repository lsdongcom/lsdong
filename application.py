# -*- coding: UTF-8 -*-

import os
import shutil
import tornado.ioloop
import tornado.web
from tornado.options import define, options
import logging

from urls import url
from settings import setting,isuploadfileoss

# logging.basicConfig(level=logging.DEBUG,
# 					filemode='a+',
# 					filename='{0}/lsdong.log'.format(os.path.join(setting['root_path'],'log')),
# 					format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
# 					datefmt='%a, %d %b %Y %H:%M:%S',
# 					)

application = tornado.web.Application(handlers = url, **setting)

define("port", default=8000, type=int, help="the listen port")


def main():
	updatetemplate()
	options.parse_command_line()
	logging.info('The template path:{0}'.format(setting['template_path']))
	logging.info('The static path:{0}'.format(setting['static_path']))
	print("the lsdong run in the port:{0}".format(options.port))
	print("you can stop the programming by 'ctrl+c'")
	application.listen(options.port)
	tornado.ioloop.IOLoop.current().start()

#根据文件上传类型动态切换模板
def updatetemplate():
	basefile = os.path.join(setting['template_path'], 'base_admin_form_uploadfile.html')
	if(os.path.exists(basefile) is True):
		os.unlink(basefile)
	if(isuploadfileoss is True):
		shutil.copy(os.path.join(setting['template_path'], 'uploadfile_base', 'base_admin_form_uploadfile_oss.html'),basefile)
	else:
		shutil.copy(os.path.join(setting['template_path'], 'uploadfile_base', 'base_admin_form_uploadfile.html'),basefile)

if __name__ == "__main__":
	main()
