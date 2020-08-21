from chain33.crypto import signer, address
from chain33.crypto.ed25519 import ed25519Signer
from chain33.crypto.gm import sm2


class Account(object):

    def __init__(self, privateKey: str, signType: str):
        self.privateKey = privateKey
        if signType == signer.SECP256K1:
            self.publicKey = signer.publicKeyFromPrivate(privateKey)
        elif signType == signer.SM2:
            sm2Util = sm2.SM2Util()
            self.publicKey = sm2Util.pubKeyFromPrivate(privateKey)
        elif signType == signer.ED25519:
            self.publicKey = ed25519Signer.publicKeyFromPrivate(privateKey)
        else:
            raise ValueError(
                "Error: signType is not correct."
            )
        self.address = address.pubKeyToAddr(self.publicKey)
        self.signType = signType

    def Address(self) -> str:
        return self.address

    def SignType(self) -> str:
        return self.signType

    def PrivateKey(self) -> str:
        return self.privateKey

    def PublicKey(self) -> str:
        return self.publicKey


# 生成随机账户
def newAccount(signType=signer.SECP256K1):
    if signType == signer.SECP256K1:
        privateKey = signer.generatePrivateKey()
        return Account(privateKey, signType)
    elif signType == signer.SM2:
        sm2Util = sm2.SM2Util()
        privateKey, _ = sm2Util.genetateKey()
        return Account(privateKey, signType)
    elif signType == signer.ED25519:
        privateKey = ed25519Signer.generatePrivateKey()
        return Account(privateKey, signType)
    else:
        raise ValueError(
            "Error: signType is not correct."
        )
