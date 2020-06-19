#!/usr/bin/python3

import json
import requests
import pre
from protobuf import transaction
from protobuf import tx_pb2
import account
from crypto import signer
import copy
import time

class jsonclient:

    def __init__(self,url):
        self.url=url
        self.headers = {'content-type':'application/json'}

    def Call(self,method,params)->json:
        payload = {
            "method": method,
            "params": [params],
            "jsonrpc": "2.0",
            "id": 1
        }
        response = requests.post(
            self.url,
            data=json.dumps(payload),
            headers=self.headers
        ).json()
        return response

    def SendTransaction(self,hextx):
        return self.Call("Chain33.SendTransaction", {"data": hextx})

    def QueryTransaction(self,txhash):
        return self.Call("Chain33.QueryTransaction",{"hash":txhash})

    def CreateRawTransaction(self,to,amount,fee,note,isToken,isWithdraw,tokenSymbol,execName,execer):
        return self.Call("Chain33.CreateRawTransaction",{"to":to,"amount":amount,"fee":fee,"note":note,"isToken":isToken,"isWithdraw":isWithdraw,"tokenSymbol":tokenSymbol,"execName":execName,"execer":execer})

    def SendKeyFragment(self, pubOwner: str, pubRecipient: str, pubProofR: str, pubProofU: str,
                        random: str, value: str, expire: int, dhProof: str, precurPub: str) -> bool:
        requestParam = {}
        requestParam["pubOwner"] = pubOwner
        requestParam["pubRecipient"] = pubRecipient
        requestParam["pubProofR"] = pubProofR
        requestParam["pubProofU"] = pubProofU
        requestParam["random"] = random
        requestParam["value"] = value
        requestParam["expire"] = expire
        requestParam["dhProof"] = dhProof
        requestParam["precurPub"] = precurPub

        resp = self.Call("Pre.CollectFragment", requestParam)
        return resp["result"]["result"]

    def Reencrypt(self, pubOwner: str, pubRecipient: str)->pre.ReKeyFrag:
        requestParam = {}
        requestParam["pubOwner"] = pubOwner
        requestParam["pubRecipient"] = pubRecipient
        resp = self.Call("Pre.Reencrypt", requestParam)
        result = resp["result"]
        return pre.ReKeyFrag(result["reKeyR"], result["reKeyU"], result["random"], result["precurPub"])

if __name__ == '__main__':
   url = "http://192.168.0.155:8801"
   print('=========this is a test===========')
   client =jsonclient(url)
   # print(client.Call("Chain33.GetPeerInfo",None))
   # 查询指定高得区块信息
  # print(client.Call("Chain33.GetBlocks",{"start":100,"end":100,"isDetail":False}))

   # 构造转账交易，并发送
   response = client.CreateRawTransaction("19MJmA7GcE1NfMwdGqgLJioBjVbzQnVYvR",10000000,100000,"THIS IS A TEST!",False,False,"","","coins")
   if  response["error"] == None:
      rawTx=response["result"]
      print(rawTx)
      #去掉ox
      hexTx= rawTx[2:]
      data=bytes.fromhex(hexTx)
      tx = tx_pb2.Transaction()
      tx.ParseFromString(data)
      print(tx)
      copytx = copy.deepcopy(tx)
      acc = account.Account
      acc.signType=signer.SECP256K1
     # 14KEKbYtKKQm4wMthSK9J4La4nAiidGozt
      acc.privateKey  = "cc38546e9e659d15e6b4893f0ab32a06d103931a8230b0bde71459d2b27d6944"
      acc.publicKey = signer.publicKeyFromPrivate("cc38546e9e659d15e6b4893f0ab32a06d103931a8230b0bde71459d2b27d6944")


      signTx = transaction.Sign(tx,acc)
      hexTx = bytes.hex(signTx.SerializeToString())
      print(hexTx)
      response = client.SendTransaction(hexTx)
      print(response["error"],response["result"],response["id"])

      # 构建交易组
      tx1 = copy.deepcopy(tx)
      tx1.nonce=tx1.nonce+1
      tx2 = copy.deepcopy(tx)
      tx2.nonce = tx1.nonce + 2
      tx3 = copy.deepcopy(tx)
      tx3.nonce = tx1.nonce + 3
      tx4 = copy.deepcopy(tx)
      tx4.nonce = tx1.nonce + 4
      txs = []
      txs.append(tx1)
      txs.append(tx2)
      txs.append(tx3)
      txs.append(tx4)
      txgroup = transaction.TxGroup(txs, transaction.MinFee)

      txgroup.Sign(acc)
      tx = txgroup.Tx()
      print('fee:',tx.fee)
      hexTx = bytes.hex(tx.SerializeToString())
      print(hexTx)
      response = client.SendTransaction(hexTx)
      print(response)
      txhash = response["result"]
      time.sleep(5)
      response=client.QueryTransaction(txhash)
      print(response)

      # 本地构造交易
      transfer = tx_pb2.AssetsTransfer()
      transfer.amount = 100000
      transfer.note = bytes("this a test", encoding='utf-8')
      transfer.to = '19MJmA7GcE1NfMwdGqgLJioBjVbzQnVYvR'
      action = tx_pb2.CoinsAction(transfer=transfer)
      action.ty = 1
      tx = transaction.createTx(execer=bytes("coins", encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                   to="19MJmA7GcE1NfMwdGqgLJioBjVbzQnVYvR")
      signTx = transaction.Sign(tx,acc)
      hexTx = bytes.hex(signTx.SerializeToString())
      response = client.SendTransaction(hexTx)
      time.sleep(5)
      response=client.QueryTransaction(txhash)
      print(response)