import account
import pre
from crypto import signer, aes
from rpc.jsonclient import jsonclient

if __name__ == '__main__':
    serverPub = "02005d3a38feaff00f1b83014b2602d7b5b39506ddee7919dd66539b5428358f08"
    msg = b"hello proxy-re-encrypt"
    serverList = ["http://192.168.0.155:11801", "http://192.168.0.155:11802", "http://192.168.0.155:11803"]

    alice = account.newAccount()
    bob = account.newAccount()

    enKey, pubr, pubu = pre.generateEncryptKey(alice.publicKey)
    cipher = aes.encrypt(msg, enKey)

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

    plain = aes.decrypt(cipher, aesKey)
    print(plain)

    # priv = "841e3b4ab211eecfccb475940171150fd1536cb656c870fe95d206ebf9732b6c"
    # pub = "03b9d801f88c38522a9bf786f23544259d516ee0d1f6699f926f891ac3fb92c6d9"
    # pubOwner = "02e5fdf78aded517e3235c2276ed0e020226c55835dea7b8306f2e8d3d99d2d4f4"
    # rekeys = list()
    # for i in range(2):
    #     jclient = jsonclient(serverList[i])
    #     rekey = jclient.Reencrypt(pubOwner, pub)
    #     rekeys.append(rekey)
    #
    # aesKey = pre.assembleReencryptFragment(priv, rekeys)
    #
    # cipher = b'84e1837bdaaf334a1cb53a68584682e0d245f3c97266f4db0e52b603a2c1ce3dd3ab86518c14c7be612fc0af5edac2b5'
    # plain = aes.decrypt(cipher, aesKey)
    # print(plain)