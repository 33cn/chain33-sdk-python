from crypto import signer, address
from crypto.ed25519 import ed25519Signer
from crypto.gm import sm2, sm4, sm3
import account

def trans(s):
    return "".join('%.2x' % x for x in s)

if __name__ == '__main__':
    data = bytes([0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef, 0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10])
    key = bytes([0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef, 0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10])

    sm2Util = sm2.SM2Util()
    priv, pub = sm2Util.genetateKey()

    cipher = sm2Util.encrypt(data, pub)

    text = sm2Util.decrypt(cipher, priv)

    assert data == text

    signature = sm2Util.sign(data, priv, "0")
    res = sm2Util.verify(data, pub, signature, "0")
    assert res == True

    sm3Util = sm3.SM3Util()
    res = sm3Util.hash(b"abc")

    sm4Util = sm4.SM4Util()
    cipher = sm4Util.encryptECB(key, data)

    print(signer.generatePrivateKey())

    key = "0x85bf7aa29436bb186cac45ecd8ea9e63e56c5817e127ebb5e99cd5a9cbfe0f23"
    data = b"sign test"
    sig = signer.sign(data, key)
    print(sig.hex())

    pub = signer.publicKeyFromPrivate(key)
    print(address.pubKeyToAddr(pub))
    print(signer.verify(data, sig, pub))

    accountA = account.newAccount(signer.SECP256K1)
    print(accountA.privateKey)
    print(accountA.publicKey)
    print(accountA.address)

    accountB = account.newAccount(signer.SM2)
    print(accountB.privateKey)
    print(accountB.publicKey)

    print(accountB.publicKey)
    print(accountB.address)

    accountC = account.newAccount(signer.ED25519)
    print(accountC.privateKey)
    print(accountC.publicKey)
    print(accountC.address)

    sig = ed25519Signer.sign(data, "97ac0e086e363315a8f30633b6d740b763533ed0439d9c696cd147b9a24437190221cf1192e7c3de734893d112ff7696e4d35bf265736e08ac708110d0b7ae97")
    ret = ed25519Signer.verify(data, sig, "0221cf1192e7c3de734893d112ff7696e4d35bf265736e08ac708110d0b7ae97")
    assert ret == True