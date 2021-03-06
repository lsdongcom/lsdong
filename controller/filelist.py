# -*- coding: UTF-8 -*-


import sys
import tornado
from base import BaseHandler
from datetime import datetime
from urllib import parse
from model.userfile import userfile
from utils.file_helper import getfiletypename,lock_site_notify
import numpy as np
from settings import siteinfo
sys.path.append('..')


class FileListHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        islock, site_notify = lock_site_notify()
        user = self.get_current_user()
        filetype = self.input_default('t')
        filetypename = getfiletypename(int(filetype))
        message = self.input_default('m', None)
        deep_number = self.get_deep_number(user)
        userdata = self.get_user_data(user, deep_number)
        userfilelist = userdata.filelist
        if(len(userfilelist)<=0):
            self.render('filelist.html', username=user.nickname, filetype=filetype, filetypename=filetypename,
                        filelist=[], message=message,site_notify=site_notify, siteinfo=siteinfo)
            return
        data = []
        alist = np.array(userfilelist)
        flist = alist[np.where(alist[:, 1] == str(filetype))]
        for item in flist:
            bsize = int(item[2])
            if (bsize > 1024 * 1024):
                filesize = round(bsize / 1024 / 1024, 1)
                filesize = '%s%s' % (filesize, 'M')
            elif (bsize > 1024):
                filesize = round(bsize / 1024, 1)
                filesize = '%s%s' % (filesize, 'K')
            else:
                filesize = '%s%s' % (bsize, 'B')
            filetime = datetime.strptime(item[7], "%Y-%m-%d %H:%M:%S")
            try:
                filenameurl = parse.quote(item[0])
            except Exception as err:
                print(err)
                filenameurl = item[0]
            finally:
                data.append([item[0], item[1], filesize, item[3], item[4], item[5], item[6], filetime, filenameurl])

        self.render('filelist.html', username=user.nickname, filetype=filetype, filetypename=filetypename,
                    filelist=data, message=message,site_notify=site_notify, siteinfo=siteinfo)

