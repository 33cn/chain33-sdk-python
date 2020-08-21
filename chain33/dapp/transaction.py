#! /user/bin/python3

import copy
import hashlib
import random
import sys

from chain33.crypto import signer, account
from chain33.crypto.ed25519 import ed25519Signer
from chain33.crypto.gm import sm2
from chain33.protobuf import tx_pb2

MaxTxSize = 100000
MinFee = 100000


# Transaction类，实现对交易得封装，提供签名，验签的方法
class Transaction(object):
    def __init__(self, tx):
        self.tx = tx

    def CheckSign(self) -> bool:
        """
        验签
        :return: bool
        """
        if self.tx.signature.ty == 1:
            copyTx = CopyTx(self.tx)
            data = copyTx.SerializeToString()
            result = signer.verify(data, self.tx.signature.signature, bytes.hex(self.tx.signature.pubkey))
            return result
        elif self.tx.signature.ty == 3:
            copyTx = CopyTx(self.tx)
            data = copyTx.SerializeToString()
            sm2util = sm2.SM2Util()
            result = sm2util.verify(data, bytes.hex(self.tx.signature.pubkey), bytes.hex(self.tx.signature.signature),
                                    "0")
            return result
        elif self.tx.signature.ty == 2:
            copyTx = CopyTx(self.tx)
            data = copyTx.SerializeToString()
            result = ed25519Signer.verify(data, self.tx.signature.signature, self.tx.signature.pubkey.hex())
            return result
        else:
            raise ValueError(
                "Error: signType is not correct."
            )

        return False

    def Sign(self, acc: account.Account) -> tx_pb2.Transaction:
        """
        签名
        :param acc: account账户
        :return:
        """
        copyTx = CopyTx(self.tx)
        self.tx = copyTx
        data = self.tx.SerializeToString()
        self.tx.signature.pubkey = bytes.fromhex(acc.publicKey)
        if acc.signType == signer.SECP256K1:
            self.tx.signature.ty = 1
            self.tx.signature.signature = signer.sign(data, acc.privateKey)
            return self.tx
        elif acc.signType == signer.SM2:
            self.tx.signature.ty = 3
            sm2util = sm2.SM2Util()
            self.tx.signature.signature = bytes.fromhex(sm2util.sign(data, acc.privateKey, "0"))
            return self.tx
        elif acc.signType == signer.ED25519:
            self.tx.signature.ty = 2
            self.tx.signature.signature = ed25519Signer.sign(data, acc.privateKey)
            return self.tx
        else:
            raise ValueError(
                "Error: signType is not correct."
            )

    def Hash(self) -> bytes:
        """
        获取tx的hash值
        :return:
        """
        return Hash(self.tx)

    def Tx(self) -> tx_pb2.Transaction:
        """
        获取tx_pb2.Transaction
        :return:
        """
        return self.tx


# TxGroup 实现对交易组得封装，提供签名，验签的方法
class TxGroup(object):
    def __init__(self, txlist: list, feerate: int):
        self.txgroup = CreateTxGroup(txlist, feerate)

    def Sign(self, acc: account.Account) -> tx_pb2.Transactions:
        """
        签名
        :param acc:
        :return:
        """
        self.txgroup = SignTxGroup(self.txgroup, acc)
        return self.txgroup

    def CheckSign(self) -> bool:
        """
        验证签名
        :return:
        """
        for tx in (self.txgroup.txs):
            if CheckSign(tx) != True:
                return False
        return True

    def Tx(self) -> tx_pb2.Transaction:
        """
        获取tx_pb2.Transaction
        :return:
        """
        if len(self.txgroup.txs) < 2:
            return None
        headtx = self.txgroup.txs[0]
        copytx = copy.deepcopy(headtx)
        data = self.txgroup.SerializeToString()
        copytx.header = data
        return copytx

    def Txs(self) -> tx_pb2.Transactions:
        return self.txgroup


# 构建交易
def CreateTransaction(execer: bytes, payload: bytes, expire: int, to: str) -> Transaction:
    """
    CreateTransaction  构建未签名交易
    :param execer:     执行器
    :param payload:    载体
    :param expire:     逾期时间，0表示永不过期
    :param to:         to地址
    :return:
    """
    tx1 = tx_pb2.Transaction()
    tx1.execer = execer
    tx1.payload = payload
    tx1.expire = expire
    tx1.to = to
    tx1.fee = MinFee
    nonce = random.randint(1, sys.maxsize)
    tx1.nonce = nonce
    return Transaction(tx1)


'''
 以下是函数,实现一些基本函数供tx,txgroup类中方法调用
'''


