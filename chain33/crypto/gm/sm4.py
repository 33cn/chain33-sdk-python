import random

from gmssl import sm4


class SM4Util(object):

    def __init__(self):
        self.crypt_sm4 = sm4.CryptSM4()

    # 生成SM4对称密钥
    def genetateSM4Key(self):
        return random.getrandbits(16)

    # ECB模式加密
    def encryptECB(self, key, data):
        self.crypt_sm4.set_key(key, sm4.SM4_ENCRYPT)
        return self.crypt_sm4.crypt_ecb(data)

    # ECB模式解密
    def decryptECB(self, key, data):
        self.crypt_sm4.set_key(key, sm4.SM4_DECRYPT)
        return self.crypt_sm4.crypt_ecb(data)

    # CBC模式加密
    def encryptCBC(self, key, iv, data):
        self.crypt_sm4.set_key(key, sm4.SM4_ENCRYPT)
        return self.crypt_sm4.crypt_cbc(iv, data)

    # ECBC模式解密
    def decryptCBC(self, key, iv, data):
        self.crypt_sm4.set_key(key, sm4.SM4_DECRYPT)
        return self.crypt_sm4.crypt_cbc(iv, data)
