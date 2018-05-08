# -*- coding: utf-8 -*-
import re
import numba as nb
from hashids import Hashids
from utils import int_tool
from Crypto.Hash import SHA256
from Crypto.Hash import SHA3_256

@nb.jit()
def split_unionid(unionid):
    hashid = unionid[-9:]
    hashkey = unionid[:-9]
    hashid = int_tool.str62_to_int(hashid)
    return hashid, hashkey

@nb.jit()
def get_hashid(hashid, hashkey,min_length=27):
    hashids = Hashids(salt=hashkey, min_length=min_length)
    hashid = hashids.encode(hashid)
    return hashid

@nb.jit()
def hashid_decode(hashid, hashkey,min_length=27):
    hashids = Hashids(salt=hashkey,min_length=min_length)
    idx = hashids.decode(hashid)[0]
    return idx

@nb.jit()
def clear_unionid(unionid):
     return re.sub('[\W_]', '', unionid)

@nb.jit()
def get_key(password, salt=None, salt1=None, salt2=None, is256=True):
    #return bytes.fromhex(SHA256.new(password.encode("utf8")).hexdigest())
    if(is256):
        h = SHA3_256.new()
    else:
        h = SHA256.new()
    h.update(password.encode("utf8"))
    if(salt):
        h.update(salt.encode("utf8"))
    if (salt1):
        h.update(salt1.encode("utf8"))
    if (salt2):
        h.update(salt2.encode("utf8"))
    return h.hexdigest()




