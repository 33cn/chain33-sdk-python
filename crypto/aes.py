from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from binascii import b2a_hex, a2b_hex

AESPrivateKeyLength = 16
AESBlockSize = 16
AESDefaultIV = b'qqqqqqqqqqqqqqqq'

def padding(text):
    if len(text) % AESBlockSize:
        add = AESBlockSize - (len(text) % AESBlockSize)
    else:
        add = 0
    text = text + (b'0' * add)
    return text

def genetateAESKey():
    return get_random_bytes(AESPrivateKeyLength)

def encrypt(data, key):
    cipher = AES.new(key, AES.MODE_CBC, AESDefaultIV)

    text = padding(data)
    ciphertext = cipher.encrypt(text)
    return b2a_hex(ciphertext)

def decrypt(data, key):
    cipher = AES.new(key, AES.MODE_CBC, AESDefaultIV)
    plain_text = cipher.decrypt(a2b_hex(data))
    return bytes.decode(plain_text).rstrip('0').encode()
