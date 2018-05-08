# -*- coding: UTF-8 -*-

import hashlib
import time
import string
import random
import smtplib
import re
from email.header import Header
from email.mime.text import MIMEText

from settings import mail


def encrypt_password(username, password):
    '''
    密码加密,通过 username 和 password 进行加盐, 使得不同用户就算密码相同也不会使加密的密钥撞库
    :param username: 用户名
    :param password: 密码
    :return: 加密后密码
    '''
    salt = 'The-StarCloud-{0}-{1}'.format(username, password)
    key = hashlib.md5('%s%s' % (hashlib.md5(password.encode('utf-8')).hexdigest(), salt)).hexdigest()
    return key


def stamp_to_string(timestamp=time.time(), format="%Y-%m-%d %H:%M:%S"):
    """
    这是时间戳转字符串时间格式的函数
    例如：
        1483332358.0 => "2017-01-02 12:45:58"
    :param timestamp: 需要转换的时间戳,默认为系统当前时间; 类型为float
    :param format: 转换后的字符串时间格式,默认为“%Y-%m-%d %H:%M:%S”
    :return: 返回值为转换后的字符串时间格式,类型：str
    """
    if isinstance(timestamp, float):
        struct_time = time.localtime(timestamp)
    else:
        raise TypeError("must be float, not {0}".format(type(timestamp)))
    string_time = time.strftime(format, struct_time)
    return string_time


def random_string(key_len):
    '''
    生成随机字符串
    :param key_len:随机字符串位数
    :return: random_str随机字符串
    '''
    base_string = string.ascii_letters + string.digits
    keylist = [random.choice(base_string) for i in range(key_len)]
    random_str = "".join(keylist)
    return random_str

def random_number(key_len):
    '''
    生成随机字符串
    :param key_len:随机字符串位数
    :return: random_str随机字符串
    '''
    base_string = string.digits
    keylist = [random.choice(base_string) for i in range(key_len)]
    random_str = "".join(keylist)
    return random_str


def send_email(to_addr, email_content, email_title, from_prefix):
    '''
    简单文本邮件发送函数
    :param to_addr:指定邮件接收方地址,字符串形式
    :param email_content: 发送的信息, 字符串形式
    :param email_title: 邮件标题, 字符串形式
    :param from_prefix: 邮件发件人前缀, 字符串形式
    :return:
        True:发送成功
        False:发送失败,失败原因写入log
    '''
    content = MIMEText(email_content, 'plain', 'utf-8')
    content['From'] = '{0}<{1}>'.format(from_prefix, mail['from_addr'])
    content['To'] = '{0}'.format(to_addr)
    content['Subject'] = Header('{0}'.format(email_title), 'utf-8').encode()

    try:
        server = smtplib.SMTP_SSL(mail['smtp_server'], 465)
        server.login(mail['from_addr'], mail['password'])
        server.sendmail(mail['from_addr'], [to_addr], content.as_string())
        server.quit()
        return True, ''
    except Exception as e:
        # 错误信息e写入log
        print(e)
        return False, e


def delete_html(html_string):
    '''
    去除字符串中的html标签
    :param html_string: 含有html标签的字符串
    :return: 不含html标签的字符串
    '''
    dr = re.compile(r'<[^>]+>', re.S)
    data = dr.sub('', html_string)
    return data