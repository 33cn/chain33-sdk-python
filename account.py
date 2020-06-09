from crypto import signer, address
from crypto.gm import sm2

class Account():

    def __init__(self, privateKey, publicKey, address, signType):
        self.privateKey = privateKey
        self.publicKey = publicKey
        self.address = address
        self.signType = signType

def newAccount(signType=signer.SECP256K1):

    if signType == signer.SECP256K1:
        privateKey = signer.generatePrivateKey()
        publicKey = signer.publicKeyFromPrivate(privateKey)
        addr = address.pubKeyToAddr(publicKey)
        return Account(privateKey, publicKey, addr, signType)
    elif signType == signer.SM2:
        sm2Util = sm2.SM2Util()
        privateKey,_ = sm2Util.genetateKey()
        publicKey = sm2Util.pubKeyFromPrivate(privateKey)
        addr = address.pubKeyToAddr(publicKey)
        return Account(privateKey, publicKey, addr, signType)
    else:
        raise ValueError(
            "Error: signType is not correct."
        )