import hashlib

import ecdsa

SECP256K1 = "secp256k1"
SM2 = "sm2"
ED25519 = "ed25519"


def generatePrivateKey() -> str:
    private_key = ecdsa.util.randrange(ecdsa.SECP256k1.order)
    return "".join('%x' % private_key)


def publicKeyFromPrivate(priv) -> str:
    priv_int = int(priv, 16)
    pub = ecdsa.SigningKey.from_secret_exponent(priv_int, curve=ecdsa.SECP256k1). \
        get_verifying_key().to_string(encoding="compressed")
    return pub.hex()


def sign(msg: bytes, priv: str) -> bytes:
    priv_int = int(priv, 16)
    return ecdsa.SigningKey.from_secret_exponent(priv_int, curve=ecdsa.SECP256k1). \
        sign_deterministic(msg, hashfunc=hashlib.sha256, sigencode=ecdsa.util.sigencode_der)


def verify(msg: bytes, sig: bytes, pub: str) -> bool:
    pubhex = bytes.fromhex(pub)
    return ecdsa.VerifyingKey.from_string(pubhex, curve=ecdsa.SECP256k1). \
        verify(sig, msg, hashfunc=hashlib.sha256, sigdecode=ecdsa.util.sigdecode_der)


def ecdh(pub: str, priv: str) -> bytes:
    pubhex = bytes.fromhex(pub)
    pubkey = ecdsa.VerifyingKey.from_string(pubhex, curve=ecdsa.SECP256k1).pubkey
    dhpoint = pubkey.point * int(priv, 16)
    dh = ecdsa.VerifyingKey.from_public_point(dhpoint, curve=ecdsa.SECP256k1).to_string(encoding="compressed")
    return dh


def ecdh_point(pub: ecdsa.ellipticcurve.Point, priv: int) -> bytes:
    dhpoint = pub * priv
    dh = ecdsa.VerifyingKey.from_public_point(dhpoint, curve=ecdsa.SECP256k1).to_string(encoding="compressed")
    return dh
