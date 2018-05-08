# -*- coding: UTF-8 -*-

import os

import tornado.ioloop
import tornado.web
from tornado.options import define, options
import logging

from urls import url
from settings import setting

# logging.basicConfig(level=logging.DEBUG,
# 					filemode='a+',
# 					filename='{0}/starcloud.log'.format(os.path.join(setting['root_path'],'log')),
# 					format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
# 					datefmt='%a, %d %b %Y %H:%M:%S',
# 					)

application = tornado.web.Application(handlers = url, **setting)

define("port", default=8000, type=int, help="the listen port")


def main():
	options.parse_command_line()
	logging.info('The template path:{0}'.format(setting['template_path']))
	logging.info('The static path:{0}'.format(setting['static_path']))
	print("the lsdong run in the port:{0}".format(options.port))
	print("you can stop the programming by 'ctrl+c'")
	application.listen(options.port)
	tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
	main()
