# -*- coding: UTF-8 -*-

import os
import time
import json
import uuid
from datetime import datetime
from safeutils import crypto_helper
from settings import userinfopath
from settings import userdatapath

class userfile():
    _user = None
    _code = None
    _deep_path = None
    _filelist = None
    _userinfofile = None
    _hash = None
    _size = None
    def __init__(self, user, filepath=None, filehash=None):
        self._user = user
        self._size = 0
        if(filepath):
            self._userinfofile = os.path.join(userinfopath, user.usertype, filepath)
            self._hash = bytes(filehash[0:32], encoding='utf-8')
            if not os.path.exists(self._userinfofile):
                data = {}
                data['userid'] = self._user.userid
                data['deep_path'] = ''
                data['filelist'] = ''
                data['size'] = 0
                with  open(self._userinfofile, 'w', encoding='utf-8') as f:
                    jdata = json.dumps(data)
                    jdata = crypto_helper.aes_encrypt(jdata, self._hash)
                    f.write(jdata)

            with open(self._userinfofile, 'r') as f:
                jdata = f.readlines()
                jdata = crypto_helper.aes_decrypt(jdata[0], self._hash)
                data = json.loads(jdata)
                self._code = data['userid']
                self._deep_path = data['deep_path']
                self._filelist = data['filelist']
                self._size = int(data['size'])
        else:
            self._hash = bytes(user.userid, encoding='utf-8')
            self._userinfofile = os.path.join(userinfopath, user.usertype, user.id)
            if(user.isexist):
                with open(self._userinfofile, 'r') as f:
                    jdata = f.readlines()
                    jdata = crypto_helper.aes_decrypt(jdata[0], self._hash)
                    data = json.loads(jdata)
                    self._code = data['userid']
                    self._deep_path = data['deep_path']
                    self._filelist = data['filelist']
                    self._size = int(data['size'])

    @property
    def deep_path(self):
        return self._deep_path

    @property
    def filelist(self):
        if(self._filelist):
            return json.loads(self._filelist)
        else:
            return []

    def save_fileinfo(self):
        data={}
        data['userid'] = self._user.userid
        data['deep_path'] = self._deep_path
        data['filelist'] = self._filelist
        data['size'] = self._size
        with  open(self._userinfofile, 'w', encoding='utf-8') as f:
            jdata = json.dumps(data)
            jdata = crypto_helper.aes_encrypt(jdata,self._hash)
            f.write(jdata)

    def get_deep_path(self, password):
        passhash256 = crypto_helper.get_key(password, self._user.id)
        if (self._deep_path):
            deep_path_list = self._deep_path.split('/t')
            if(deep_path_list[1]==passhash256):
                deep_file = deep_path_list[0]
                return deep_file,passhash256
        return None,None
        
    def create_deep_path(self, password):
        if (not self._deep_path):
            deep_file = '%s%s' %  (uuid.uuid1(),uuid.uuid1())
            deep_file = deep_file.replace('-', '')
            deep_path = os.path.join(userinfopath, self._user.usertype,deep_file)
            while os.path.exists(deep_path):
                deep_file = '%s%s' % (uuid.uuid1(), uuid.uuid1())
                deep_file = deep_file.replace('-', '')
                deep_path = os.path.join(userinfopath, self._user.usertype, deep_file)
            passhash256 = crypto_helper.get_key(password, self._user.id)
            self._deep_path = '%s/t%s' %  (deep_file,passhash256)
            self.save_fileinfo()

            data = {}
            data['userid'] = self._user.userid
            data['deep_path'] = ''
            data['filelist'] = ''
            data['size'] = 0
            with  open(deep_path, 'w', encoding='utf-8') as f:
                jdata = json.dumps(data)
                jdata = crypto_helper.aes_encrypt(jdata, bytes(passhash256[0:32], encoding='utf-8'))
                f.write(jdata)

            return deep_file, passhash256

    def add_file(self, filename, filetype,size, filehash, passwordhash):
        save_name = '%s%s' % (uuid.uuid1(), uuid.uuid1())
        save_name = save_name.replace('-', '')
        file_path = os.path.join(userdatapath, self._user.usertype,save_name)
        while os.path.exists(file_path):
            save_name = '%s%s' % (uuid.uuid1(), uuid.uuid1())
            save_name = save_name.replace('-', '')
            file_path = os.path.join(userdatapath, self._user.usertype, save_name)
        files = []
        if(self._filelist):
            files = json.loads(self._filelist)
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        files.append([filename, filetype,size, filehash, passwordhash, save_name, 0, t])
        self._size = self._size + size
        self._filelist = json.dumps(files)
        self.save_fileinfo()
        return save_name

    def update_file(self, savename, status):
        files = json.loads(self._filelist)
        for fileinfo in files:
            if(fileinfo[5]==savename):
                fileinfo[6]=status
        self._filelist = json.dumps(files)
        self.save_fileinfo()

    def del_file(self, savename):
        files = json.loads(self._filelist)
        l = len(files)
        for i in range(l):
            if (files[i][5] == savename):
                self._size = self._size - int(files[i][2])
                del files[i]
                break;
        self._filelist = json.dumps(files)
        self.save_fileinfo()



