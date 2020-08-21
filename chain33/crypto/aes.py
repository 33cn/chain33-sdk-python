from binascii import b2a_hex, a2b_hex

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

AESPrivateKeyLength = 16
AESBlockSize = 16


def padding(text):
    if len(text) % AESBlockSize:
        add = AESBlockSize - (len(text) % AESBlockSize)
    else:
        add = 0
    pad = add.to_bytes(length=1, byteorder='big', signed=True)
    text = text + (pad * add)
    return text


def unpadding(text):
    srclen = len(text)
    pad = text[srclen - 1]
    return text[:(srclen - pad)]


def genetateAESKey():
    return get_random_bytes(AESPrivateKeyLength)


def encrypt(data, key):
    iv = get_random_bytes(AESBlockSize)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    text = padding(data)
    ciphertext = cipher.encrypt(text)

    return b2a_hex(iv + ciphertext)


def decrypt(data, key):
    data = a2b_hex(data)
    iv = data[:AESBlockSize]
    src = data[AESBlockSize:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain_text = cipher.decrypt(src)

    return unpadding(plain_text)
