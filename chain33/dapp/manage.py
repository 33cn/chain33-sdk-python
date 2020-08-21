#! /user/bin/python3

from chain33.crypto import address
from chain33.dapp import transaction as tx
from chain33.protobuf import manage_pb2


def createManage(title: str, key: str, value: str, op: str, addr: str) -> tx.Transaction:
    """
    createManage 构造管理合约配置交易
    :param title: 平行链链名前缀 比如user.p.huobi.
    :param key:  类型
    :param value: 具体值
    :param op: 操作符，add,delete
    :param addr: 替换之前addr的值，具有唯一性，这个值不会增加或者删除，始终只有一个
    :return: tx.Transaction
    """
    modify = manage_pb2.ModifyConfig()
    modify.key = key
    modify.value = value
    modify.op = op
    modify.addr = addr
    action = manage_pb2.ManageAction(modify=modify)
    action.ty = 0
    execer = title + "manage"
    to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)
