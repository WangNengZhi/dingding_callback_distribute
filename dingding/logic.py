# -*- coding:utf-8 -*-

import io
import time
import json
import struct
import base64
import string
import hashlib
import binascii

import requests

from common import keys
from random import choice

from Crypto.Cipher import AES


def get_token():
    url = 'https://oapi.dingtalk.com/gettoken?appkey=%s&appsecret=%s' % (keys.APP_KEY, keys.APP_SECRET)
    res = requests.get(url)
    if res.status_code == 200:
        str_res = res.text
        token = (json.loads(str_res)).get('access_token')
        return token


class DingTalkCrypto():
    def __init__(self, encodingAesKey, key):
        self.encodingAesKey = encodingAesKey
        self.key = key
        self.aesKey = base64.b64decode(self.encodingAesKey + '=')

    def encrypt(self, content):
        """加密"""
        msg_len = self.length(content)
        content = self.generateRandomKey(16) + msg_len.decode() + content + self.key
        contentEncode = self.pks7encode(content)
        iv = self.aesKey[:16]
        aesEncode = AES.new(self.aesKey, AES.MODE_CBC, iv)
        aesEncrypt = aesEncode.encrypt(contentEncode)
        return base64.b64encode(aesEncrypt).decode().replace('\n', '')

    def length(self, content):
        """将msg_len转为符合要求的四位字节长度"""
        l = len(content)
        return struct.pack('>l', l)

    def pks7encode(self, content):
        """安装PKCS#7标准填充字符串"""
        l = len(content)
        output = io.StringIO()
        val = 32 - (l % 32)
        for _ in range(val):
            output.write('%02x' % val)
        return bytes(content, 'utf-8') + binascii.unhexlify(output.getvalue())

    def pks7decode(self, content):
        nl = len(content)
        val = int(binascii.hexlify(content[-1].encode()), 16)
        if val > 32:
            raise ValueError('Input is not padded or padding is corrupt')
        l = nl - val
        return content[:l]

    def decrypt(self, content):
        """解密数据"""
        # 钉钉返回的消息体
        content = base64.b64decode(content)
        iv = self.aesKey[:16]  # 初始向量
        aesDecode = AES.new(self.aesKey, AES.MODE_CBC, iv)
        decodeRes = aesDecode.decrypt(content)[20:].decode().replace(self.key, '')
        return self.pks7decode(decodeRes)

    def generateRandomKey(self, size,
                          chars=string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase + string.digits):
        """生成加密所需要的随机字符串"""
        return ''.join(choice(chars) for i in range(size))

    def generateSignature(self, nonce, timestamp, token, msg_encrypt):
        """生成签名"""
        signList = ''.join(sorted([nonce, timestamp, token, msg_encrypt])).encode()
        return hashlib.sha1(signList).hexdigest()


def result_success(encode_aes_key, token, corp_id):
    """封装success返回值"""
    dtc = DingTalkCrypto(encode_aes_key,corp_id)
    encrypt = dtc.encrypt('success')
    timestamp = str(int(round(time.time())))
    nonce = dtc.generateRandomKey(8)
    # 生成签名
    signature = dtc.generateSignature(nonce, timestamp, token, encrypt)
    # 构造返回数据
    new_data = {
        'msg_signature': signature,
        'timeStamp': timestamp,
        'nonce': nonce,
        'encrypt': encrypt
    }
    return new_data


def encrypt_result(encode_aes_key, din_corpid, encrypt):
    """解密钉钉回调的返回值"""
    dtc = DingTalkCrypto(encode_aes_key, din_corpid)
    return dtc.decrypt(encrypt)

