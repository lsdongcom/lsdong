# -*- coding: UTF-8 -*-

class userinfo():

    def __init__(self, id=None, unionid=None, nickname=None,usertype=None, isexist=False):
        self._id = id
        self._unionid = unionid
        self._nickname = nickname
        self._usertype = usertype
        self._isexist = isexist

    @property
    def id(self):
        return self._id

    @property
    def userid(self):
        return self._unionid

    @property
    def nickname(self):
        return self._nickname

    @property
    def usertype(self):
        return self._usertype

    @property
    def isexist(self):
        return self._isexist

    def get_session(self):
        userinfo_dict = {}
        userinfo_dict['id'] = self._id
        userinfo_dict['unionid'] = self._unionid
        userinfo_dict['nickname'] = self._nickname
        userinfo_dict['usertype'] = self._usertype
        userinfo_dict['isexist'] = self._isexist
        return userinfo_dict

    def get_userinfo_from_session(self, session_user):
        self._id = session_user['id']
        self._unionid = session_user['unionid']
        self._nickname = session_user['nickname']
        self._usertype = session_user['usertype']
        self._isexist = session_user['isexist']

    def set_isexist(self, isexist=False):
        self._isexist = isexist

