#!/usr/bin/python3

import copy
import json
import time

import requests

from chain33.crypto import signer, account, pre
from chain33.dapp import transaction, storage, coins
from chain33.protobuf import tx_pb2, storage_pb2
from chain33.rpc import types


class client:

    def __init__(self, url):
        self.url = url
        self.headers = {'content-type': 'application/json'}

    def Call(self, method, params) -> json:
        """
        rpc调用通用接口
        :param method:方法名称
        :param params: 参数
        :return: json对象
        """
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

    def SendTransaction(self, tx: tx_pb2.Transaction) -> (str, str):
        """
        发送交易
        :param tx: tx_pb2.Transaction
        :return: 交易hash和 错误信息
        """
        hexTx = bytes.hex(tx.SerializeToString())
        resp = self.Call("Chain33.SendTransaction", {"data": hexTx})
        return resp['result'], resp["error"]

    def QueryTransaction(self, txhash) -> (json, str):
        """
        QueryTransaction 查询交易信息
        :param txhash: 交易哈希
        :return:
        """
        resp = self.Call("Chain33.QueryTransaction", {"hash": txhash})
        return resp['result'], resp["error"]

    def GetHexTxByHash(self, hash: str) -> (str, str):
        """
        GetHexTxByHash 根据哈希获取交易的字符串
        :param hash:
        :return:
        """
        resp = self.Call("Chain33.GetHexTxByHash", {"hash": hash})
        return resp['result'], resp["error"]

    def GetTxByAddr(self, addr: str, flag: int, count: int, direction: int, height: int, index: int) -> (list, str):
        """
        GetTxByAddr 根据地址获取交易信息
        :param addr: 要查询的账户地址
        :param flag: 交易类型: 0表示所有涉及到addr的交易， 1表示addr作为发送方  2表示addr作为接收方
        :param count: 单次查询返回得数据条数
        :param direction: 查询方向： 0表示正向查询，区块高度从低到高；-1表示反向查询
        :param height:  交易所在的block高度，-1表示从最新的开始向后取; 大于等于0的值，从具体的高度+具体的index开始取
        :param index: 交易所在block中的索引，取值0-100000
        :return: 交易列表,错误信息
        """
        resp = self.Call("Chain33.GetTxByAddr",
                         {"addr": addr, "flag": flag, "count": count, "direction": direction, "height": height,
                          "index": index})
        infos = resp['result']['txInfos']
        txInfos = []
        for i in range(0, len(infos), 1):
            assets = []
            for j in range(0, len(infos[i]['assets']), 1):
                asset = types.Asset(infos[i]['assets'][j]['exec'], infos[i]['assets'][j]['symbol'],
                                    infos[i]['assets'][j]['amount'])
                assets.append(asset)
            txInfo = types.TxInfo(hash=infos[i]['hash'], hegiht=infos[i]['height'], index=infos[i]['index'],
                                  assets=assets)
            txInfos.append(txInfo)
        return txInfos, resp["error"]

    def CreateNoBalanceTxs(self, txHexs: list, payAddr: str, privkey: str, expire: str) -> (str, str):
        """
        CreateNoBalanceTxs 构造多笔不收手续费的交易组
        :param txHexs:  未签名原始交易数据列表
        :param payAddr:  代扣地址
        :param privkey:  代扣地址私钥
        :param expire:   过期时间  比如300s, 1h24m等等
        :return:     未签名的原始交易数据
        """
        resp = self.Call("Chain33.CreateNoBalanceTxs",
                         {"txHexs": txHexs, "payAddr": payAddr, "privkey": privkey, "expire": expire, })
        return resp['result'], resp['error']

    def GetLastHeader(self) -> (types.BlockHeader, str):
        """
        GetLastHeader 获取最新的区块头信息
        :return: types.BlockHeader和错误信息
        """
        resp = self.Call("Chain33.GetLastHeader", None)
        result = resp['result']
        return types.BlockHeader(result['version'], result['parentHash'], result['txHash'], result['stateHash'],
                                 result['height'], result['blockTime'], result['txCount'], result['hash'],
                                 result['difficulty']), resp["error"]

    def GetVersion(self) -> (types.Version, str):
        resp = self.Call("Chain33.GetLastHeader", None)
        result = resp['result']
        return types.Version(result['title'], result['app'], result['chain33'], result['localDb']), resp["error"]

    def GetBlocks(self, start: int, end: int, isDetail: bool) -> (json, str):
        """
        GetBlocks 获取区间区块
        :param start:  开始区块高度
        :param end:    结束区块高度
        :param isDetail: 是否打印区块详细信息
        :return: json对象 和错误信息
        """
        resp = self.Call("Chain33.GetBlocks", {"start": start, "end": end, "isDetail": isDetail})
        return resp['result'], resp["error"]

    def GetHeaders(self, start: int, end: int, isDetail: bool, pid: list) -> (json, str):
        """
        GetHeaders 获取区间区块头
        :param start:  开始区块高度
        :param end:    结束区块高度
        :param isDetail: 是否打印区块详细信息
        :param pid:   peer列表
        :return: json对象 和错误信息
        """
        resp = self.Call("Chain33.GetHeaders", {"start": start, "end": end, "isDetail": isDetail, "pid": pid})
        return resp['result'], resp["error"]

    def GetBlockHash(self, height: int) -> (str, str):
        """
        GetBlockHash 获取区块哈希
        :param height: 区块高度
        :return: 区块哈希 和错误信息
        """
        resp = self.Call("Chain33.GetBlockHash", {"height": height})
        return resp['result']['hash'], resp["error"]

    def GetLastBlockSequence(self) -> (int, str):
        """
        GetLastBlockSequence 获取最新区块得序列号
        :return: 序列号 和错误信息
        """
        resp = self.Call("Chain33.GetLastBlockSequence", None)
        return resp['result'], resp["error"]

    def AddPushSubscribe(self, name: str, url: str, encode: str, lastSequence: int, lastHeight: int, lastBlockHash: str,
                         type: int, contract: dict) -> (bool, str):
        """
        AddPushSubscribe 注册区块（区块头）推送服务或者合约回执推送服务
        :param name: 注册名称，长度不能超过128,一旦通过name完成注册，其他订阅用户就不能使用相同的名字进行注册
        :param url:  接收推送的URL，长度不能超过1024,当name相同，URL不同，提示该name已经被注册，注册失败，当name相同，URL相同，如果推送已经停止，则重新开始推送，如果推送正常，则继续推送
        :param encode: 数据编码方式：json或者proto
        :param lastSequence: 推送开始序列号
        :param lastHeight: 推送开始高度
        :param lastBlockHash: 推送开始哈希
        :param type: 推送的数据类型；0表示区块， 1代表区块头， 2代表交易回执
        :param contract: 订阅的合约名称，当type=2的时候生效，比如 coins=true
        :return:
        """
        resp = self.Call("Chain33.AddPushSubscribe",
                         {"name": name, "URL": url, "encode": encode, "lastSequence": lastSequence,
                          "lastHeight": lastHeight, "lastBlockHash": lastBlockHash, "type": type, "contract": contract})
        if resp["error"] != None:
            return False, resp["error"]
        return resp['result']['isOk'], resp['result']['msg']

    def ListPushes(self) -> (list, str):
        """
        ListPushes 列举推送服务
        :return: 推送服务列表，错误信息
        """
        resp = self.Call("Chain33.ListPushes", None)
        return resp['result']['items'], resp["error"]

    def GetPushSeqLastNum(self, name: str) -> (int, str):
        """
        GetPushSeqLastNum 获取某推送服务最新序列号的值
        :param name: 推送服务名
        :return: 序列号，错误信息
        """
        resp = self.Call("Chain33.GetPushSeqLastNum", {"data": name})
        return resp['result']['data'], resp["error"]

    def IsSync(self) -> (bool, str):
        """
        IsSync 查询同步状态
        :return: bool和错误信息
        """
        resp = self.Call("Chain33.IsSync", None)
        return resp['result'], resp["error"]

    def GetCoinSymbol(self) -> (str, str):
        """
        GetCoinSymbol 获取主代币信息
        :return: 代币Symbol和错误信息
        """
        resp = self.Call("Chain33.GetCoinSymbol", None)
        return resp['result']['data'], resp["error"]

    # 钱包接口
    def Lock(self) -> (bool, str):
        """
        Lock 钱包加锁
        :return: 是否成功，错误信息
        """
        resp = self.Call("Chain33.Lock", None)
        if resp["error"] != None:
            return False, resp["error"]
        return resp['result']['isOk'], resp['result']['msg']

    def UnLock(self, passwd: str, walletOrTicket: bool, timeout: int) -> (bool, str):
        """
        UnLock 解锁钱包
        :param passwd: 解锁密码
        :param walletOrTicket: true只解锁ticket买票功能，false解锁整个钱包
        :param timeout: 超时时间
        :return: 是否成功，错误信息
        """
        resp = self.Call("Chain33.UnLock", {"passwd": passwd, "walletOrTicket": walletOrTicket, "timeout": timeout})
        if resp["error"] != None:
            return False, resp["error"]
        return resp['result']['isOk'], resp['result']['msg']

    def SetPasswd(self, oldPass: str, newPass: str) -> (bool, str):
        """
        SetPasswd 设置/修改钱包密码
        :param oldPass: 第一次设置密码时，oldPass为空
        :param newPass: 必须时包含8个字符得数字和字母组合
        :return:  是否成功，错误信息
        """
        resp = self.Call("Chain33.SetPasswd", {"oldPass": oldPass, "newPass": newPass})
        if resp["error"] != None:
            return False, resp["error"]
        return resp['result']['isOk'], resp['result']['msg']

    def SetLabl(self, addr: str, label: str) -> (types.LabelAcc, str):
        """
        SetLabl 设置账户标签
        :param addr: 账户地址
        :param label: 账户标签
        :return:  types.LabelAcc,错误信息
        """
        resp = self.Call("Chain33.SetLabl", {"addr": addr, "label": label})
        result = resp['result']
        acc = types.Account(result['acc']['currency'], result['acc']['balance'], result['acc']['frozen'],
                            result['acc']['addr'])
        return types.LabelAcc(result['label'], acc), resp['error']

    def NewAccount(self, label: str) -> (types.LabelAcc, str):
        """
        NewAccount 创建账户
        :param label: 账户标签
        :return: types.LabelAcc,错误信息
        """
        resp = self.Call("Chain33.NewAccount", {"label": label})
        result = resp['result']
        acc = types.Account(result['acc']['currency'], result['acc']['balance'], result['acc']['frozen'],
                            result['acc']['addr'])
        return types.LabelAcc(result['label'], acc), resp['error']

    def GetAccounts(self, withoutBalance: bool) -> (list, str):
        """
        GetAccounts 获取账户列表
        :param withoutBalance: 默认为false，将返回account的信息。为true则返回label和addr信息，其他信息为0
        :return: types.LabelAcc列表，错误信息
        """
        resp = self.Call("Chain33.GetAccounts", {"withoutBalance": withoutBalance})
        wallets = resp['result']['wallets']
        list = []
        for i in range(0, len(wallets), 1):
            result = wallets[i]
            acc = types.Account(result['acc']['currency'], result['acc']['balance'], result['acc']['frozen'],
                                result['acc']['addr'])
            list.append(types.LabelAcc(result['label'], acc))
        return list, resp['error']

    def MergeBalance(self, to: str) -> (list, str):
        """
        MergeBalance 合并账户余额
        :param to: 合并钱包上的所有余额到一个账户地址
        :return: 交易hash列表，错误信息
        """
        resp = self.Call("Chain33.MergeBalance", {"to": to})
        return resp['result']['hashes'], resp['error']

    def ImportPrivKey(self, privkey: str, label: str) -> (types.LabelAcc, str):
        """
        ImportPrivKey 导入私钥
        :param privkey: 私钥
        :param label: 标签
        :return: types.LabelAcc，错误信息
        """
        resp = self.Call("Chain33.ImportPrivKey", {"privkey": privkey, "label": label})
        result = resp['result']
        acc = types.Account(result['acc']['currency'], result['acc']['balance'], result['acc']['frozen'],
                            result['acc']['addr'])
        return types.LabelAcc(result['label'], acc), resp['error']

    def DumpPrivkey(self, addr: str) -> (str, str):
        """
        DumpPrivkey 导出私钥
        :param addr: 账户地址
        :return: 账户地址私钥，错误信息
        """
        resp = self.Call("Chain33.DumpPrivkey", {"data": addr})
        return resp['result']['data'], resp['error']

    def SetTxFee(self, amount: int) -> (bool, str):
        """
        SetTxFee 设置交易费用
        :param amount: 手续费
        :return: 是否成功，错误信息
        """
        resp = self.Call("Chain33.SetTxFee", {"amount": amount})
        if resp["error"] != None:
            return False, resp["error"]
        return resp['result']['isOk'], resp['result']['msg']

    def SendToAddress(self, fromAddr: str, toAddr: str, amount: int, note: str, isToken: bool, tokenSymbol: str) -> (
            str, str):
        """
        SendToAddress 在线发送转账交易
        :param fromAddr: 来源地址
        :param toAddr: 发送到地址
        :param amount: 发送金额
        :param note: 备注
        :param isToken: 是否是token类型的转账（非token转账这个不用填）
        :param tokenSymbol: token的symbol(非token转账不用填）
        :return: 交易hash,错误信息
        """
        resp = self.Call("Chain33.SendToAddress", {"from": fromAddr, "to": toAddr, "amount": amount,
                                                   "note": note, "isToken": isToken, "tokenSymbol": tokenSymbol})
        return resp['result']['hash'], resp['error']

    def SignRawTx(self, addr: str, privkey: str, txHex: str, expire: str, index: int):
        """
        SignRawTx 在线签名交易
        :param addr: 签名地址
        :param privkey: 签名私钥，addr和 privkey只能二选一
        :param txHex: 交易算是数据
        :param expire: 过期时间，可以选择300ms, 2h45m等格式
        :param index: 若是签名交易组，则为要签名的交易序号，从1开始，小于等于0则为签名组内全部交易
        :return: 签名后的交易二进制码，错误信息
        """
        resp = self.Call("Chain33.SignRawTx", {"addr": addr, "privkey": privkey, "txHex": txHex,
                                               "expire": expire, "index": index})
        return resp['result']['txHex'], resp['error']

    def GenSeed(self, lang: int) -> (str, str):
        """
        GenSeed 生成随机的seed
        :param lang: 0表示英文，1表示简体汉字
        :return: seed字符串，错误信息
        """
        resp = self.Call("Chain33.GenSeed", {"lang": lang})
        return resp['result']['seed'], resp['error']

    def SaveSeed(self, seed: str, paaswd: str) -> (bool, str):
        """
        SaveSeed 保存seed
        :param seed:  seed字符串
        :param paaswd: 密码
        :return: 是否成功，错误信息
        """
        resp = self.Call("Chain33.SaveSeed", {"seed": seed, "passwd": paaswd})
        if resp["error"] != None:
            return False, resp["error"]
        return resp['result']['isOk'], resp['result']['msg']

    def GetSeed(self, passwd: str) -> (str, str):
        """
        GetSeed 获取钱包的seed
        :param passwd: 密码
        :return: seed字符串，错误信息
        """
        resp = self.Call("Chain33.GetSeed", {"passwd": passwd})
        return resp['result']['seed'], resp["error"]

    def GetWalletStatus(self) -> (json, str):
        """
        GetWalletStatus 获取钱包状态
        :return: json对象，错误信息
        """
        resp = self.Call("Chain33.GetWalletStatus", None)
        return resp['result'], resp["error"]

    # Dapp 通用的在线构造Transaction的接口
    def CreateTransaction(self, execer: str, actionName: str, payload: json) -> (str, str):
        """
        CreateTransaction 通用的在线构造Transaction的接口
        :param execer:  执行器名称
        :param actionName: 方法名
        :param payload: 业务载体
        :return:  十六进制的未签名的原始交易hexTx,错误信息
        """
        resp = self.Call("Chain33.CreateTransaction", {"execer": execer, "actionName": actionName, "payload": payload})
        return resp['result'], resp["error"]

    # 通用的查询接口
    def Query(self, execer: str, funcName: str, payload: json) -> (json, str):
        """
        Query 通用的查询接口
        :param execer: 执行器名称
        :param funcName: 查询方法名
        :param payload: 查询参数
        :return:   json对象，错误信息
        """
        resp = self.Call("Chain33.Query", {"execer": execer, "funcName": funcName, "payload": payload})
        return resp['result'], resp["error"]

    def SendKeyFragment(self, pubOwner: str, pubRecipient: str, pubProofR: str, pubProofU: str,
                        random: str, value: str, expire: int, dhProof: str, precurPub: str) -> bool:
        """
        SendKeyFragment 发送重加密密钥分片给重加密节点
        :param pubOwner:  数据共享者公钥
        :param pubRecipient: 数据接收者公钥
        :param pubProofR:  重加密随机公钥R
        :param pubProofU:  重加密随机公钥U
        :param random: 密钥分片随机数
        :param value:  密钥分片值
        :param expire:  超时时间
        :param dhProof:  身份证明
        :param precurPub: 密钥分片随机公钥
        :return:  Ture/False
        """
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

    def Reencrypt(self, pubOwner: str, pubRecipient: str) -> pre.ReKeyFrag:
        """
        Reencrypt 申请重加密
        :param pubOwner: 数据共享者公钥
        :param pubRecipient: 数据接收者公钥
        :return: pre.ReKeyFrag 重加密片段
        """
        requestParam = {}
        requestParam["pubOwner"] = pubOwner
        requestParam["pubRecipient"] = pubRecipient
        resp = self.Call("Pre.Reencrypt", requestParam)
        result = resp["result"]
        return pre.ReKeyFrag(result["reKeyR"], result["reKeyU"], result["random"], result["precurPub"])

    def QueryBalance(self, addr: str, execer: str, asset_exec: str, asset_symbol: str) -> (types.Account, str):
        """
        QueryBalance 查询余额
        :param addr:    个人账户地址
        :param execer:  合约名称
        :param asset_exec:  资产类型
        :param asset_symbol:  资产符号
        :return: types.Account，错误信息
        """
        params = {
            "addresses": [
                addr
            ],
            "execer": execer,
            "asset_exec": asset_exec,
            "asset_symbol": asset_symbol
        }
        resp = self.Call("Chain33.GetBalance", params)
        result = resp["result"]
        account = result[0]
        return types.Account(currency=account["currency"], balance=account["balance"], frozen=account["frozen"],
                             addr=account["addr"]), resp["error"]

    def QueryStorage(self, title: str, txHash: str) -> (storage_pb2.Storage, str):
        """
        QueryStorage 查询存证信息
        :param title: 链名前缀，比如user.p.huobi.
        :param txHash: 交易hash或者用户存储时填写得唯一标识key值
        :return: storage_pb2.Storage,错误信息
        """
        params = {
            "execer": title + "storage",
            "funcName": "QueryStorage",
            "payload": {
                "txHash": txHash
            }
        }
        resp = self.Call("Chain33.Query", params)
        # 添加解析函数
        result = resp["result"]
        return storage.parseJsonToStorage(result), resp["error"]


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