# tx hash 返回字节切片
def Hash(tx: tx_pb2.Transaction) -> bytes:
    copytx = tx_pb2.Transaction()
    copytx.execer = tx.execer
    copytx.payload = tx.payload
    copytx.expire = tx.expire
    copytx.to = tx.to
    copytx.fee = tx.fee
    copytx.nonce = tx.nonce
    copytx.groupCount = tx.groupCount
    copytx.next = tx.next
    data = copytx.SerializeToString()
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.digest()


def Sign(tx: tx_pb2.Transaction, acc: account.Account) -> tx_pb2.Transaction:
    """
    签名函数
    :param tx: tx_pb2.Transaction
    :param acc: account.Account
    :return:
    """
    copyTx = CopyTx(tx)
    data = copyTx.SerializePartialToString()
    tx.signature.pubkey = bytes.fromhex(acc.publicKey)
    if acc.signType == signer.SECP256K1:
        tx.signature.ty = 1
        tx.signature.signature = signer.sign(data, acc.privateKey)
        return tx
    elif acc.signType == signer.SM2:
        tx.signature.ty = 3
        sm2util = sm2.SM2Util()
        tx.signature.signature = bytes.fromhex(sm2util.sign(data, acc.privateKey, '0'))
        return tx
    elif acc.signType == signer.ED25519:
        tx.signature.ty = 2
        tx.signature.signature = ed25519Signer.sign(data, acc.privateKey)
        return tx
    else:
        raise ValueError(
            "Error: signType is not correct."
        )


def CheckSign(tx: tx_pb2.Transaction) -> bool:
    """
    CheckSign
    :param tx: tx_pb2.Transaction
    :return: bool
    """
    if tx.signature.ty == 1:
        copyTx = CopyTx(tx)
        data = copyTx.SerializeToString()
        result = signer.verify(data, tx.signature.signature, bytes.hex(tx.signature.pubkey))
        return result
    elif tx.signature.ty == 3:
        copyTx = CopyTx(tx)
        data = copyTx.SerializeToString()
        sm2util = sm2.SM2Util()
        result = sm2util.verify(data, bytes.hex(tx.signature.pubkey), bytes.hex(tx.signature.signature), "0")
        return result
    elif tx.signature.ty == 2:
        copyTx = CopyTx(tx)
        data = copyTx.SerializeToString()
        result = ed25519Signer.verify(data, tx.signature.signature, tx.signature.pubkey.hex())
        return result
    else:
        raise ValueError(
            "Error: signType is not correct."
        )

    return False


# 构建交易
def createTx(execer: bytes, payload: bytes, expire: int, to: str) -> tx_pb2.Transaction:
    tx1 = tx_pb2.Transaction()
    tx1.execer = execer
    tx1.payload = payload
    tx1.expire = expire
    tx1.to = to
    tx1.fee = MinFee
    nonce = random.randint(1, sys.maxsize)
    tx1.nonce = nonce

    return tx1


# ClearTxSignature
def CopyTx(tx: tx_pb2.Transaction) -> tx_pb2.Transaction:
    copytx = tx_pb2.Transaction()
    copytx.execer = tx.execer
    copytx.payload = tx.payload
    copytx.expire = tx.expire
    copytx.to = tx.to
    copytx.fee = tx.fee
    copytx.nonce = tx.nonce
    copytx.groupCount = tx.groupCount
    copytx.header = tx.header
    copytx.next = tx.next
    return copytx


