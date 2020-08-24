import binascii
import hashlib
from math import ceil
from typing import List

import ecdsa
from ecdsa import ellipticcurve, numbertheory
from ecdsa.util import bit_length

from chain33.crypto import signer

baseN = ecdsa.SECP256k1.order
encKeyLength = 16


class KFrag:
    def __init__(self, random, value, precurpub):
        self.random = random
        self.value = value
        self.precurpub = precurpub


class ReKeyFrag:
    def __init__(self, reKeyR, reKeyU, random, precurpub):
        self.reKeyR = reKeyR
        self.reKeyU = reKeyU
        self.random = random
        self.precurpub = precurpub


class EccPoint():
    def __init__(self, point: ellipticcurve.Point = None):
        self.point = point

    def setEccPoint(self, pub: str):
        pubByte = bytes.fromhex(pub)
        point = ecdsa.VerifyingKey.from_string(pubByte, ecdsa.SECP256k1, hashlib.sha256).pubkey.point
        self.point = point

    def __add__(self, other):
        if other.point == None:
            return EccPoint(self.point)
        return EccPoint(self.point + other.point)

    def __mul__(self, other: int):
        return EccPoint(self.point * other)


def kdf(z, klen):  # z为16进制表示的比特串（str），klen为密钥长度（单位byte）
    klen = int(klen)
    ct = 0x00000001
    rcnt = ceil(klen / 32)
    zin = [i for i in bytes.fromhex(z)]
    ha = b""
    for i in range(rcnt):
        msg = zin + [i for i in binascii.a2b_hex(('%08x' % ct).encode('utf8'))]
        ha = ha + hashlib.sha256(bytes(msg)).digest()
        ct += 1
    return ha[0: klen]


def generateEncryptKey(pubOwner):
    pubOwnerKey = ecdsa.VerifyingKey.from_string(bytes.fromhex(pubOwner), ecdsa.SECP256k1, hashlib.sha256)

    priv_r = ecdsa.SigningKey.from_secret_exponent(int(signer.generatePrivateKey(), 16), ecdsa.SECP256k1,
                                                   hashlib.sha256)
    priv_u = ecdsa.SigningKey.from_secret_exponent(int(signer.generatePrivateKey(), 16), ecdsa.SECP256k1,
                                                   hashlib.sha256)

    sum = (priv_r.privkey.secret_multiplier + priv_u.privkey.secret_multiplier) % baseN
    result = pubOwnerKey.pubkey.point * sum

    encKey = ecdsa.VerifyingKey.from_public_point(result, ecdsa.SECP256k1, hashlib.sha256).to_string(
        encoding="compressed")
    return kdf(encKey.hex(), encKeyLength), priv_r.get_verifying_key().to_string(
        encoding="compressed").hex(), priv_u.get_verifying_key().to_string(encoding="compressed").hex()


def hashToModInt(digest):
    orderBits = bit_length(baseN)
    orderBytes = int((orderBits + 7) / 8)
    if len(digest) > orderBytes:
        digest = digest[:orderBytes]

    ret = int(digest.hex(), 16)
    excess = len(digest) * 8 - orderBits
    if excess > 0:
        return ret >> excess
    return ret


# def hashToModInt(digest):
#     sum = int(digest, 16)
#     order_minus_1 = baseN - 1
#
#     return (sum % order_minus_1) + 1

def makeShamirPolyCoeff(threshold) -> List[int]:
    coeffs = list()
    for _ in range(threshold - 1):
        key = int(signer.generatePrivateKey(), 16)
        coeffs.append(key)
    return coeffs


def hornerPolyEval(coeff: List[int], x: int) -> int:
    result = coeff[0]
    for i in range(1, len(coeff)):
        result = (result * x) + coeff[i]
    return result % baseN


def calcPart(a: int, b: int) -> int:
    p = (a - b) % baseN
    res = (a * numbertheory.inverse_mod(p, baseN)) % baseN
    return res


def calcLambdaCoeff(id_i: int, selected_ids: List[int]) -> int:
    ids = [x for x in selected_ids if x != id_i]

    if not ids:
        return 1

    result = calcPart(ids[0], id_i)
    for id_j in ids[1:]:
        result = (result * calcPart(id_j, id_i)) % baseN

    return result


