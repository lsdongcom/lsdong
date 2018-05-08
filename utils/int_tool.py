# -*- coding: UTF-8 -*-
#
# 62进制,特别合于月、日、时、分、秒的压缩进储
#
digit62 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

# 整数转化为62进制字符串
# 入口：
#   x : 整数
# 返回： 字符串
def int_to_str62(x):
    try:
        x = int(x)
    except:
        x = 0
    if x < 0:
        x = -x
    if x == 0:
        return "0"
    s = ""
    while x > 62:
        x1 = x % 62
        s = digit62[x1] + s
        x = x // 62
    if x > 0:
        s = digit62[x] + s
    return s


# 62进制字符串转化为整数
# 入口：
#   s : 62进制字符串
# 返回： 整数
def str62_to_int(s):
    x = 0
    s = str(s).strip()
    if s == "":
        return x
    for y in s:
        k = digit62.find(y)
        if k >= 0:
            x = x * 62 + k
    return x