# 获取真实手续费
def GetRealFee(tx: tx_pb2.Transaction, minFee: int) -> int:
    """
    GetRealFee
    :param tx: tx_pb2.Transaction
    :param minFee: int
    :return:
    """
    txSize = tx.ByteSize()
    # 如果签名为空，那么加上签名的空间
    if tx.signature == None:
        txSize += 300
    if txSize > MaxTxSize:
        raise Exception('ErrTxMsgSizeTooBig')
    # 检查交易费是否小于最低值
    realFee = (txSize // 1000 + 1) * minFee
    return realFee


# 获取txgroup
def GetTxGroups(tx: tx_pb2.Transaction) -> TxGroup:
    """
    GetTxGroups tx_pb2.Transaction
    :param tx:
    :return:
    """
    if tx.GroupCount < 0 or tx.GroupCount == 1 or tx.GroupCount > 20:
        raise Exception('ErrTxGroupCount')
    if tx.GroupCount > 0:
        txgroup = tx_pb2.Transactions
        txgroup.ParseFromString(tx.header)
        return txgroup


# 构造交易组
def CreateTxGroup(txs: list, feeRate: int) -> tx_pb2.Transactions:
    """
    CreateTxGroup 构造交易组
    :param txs: 交易列表
    :param feeRate: 交易费率
    :return:
    """
    if len(txs) < 2:
        raise Exception('ErrTxGroupCountLessThanTwo')
    txgroup = tx_pb2.Transactions()
    # txgroup.Txs=txs
    totalfee = 0
    minfee = 0
    header = Hash(txs[0])
    for i in range(len(txs) - 1, -1, -1):
        txs[i].groupCount = len(txs)
        totalfee += txs[i].fee
        # Header和Fee设置是为了GetRealFee里面Size的计算，Fee是否为0和不同大小，size也是有差别的，header是否为空差别是common.Sha256Len + 2
        # 这里直接设置Header兼容性更好， Next不需要，已经设置过了，唯一不同的是，txs[0].fee会跟实际计算有差别，这里设置一个超大值只做计算
        txs[i].header = header
        realfee = GetRealFee(txs[i], feeRate)
        txs[i].fee = 0
        minfee += realfee
        if i == 0:
            if totalfee < minfee:
                totalfee = minfee
            txs[0].fee = totalfee
            header = Hash(txs[0])
        else:
            txs[i].fee = 0
            txs[i - 1].next = Hash(txs[i])
    for i in range(0, len(txs), 1):
        txs[i].header = header

    for i in range(0, len(txs), 1):
        txgroup.txs.append(txs[i])
    return txgroup


# 交易组签名
def SignTxGroup(group: tx_pb2.Transactions, acc: account.Account) -> tx_pb2.Transactions:
    """
    交易组签名
    :param group: tx_pb2.Transactions
    :param acc:  account.Account
    :return:
    """
    txgroup = tx_pb2.Transactions()
    for i in range(0, len(group.txs), 1):
        txgroup.txs.append(Sign(group.txs[i], acc))
    return txgroup


def GetTx(txgroup: tx_pb2.Transactions) -> tx_pb2.Transaction:
    """
    GetTx
    :param txgroup: tx_pb2.Transactions
    :return:
    """
    if len(txgroup.txs) < 2:
        return None
    headtx = txgroup.txs[0]
    # 不会影响原来的tx
    copytx = copy.deepcopy(headtx)
    data = txgroup.SerializeToString()
    # 放到header中不影响交易的Hash
    copytx.header = data
    return copytx


if __name__ == '__main__':
    print('this a test!')
    tx1 = createTx(execer=bytes("coins", encoding='utf-8'), payload=bytes("hello world", encoding='utf-8'), expire=0,
                   to="xxxxx")
    acc1 = account.newAccount(signer.SM2)
    tx = Transaction(tx1)
    tx.Sign(acc1)
    assert tx.CheckSign()

    accE = account.newAccount(signer.ED25519)
    txE = Transaction(tx1)
    txE.Sign(accE)
    assert txE.CheckSign()

    tx2 = createTx(execer=bytes("coins", encoding='utf-8'), payload=bytes("hello world", encoding='utf-8'), expire=0,
                   to="xxxxx")
    acc = account.newAccount(signer.SECP256K1)
    tx3 = Sign(tx2, acc)
    assert CheckSign(tx3)
    txs = Transaction(tx2)
    tx = txs.Sign(acc)
    tx5 = Transaction(tx)
    assert tx5.CheckSign()
    assert GetRealFee(tx, MinFee) == MinFee

    # 构建交易组
    tx6 = createTx(execer=bytes("coins", encoding='utf-8'), payload=bytes("hello world1", encoding='utf-8'), expire=0,
                   to="xxxxx")

    tx7 = createTx(execer=bytes("coins", encoding='utf-8'), payload=bytes("hello world2", encoding='utf-8'), expire=0,
                   to="xxxxx")

    tx8 = createTx(execer=bytes("coins", encoding='utf-8'), payload=bytes("hello world3", encoding='utf-8'), expire=0,
                   to="xxxxx")
    txs = []
    txs.append(tx6)
    txs.append(tx7)
    txs.append(tx8)

    txgroup = TxGroup(txs, MinFee)
    # 签名
    txgroup.Sign(acc)
    assert len(txgroup.Txs().txs) == 3
    # 验签
    assert txgroup.CheckSign()
    print('test sucessfully!')

    # 本地构造转账交易
    transfer = tx_pb2.AssetsTransfer()
    transfer.amount = 100000
    transfer.note = bytes("this a test", encoding='utf-8')
    transfer.to = '19MJmA7GcE1NfMwdGqgLJioBjVbzQnVYvR'
    action = tx_pb2.CoinsAction(transfer=transfer)
    action.ty = 1
    tx = createTx(execer=bytes("coins", encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                  to="19MJmA7GcE1NfMwdGqgLJioBjVbzQnVYvR")
    tx = Transaction(tx)
    tx.Sign(acc1)
    assert tx.CheckSign()
