import copy
import time

from chain33.crypto import account, signer
from chain33.dapp import coins, storage, transaction
from chain33.rpc.jsonclient import client

if __name__ == '__main__':
    url = "http://localhost:8801"
    # 实例化一个jsonclient
    client = client(url)
    print(client.Call("Chain33.GetPeerInfo", None))
    # 本地构造转账交易，并发送
    tx = coins.transfer("", 100000000, "1FNdYStvfKizgCy7DbJ2vAmt9U8Neys3No", "test")

    copytx = copy.deepcopy(tx.Tx())
    # 14KEKbYtKKQm4wMthSK9J4La4nAiidGozt
    # 实例一个账户
    acc = account.Account(privateKey="cc38546e9e659d15e6b4893f0ab32a06d103931a8230b0bde71459d2b27d6944",
                          signType=signer.SECP256K1)
    # 交易签名
    tx.Sign(acc)
    # 发送
    txhash, err = client.SendTransaction(tx.Tx())
    print(txhash, err)

    # 获取主币名称
    symbol, err = client.GetCoinSymbol()
    print('symbol', symbol, err)

    # 查询余额
    a, err = client.QueryBalance('1FNdYStvfKizgCy7DbJ2vAmt9U8Neys3No', "coins", "", "")
    print(a.balance, err)

    # 本地构造交易组
    tx1 = copy.deepcopy(copytx)
    tx1.nonce = tx1.nonce + 1
    tx2 = copy.deepcopy(copytx)
    tx2.nonce = tx1.nonce + 2
    tx3 = copy.deepcopy(copytx)
    tx3.nonce = tx1.nonce + 3
    tx4 = copy.deepcopy(copytx)
    tx4.nonce = tx1.nonce + 4
    txs = []
    txs.append(tx1)
    txs.append(tx2)
    txs.append(tx3)
    txs.append(tx4)
    txgroup = transaction.TxGroup(txs, transaction.MinFee)

    txgroup.Sign(acc)
    tx = txgroup.Tx()
    txhash, err = client.SendTransaction(tx)
    if err != None:
        raise ValueError(
            "Error:" + err
        )
    time.sleep(5)
    result, err = client.QueryTransaction(txhash)
    print(result)

    # 往合约地址打币
    tx = coins.transferToExec("", 200000000, "ticket", "test transferToExec")
    tx.Sign(acc)
    client.SendTransaction(tx.Tx())
    # 等待打包
    time.sleep(3)
    account1, err = client.QueryBalance(acc.address, "ticket", "", "")
    print(account1.balance)

    # 回提coins代币
    tx = coins.withdraw("", 200000000, "ticket", "test withdraw")
    tx.Sign(acc)
    client.SendTransaction(tx.Tx())
    # 等待打包
    time.sleep(3)
    account1, err = client.QueryBalance(acc.address, "ticket", "", "")
    print(account1.balance)

    # 本地构造明文存证交易
    tx = storage.contentStorage("", "", bytes("", encoding='utf-8'), "value1", 0)
    tx.Sign(acc)
    txhash, err = client.SendTransaction(tx.Tx())
    print(txhash)
    time.sleep(4)
    result, err = client.QueryStorage("", txhash)
    print('result:', result)
    # 追加存证
    tx = storage.contentStorage("", txhash, "", "value2", 1)
    tx.Sign(acc)
    client.SendTransaction(tx.Tx())
    time.sleep(4)
    result, err = client.QueryStorage("", txhash)
    print('result:', result)
