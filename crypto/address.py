import hashlib

version = "00"
addressChecksumLen = 4
Base58Alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

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

    version_payload = bytes.fromhex(version)+ripemd160.digest()

    checkSum = checksum(version_payload)
    full_payload = version_payload + checkSum

    address = base58encode(full_payload.hex())
    return address
