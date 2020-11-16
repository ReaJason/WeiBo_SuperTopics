import requests
import time

from rsa import PublicKey, encrypt
from binascii import b2a_hex
from math import floor
from random import random
from urllib import parse
from base64 import b64encode
from captcha import predict
"""
level:
        1、正常账号
        2、高危账号
        3、登录频繁账号/登录出错账号
        4、异常账号
        5、登录保护号
        6、密码错误账号
"""


def get_profile(cookie):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, "
                      "like Gecko) Chrome/83.0.4103.116 Mobile Safari/537.36 ",
        "cookie": cookie
    }
    try:
        profile_res = requests.get("https://m.weibo.cn/profile/info", headers=headers)
        content_type = profile_res.headers["Content-Type"]
        if content_type == "application/json; charset=utf-8":
            return True
        else:
            return False
    except Exception as e:
        return False


def security(cookie):
    url = "https://security.weibo.com/account/security?topnav=1&wvr=6"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
        "Cookie": cookie
    }
    try:
        code = requests.get(url=url, headers=headers, allow_redirects=False, timeout=10).status_code
    except:
        return dict(status=0, msg="网络异常，检测失败", level=3)
    if code == 200:
        return dict(status=1, msg="正常账号", level=1)
    else:
        if get_profile(cookie):
            return dict(status=1, msg="高危账号", level=2)
        else:
            return dict(status=1, msg="异常账号", level=4)


class WBCookie(object):
    def __init__(self,sess, username, password, proxy=None):
        self.sess = sess
        self.username = username
        self.password = password
        self.uid = None
        self.nick = None
        self.proxy = {
            "http": proxy,
            "https":proxy
        }
        self.headers = {
            'Referer': 'http://my.sina.com.cn/profile/unlogin',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                          'like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 '
        }

    def get_username(self):
        su = b64encode(parse.quote(self.username).encode('utf8')).decode('utf8')
        return su

    def get_password(self, public_key_json):
        pubkey = public_key_json['pubkey']
        servertime = public_key_json['servertime']
        nonce = public_key_json['nonce']
        public_key = PublicKey(int(pubkey, 16), int('10001', 16))
        password_str = str(servertime) + '\t' + str(nonce) + '\n' + self.password
        password = b2a_hex(encrypt(password_str.encode('utf8'), public_key)).decode('utf8')
        return password

    def pre_login(self, public_key_json, door):
        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        servertime = public_key_json['servertime']
        pcid = public_key_json['pcid']
        nonce = public_key_json['nonce']
        rsakv = public_key_json['rsakv']
        data = {
            'entry': 'account',
            'gateway': '1',
            'from': "",
            'savestate': '0',
            'qrcode_flag': 'true',
            'useticket': '0',
            "pagereer": "",
            'pcid': pcid,
            'door': door,
            'vsnf': '1',
            'su': self.get_username(),
            'service': 'sso',
            "domain": "sina.com.cn",
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            "cdult": "3",
            'rsakv': rsakv,
            'sp': self.get_password(public_key_json=public_key_json),
            'sr': '1920*1080',
            'encoding': 'UTF-8',
            'prelt': '207',
            'returntype': 'TEXT',
        }
        try:
            response = self.sess.post(url=url, headers=self.headers, data=data, proxies=self.proxy).json()
            if response['retcode'] == '2071':  # 您已开启登录保护，请扫码登录
                return self.pac_msg(status=0, level=5, msg='您已开启登录保护，请扫码登录')
            elif response['retcode'] == '101':  # 登录名或密码错误
                return self.pac_msg(status=0, level=6, msg='登录名或密码错误')
            elif response['retcode'] == '2070':  # 验证码错误
                return self.pac_msg(status=0, level=3, msg=response["reason"])
            elif response['retcode'] == '4040':  # 账号登录频繁
                return self.pac_msg(status=0, level=3, msg=response["reason"])
            else:
                try:
                    self.uid = response['uid']
                    self.nick = response['nick']
                except:
                    return self.pac_msg(status=0, level=3, msg=response["reason"])
                cookie1 = ''
                for k, v in self.sess.cookies.items():
                    if k == 'SUB':
                        cookie1 += f"{k}={v}; "
                    if k == '_T_WM':
                        cookie1 += f"{k}={v}; "
                try:
                    response = self.sess.get(url=response["crossDomainUrlList"][0], headers=self.headers,
                                             proxies=self.proxy)
                except:
                    return self.pac_msg(status=1, m_cookie=cookie1, level=3, msg='获取WebCookie失败')
                cookie2 = ''
                for k, v in response.cookies.items():
                    if k == 'SUB':
                        cookie2 += f"{k}={v};"
                security_res = security(cookie1)
                if security_res['status']:
                    return self.pac_msg(
                        status=1, m_cookie=cookie1, web_cookie=cookie2, level=security_res['level'], msg=security_res['msg'])
                else:
                    return self.pac_msg(
                        status=0, m_cookie=cookie1, web_cookie=cookie2, level=security_res['level'], msg=security_res['msg'])
        except:
            return self.pac_msg(status=0, level=3, msg="获取预登录参数失败，请重试")

    def pac_msg(self, status, msg, level, m_cookie=None, web_cookie=None):
        if m_cookie or web_cookie:
            return {
                "status": status,
                "username": self.username,
                "password": self.password,
                "m_cookie": m_cookie,
                'web_cookie': web_cookie,
                "level": level,
                "msg": msg
            }
        else:
            return {
                "status": status,
                "username": self.username,
                "password": self.password,
                "level": level,
                "msg": msg
            }


class ReLogin(object):
    def __init__(self, sess, username, password):
        self.sess = sess
        self.username = username
        self.password = password
        self.headers = {
            'Referer': 'http://my.sina.com.cn/profile/unlogin',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                          'like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 '
        }

    def get_door(self, public_key_json):
        try:
            pcid = public_key_json['pcid']
            url = f'https://login.sina.com.cn/cgi/pin.php?r={floor(random() * 1e8)}&s=0&p={pcid}'
            return url
        except:
            return None

    def get_username(self):
        su = b64encode(parse.quote(self.username).encode('utf8')).decode('utf8')
        return su

    def get_pubkey(self):
        url = 'https://login.sina.com.cn/sso/prelogin.php'
        params = {
            'entry': 'weibo',
            'su': self.get_username(),
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js(v1.4.19)',
            '_': round(time.time() * 1000)
        }
        try:
            self.sess.get(url="https://m.weibo.cn/", headers=self.headers)
            response = self.sess.get(url=url, headers=self.headers, params=params).json()
            return response
        except Exception as e:
            return None

    def run(self):
        public_key_json = self.get_pubkey()
        if public_key_json:
            url = self.get_door(public_key_json)
            if url:
                return {"status": 1,'url': url, 'public_key_json': public_key_json, 'msg': '成功获取验证码'}
            else:
                return {"status": 0,"msg": "获取参数失败"}
        else:
            return {"status": 0,"msg": "获取参数失败"}


def login(username, password):
    session = requests.session()
    captcha = ReLogin(session, username, password).run()
    if not captcha['status']:
        print(captcha['msg'])
        return None
    print(f"验证码地址为：{captcha['url']}")
    door = input("请打开链接输入验证码：").strip()
    # img_content = session.get(url=captcha['url']).content
    # door = predict(base64_img=b64encode(img_content))
    sina = WBCookie(session, username, password).pre_login(captcha['public_key_json'], door)
    print(sina)


if __name__ == '__main__':
    username = "*****"
    password = "*****"
    login(username, password)