def generateKeyFragment(privOwner, pubRecipient, numSplit, threshold) -> List[KFrag]:
    precursorKey = int(signer.generatePrivateKey(), 16)
    precursor = ecdsa.SigningKey.from_secret_exponent(precursorKey, ecdsa.SECP256k1, hashlib.sha256)

    privInt = int(privOwner, 16)
    pubRecipientKey = ecdsa.VerifyingKey.from_string(bytes.fromhex(pubRecipient), ecdsa.SECP256k1, hashlib.sha256)

    dh_alice_point = signer.ecdh_point(pubRecipientKey.pubkey.point, precursorKey)
    aAliceHash = hashlib.sha256()
    aAliceHash.update(precursor.get_verifying_key().pubkey.point.x().to_bytes(32, byteorder='big', signed=False))
    aAliceHash.update(pubRecipientKey.pubkey.point.x().to_bytes(32, byteorder='big', signed=False))
    aAliceHash.update(dh_alice_point)
    dAlice = aAliceHash.digest()
    dAliceBN = hashToModInt(dAlice)

    f0 = (privInt * numbertheory.inverse_mod(dAliceBN, baseN)) % baseN

    precursorPub = precursor.get_verifying_key().to_string(encoding="compressed").hex()
    kfrags = list()
    if numSplit == 1:
        id = ecdsa.util.randrange(ecdsa.SECP256k1.order)
        kfrag = KFrag(str(id), str(f0), precursorPub)
        kfrags.append(kfrag)
    else:
        coeffs = makeShamirPolyCoeff(threshold)
        coeffs.append(f0)

        for _ in range(numSplit):
            id = ecdsa.util.randrange(baseN)
            dShareHash = hashlib.sha256()
            dShareHash.update(
                precursor.get_verifying_key().pubkey.point.x().to_bytes(32, byteorder='big', signed=False))
            dShareHash.update(pubRecipientKey.pubkey.point.x().to_bytes(32, byteorder='big', signed=False))
            dShareHash.update(dh_alice_point)
            dShareHash.update(id.to_bytes(32, byteorder='big', signed=False))

            share = hashToModInt(dShareHash.digest())
            rk = hornerPolyEval(coeffs, share)
            kfrag = KFrag(str(id), str(rk), precursorPub)
            kfrags.append(kfrag)

    return kfrags


def assembleReencryptFragment(privRecipient: str, reKeyFrags: List[ReKeyFrag]) -> bytes:
    privRecipientInt = int(privRecipient, 16)
    privRecipientKey = ecdsa.SigningKey.from_secret_exponent(privRecipientInt, ecdsa.SECP256k1, hashlib.sha256)

    precursor = bytes.fromhex(reKeyFrags[0].precurpub)
    precursorPub = ecdsa.VerifyingKey.from_string(precursor, curve=ecdsa.SECP256k1)

    dh_Bob_poit = signer.ecdh_point(precursorPub.pubkey.point, privRecipientInt)
    dBobHash = hashlib.sha256()
    dBobHash.update(precursorPub.pubkey.point.x().to_bytes(32, byteorder='big', signed=False))
    dBobHash.update(privRecipientKey.get_verifying_key().pubkey.point.x().to_bytes(32, byteorder='big', signed=False))
    dBobHash.update(dh_Bob_poit)
    dBob = dBobHash.digest()
    dBobBN = hashToModInt(dBob)

    if len(reKeyFrags) == 1:
        rPoint = EccPoint()
        rPoint.setEccPoint(reKeyFrags[0].reKeyR)
        uPoint = EccPoint()
        uPoint.setEccPoint(reKeyFrags[0].reKeyU)

        share_key = (rPoint + uPoint) * dBobBN
    else:
        eFinal = EccPoint()
        vFinal = EccPoint()
        ids = list()
        for i in range(len(reKeyFrags)):
            xs = hashlib.sha256()
            xs.update(precursorPub.pubkey.point.x().to_bytes(32, byteorder='big', signed=False))
            xs.update(privRecipientKey.get_verifying_key().pubkey.point.x().to_bytes(32, byteorder='big', signed=False))
            xs.update(dh_Bob_poit)
            xs.update(int(reKeyFrags[i].random).to_bytes(32, byteorder='big', signed=False))
            share = hashToModInt(xs.digest())
            ids.append(share)

        for i in range(len(ids)):
            coeff = calcLambdaCoeff(ids[i], ids)
            rPoint = EccPoint()
            rPoint.setEccPoint(reKeyFrags[i].reKeyR)
            uPoint = EccPoint()
            uPoint.setEccPoint(reKeyFrags[i].reKeyU)

            e = rPoint * coeff
            v = uPoint * coeff

            eFinal = e + eFinal
            vFinal = v + vFinal

        share_key = (eFinal + vFinal) * dBobBN

    eckey = ecdsa.VerifyingKey.from_public_point(share_key.point, ecdsa.SECP256k1, hashlib.sha256). \
        to_string(encoding="compressed")
    return kdf(eckey.hex(), encKeyLength)
