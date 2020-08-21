import hashlib

version = "00"
addressChecksumLen = 4
Base58Alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
# MaxExecNameLength 执行器名最大长度
MaxExecNameLength = 100

addrSeed = bytes("address seed bytes for public key", encoding="utf-8")


def normalise_bytes(buffer_object):
    return memoryview(buffer_object).cast('B')


def base58encode(data):
    result = []
    x = int(data, 16)
    base = 58
    zero = 0

    while x != zero:
        x, mod = divmod(x, base)
        result.append(Base58Alphabet[mod])
    result.append(Base58Alphabet[x])
    result.reverse()

    return "".join(result)


def checksum(payload):
    first_sha = hashlib.sha256(normalise_bytes(payload)).digest()
    second_sha = hashlib.sha256(normalise_bytes(first_sha)).digest()

    return second_sha[:addressChecksumLen]


def pubKeyToAddr(pub_key):
    pub_hash = hashlib.sha256(normalise_bytes(bytes.fromhex(pub_key))).digest()

    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(normalise_bytes(pub_hash))

    version_payload = bytes.fromhex(version) + ripemd160.digest()

    checkSum = checksum(version_payload)
    full_payload = version_payload + checkSum

    address = base58encode(full_payload.hex())
    return address


def sha2Sum(b) -> bytes:
    sha256 = hashlib.sha256()
    sha256.update(b)
    first = sha256.digest()
    sha256 = hashlib.sha256()
    sha256.update(first)
    second = sha256.digest()
    return second


def rimpHash(b: bytes) -> bytes:
    hash_256 = hashlib.sha256()
    hash_256.update(b)
    hash_256_value = hash_256.digest()
    obj = hashlib.new('ripemd160', hash_256_value)
    ripemd_160_value = obj.digest()
    return ripemd_160_value


# 获取合约地址
def getExecAddress(name: str) -> str:
    """
    getExecAddress 获取合约地址
    :param name: 合约名称
    :return:
    """
    if len(name) > MaxExecNameLength:
        raise Exception('ExecName too length')
    buf = bytes(name, encoding='utf-8')
    data = addrSeed + buf
    pub = sha2Sum(data)
    rimp = rimpHash(pub)
    ad = bytearray(25)
    ad[0] = 0
    for i in range(0, 20, 1):
        ad[i + 1] = rimp[i]
    sh = sha2Sum(ad[0:21])
    sum = sh[0:4]
    for i in range(0, 4, 1):
        ad[i + 21] = sum[i]
    result = base58encode(ad.hex())
    return result


if __name__ == '__main__':
    result = getExecAddress('ticket')
    print(result)
    assert result == '16htvcBNSEA7fZhAdLJphDwQRQJaHpyHTp'
