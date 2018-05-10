# -*- coding: UTF-8 -*-

import os, struct
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Hash import SHA224

def get_key(password, salt=None, salt1=None, salt2=None, is256=True):
    #return bytes.fromhex(SHA256.new(password.encode("utf8")).hexdigest())
    if(is256):
        h = SHA256.new()
    else:
        h = SHA224.new()
    h.update(password.encode("utf8"))
    if(salt):
        h.update(salt.encode("utf8"))
    if (salt1):
        h.update(salt1.encode("utf8"))
    if (salt2):
        h.update(salt2.encode("utf8"))
    return h.hexdigest()

def get_bytekey(password, salt=None, salt1=None, salt2=None):
    return bytes.fromhex(get_key(password, salt, salt1, salt2))

def aes_encrypt(text,encryptkey):
    if(not text):return None
    key = pad(encryptkey)
    aes = AES.new(key, AES.MODE_ECB)
    btext = bytes(text, encoding='utf-8')
    encrypted_text = aes.encrypt(pad(btext)).hex()
    return str(encrypted_text)

def aes_decrypt(text,encryptkey):
    if (not text): return None
    key = pad(encryptkey)
    aes = AES.new(key, AES.MODE_ECB)
    btext = bytes.fromhex(text)
    return str(aes.decrypt(btext), encoding='utf-8', errors="ignore").strip()

def pad(text):
    while len(text) % 32 != 0:
        text += b' '
    return text

def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))


def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))
            outfile.truncate(origsize)

# example
# key=get_bytekey('my password')
# print(key,len(key))
# key=key[0:32]
# print(key,len(key))
# encontent = aes_encrypt('my password',key)
# decontent = aes_decrypt(encontent,key)
# print(encontent,decontent)
# encrypt_file(key,'/home/haven/hyd.zip','/home/haven/hyd.zip.en')
# decrypt_file(key,'/home/haven/hyd.zip.en','/home/haven/hyd1.zip')