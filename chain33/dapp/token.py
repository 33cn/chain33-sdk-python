#! /user/bin/python3
from chain33.crypto import address
from chain33.dapp import manage, transaction as tx
from chain33.protobuf import tx_pb2


def tokenBlackList(title: str, value: str, op: str) -> tx.Transaction:
    """
    tokenBlackList 添加或者删除token黑名单
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param value: 黑名单值，比如bty
    :param op: 操作符， add或者delete
    :return:
    """
    return manage.createManage(title=title, key="token-blacklist", value=value, op=op, addr="")


def tokenFinisher(title: str, addr: str, op: str) -> tx.Transaction:
    """
    tokenFinisher 给某个地址赋予或者收回tokennfinsher权限
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param addr: 授权地址
    :param op: 操作符， add或者delete
    :return:
    """
    return manage.createManage(title=title, key="token-finisher", value=addr, op=op, addr="")


def tokenPreCreate(title: str, name: str, symbol: str, total: int, price: int, owner: str, category: int,
                   introduction: str) -> tx.Transaction:
    """
    tokenPreCreate 构建预创建token的交易
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param name: 代币全称
    :param symbol: 代币符号,大小写字母+数字
    :param total: 发行总量
    :param price: 需要质押的coins代币数量，可以填0
    :param owner: 发行地址
    :param category: 代币种类,值为1时表示支持Mint和Burn操作，其他值则表示不支持增发和销毁
    :param introduction: 说明
    :return:
    """
    tokenPreCreate = tx_pb2.TokenPreCreate()
    tokenPreCreate.name = name
    tokenPreCreate.symbol = symbol
    tokenPreCreate.total = total
    tokenPreCreate.price = price
    tokenPreCreate.owner = owner
    tokenPreCreate.category = category
    tokenPreCreate.introduction = introduction
    action = tx_pb2.TokenAction(tokenPreCreate=tokenPreCreate)
    action.ty = 7
    execer = title + "token"
    to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


def tokenFinishCreate(title: str, symbol: str, owner: str) -> tx.Transaction:
    """
    tokenFinishCreate 构建完成创建token的交易
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param symbol: 代币符号
    :param owner: 发行地址
    :return: tx.Transaction
    """
    tokenFinishCreate = tx_pb2.TokenFinishCreate()
    tokenFinishCreate.owner = owner
    tokenFinishCreate.symbol = symbol
    action = tx_pb2.TokenAction(tokenFinishCreate=tokenFinishCreate)
    action.ty = 8
    execer = title + "token"
    to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


def tokenRevokeCreate(title: str, symbol: str, owner: str) -> tx.Transaction:
    """
    tokenRevokeCreate 构造撤销创建token的交易
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param symbol: 代币符号
    :param owner: 发行地址
    :return:
    """
    tokenRevokeCreate = tx_pb2.TokenRevokeCreate()
    tokenRevokeCreate.owner = owner
    tokenRevokeCreate.symbol = symbol
    action = tx_pb2.TokenAction(tokenRevokeCreate=tokenRevokeCreate)
    action.ty = 9
    execer = title + "token"
    to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


def transfer(title: str, symbol: str, amount: int, toAddr: str, note: str) -> tx.Transaction:
    """
    transfer 构造普通token转账交易
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param symbol: 代币符号
    :param amount: 转账金额
    :param toAddr: 收款地址
    :param note:  备注
    :return:
    """
    transfer = tx_pb2.AssetsTransfer()
    transfer.amount = amount
    transfer.note = bytes(note, encoding='utf-8')
    transfer.to = toAddr
    transfer.cointoken = symbol
    action = tx_pb2.TokenAction(transfer=transfer)
    action.ty = 4
    execer = title + "token"
    to = toAddr
    if title != "":
        to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


# withdraw 构造提款交易，将其他执行器下面token代币提回到token执行器下面
def withdraw(title: str, symbol: str, amount: int, execName: str, note: str) -> tx.Transaction:
    """
    withdraw 构造提款交易，将其他执行器下面token代币提回到token执行器下面
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param symbol: 代币符号
    :param amount:  金额
    :param execName: 合约名称
    :param note: 备注
    :return:
    """
    withdraw = tx_pb2.AssetsWithdraw()
    withdraw.amount = amount
    withdraw.note = bytes(note, encoding='utf-8')
    withdraw.to = address.getExecAddress(execName)
    withdraw.cointoken = symbol
    withdraw.execName = execName
    action = tx_pb2.TokenAction(withdraw=withdraw)
    action.ty = 6
    execer = title + "token"
    to = withdraw.to
    if title != "":
        to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


def transferToExec(title: str, symbol: str, amount: int, execName: str, note: str) -> tx.Transaction:
    """
    transferToExec 将token执行器下面的代币转移到其他执行器下面
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param symbol: 代币符号
    :param amount: 金额
    :param execName: 合约名称
    :param note: 备注
    :return:
    """
    transfer = tx_pb2.AssetsTransferToExec()
    transfer.cointoken = symbol
    transfer.amount = amount
    transfer.note = bytes(note, encoding='utf-8')
    transfer.to = address.getExecAddress(execName)
    transfer.execName = execName
    action = tx_pb2.TokenAction(transferToExec=transfer)
    action.ty = 11
    execer = title + "token"
    to = transfer.to
    if title != "":
        to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


def tokenMint(title: str, symbol: str, amount: int) -> tx.Transaction:
    """
    tokenMint 构造增发token的交易
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param symbol: 代币符号
    :param amount: 增发数量
    :return:
    """
    tokenMint = tx_pb2.TokenMint()
    tokenMint.symbol = symbol
    tokenMint.amount = amount
    action = tx_pb2.TokenAction(tokenMint=tokenMint)
    action.ty = 12
    execer = title + "token"
    to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


def tokenBurn(title: str, symbol: str, amount: int) -> tx.Transaction:
    """
    tokenBurn 构造销毁指定数量token的交易
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param symbol: 代币符号
    :param amount: 销毁数量
    :return:
    """
    tokenBurn = tx_pb2.TokenBurn()
    tokenBurn.symbol = symbol
    tokenBurn.amount = amount
    action = tx_pb2.TokenAction(tokenBurn=tokenBurn)
    action.ty = 13
    execer = title + "token"
    to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)
