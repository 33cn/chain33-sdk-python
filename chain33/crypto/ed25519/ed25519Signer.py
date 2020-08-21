from ed25519 import (create_keypair, SigningKey, VerifyingKey)


def generatePrivateKey() -> str:
    sk, vk = create_keypair()
    return sk.to_bytes().hex()


def publicKeyFromPrivate(priv: str) -> str:
    skByte = bytes.fromhex(priv)
    return SigningKey(skByte).get_verifying_key().to_bytes().hex()


def sign(msg: bytes, priv: str) -> bytes:
    skByte = bytes.fromhex(priv)
    skSigning = SigningKey(skByte)

    return skSigning.sign(msg)


def verify(msg: bytes, sig: bytes, pub: str) -> bool:
    vkByte = bytes.fromhex(pub)

    VerifyingKey(vkByte).verify(sig=sig, msg=msg)
    return True
