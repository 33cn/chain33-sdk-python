import account
import pre
from crypto import signer, aes
from rpc.jsonclient import jsonclient

if __name__ == '__main__':
    key = "0x85bf7aa29436bb186cac45ecd8ea9e63e56c5817e127ebb5e99cd5a9cbfe0f23"
    serverPub = "02005d3a38feaff00f1b83014b2602d7b5b39506ddee7919dd66539b5428358f08"
    msg = b"hello proxy-re-encrypt"
    serverList = ["http://192.168.0.155:11801", "http://192.168.0.155:11802", "http://192.168.0.155:11803"]

    alice = account.newAccount()
    bob = account.newAccount()

    enKey, pubr, pubu = pre.generateEncryptKey(alice.publicKey)
    cipher = aes.encrypt(msg, enKey)
    print(enKey.hex())

    keyFragments = pre.generateKeyFragment(alice.privateKey, bob.publicKey, 3, 2)

    dhproof = signer.ecdh(serverPub, alice.privateKey)

    rekeys = list()
    for i in range(len(keyFragments)):
        jclient = jsonclient(serverList[i])
        result = jclient.SendKeyFragment(alice.publicKey, bob.publicKey, pubr, pubu, keyFragments[i].random, keyFragments[i].value,
                                100000, dhproof.hex(), keyFragments[i].precurpub)
        rekey = jclient.Reencrypt(alice.publicKey, bob.publicKey)
        rekeys.append(rekey)

    aesKey = pre.assembleReencryptFragment(bob.privateKey, rekeys)
    print(aesKey.hex())

    plain = aes.decrypt(cipher, aesKey)
    print(plain)
