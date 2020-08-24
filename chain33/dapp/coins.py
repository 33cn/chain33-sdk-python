#! /user/bin/python3
from chain33.crypto import signer, account, address
from chain33.dapp import transaction as tx
from chain33.protobuf import tx_pb2


def transfer(title: str, amount: int, toAddr: str, note: str) -> tx.Transaction:
    """
    transfer 构造普通转账交易
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param amount: 转账金额
    :param toAddr: 收款地址
    :param note: 备注
    :return: tx.Transaction
    """
    transfer = tx_pb2.AssetsTransfer()
    transfer.amount = amount
    transfer.note = bytes(note, encoding='utf-8')
    transfer.to = toAddr
    action = tx_pb2.CoinsAction(transfer=transfer)
    action.ty = 1
    execer = title + "coins"
    to = toAddr
    if title != "":
        to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


def withdraw(title: str, amount: int, execName: str, note: str) -> tx.Transaction:
    """
     构造提款交易，将其他执行器下面coins代币提回到coins执行器下面
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param amount: 提款金额
    :param execName: 合约名称
    :param note: 备注
    :return: tx.Transaction
    """
    withdraw = tx_pb2.AssetsWithdraw()
    withdraw.amount = amount
    withdraw.note = bytes(note, encoding='utf-8')
    withdraw.execName = execName
    withdraw.to = address.getExecAddress(execName)
    action = tx_pb2.CoinsAction(withdraw=withdraw)
    action.ty = 3
    execer = title + "coins"
    to = withdraw.to
    if title != "":
        to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


def transferToExec(title: str, amount: int, execName: str, note: str) -> tx.Transaction:
    """
    transferToExec 将coins执行器下面的代币转移到其他执行器下面
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param amount: 转账金额
    :param execName: 合约名称
    :param note: 备注
    :return: tx.Transaction
    """
    transfer = tx_pb2.AssetsTransferToExec()
    transfer.amount = amount
    transfer.note = bytes(note, encoding='utf-8')
    transfer.execName = execName
    transfer.to = address.getExecAddress(execName)
    action = tx_pb2.CoinsAction(transferToExec=transfer)
    action.ty = 10
    execer = title + "coins"
    to = transfer.to
    if title != "":
        to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


if __name__ == '__main__':
    print('this a test!')
    acc1 = account.newAccount(signer.SECP256K1)
    # 本地构造转账交易
    tx1 = transfer("", 100000, '19MJmA7GcE1NfMwdGqgLJioBjVbzQnVYvR', "this is a test!")
    tx1.Sign(acc1)
    assert tx1.CheckSign()
    assert tx1.Tx().to == '19MJmA7GcE1NfMwdGqgLJioBjVbzQnVYvR'

    # 本地构造transferToExec交易
    tx2 = transferToExec("", 100000, 'ticket', '把币打到ticket合约下')
    tx2.Sign(acc1)
    assert tx2.CheckSign()
    assert tx2.Tx().to == address.getExecAddress('ticket')

    # 本地构造withdraw交易
    tx3 = withdraw("", 100000, 'ticket', '从ticket合约下提币')
    tx3.Sign(acc1)
    assert tx3.CheckSign()
    assert tx3.Tx().to == address.getExecAddress('ticket')
    print(1 & 1 << 0 == 0)
    print('test sucessfully!')
