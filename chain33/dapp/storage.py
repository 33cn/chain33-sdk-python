#! /user/bin/python3
import json

from chain33.crypto import address
from chain33.dapp import transaction as tx
from chain33.protobuf import storage_pb2


def contentStorage(title: str, key: str, content: bytes, value: str, op: int) -> tx.Transaction:
    """
    contentStorage 构建明文存证交易，返回Transaction类对象实例
    :param title: 链名前缀，比如user.p.huobi.     (主链填空字符串即可）
    :param key: 唯一标识，后面可以根据key来查询存证内容，如果不填则默认以txhash作为key
    :param content: 存证内容,（注意 content和value只能二选一，不可同时填写，要么选择bytes类型存储，要么选择str类型存储）
    :param value: 存证内容（注意 content和value只能二选一，不可同时填写，要么选择bytes类型存储，要么选择str类型存储）
    :param op:  0表示创建 1表示追加add
    :return:
    """
    if op != 0 and op != 1:
        raise ValueError(
            "Error: op is not correct."
        )
    v = storage_pb2.ContentOnlyNotaryStorage()
    v.key = key
    v.value = value
    v.op = op
    action = storage_pb2.StorageAction(contentStorage=v)
    action.ty = 1
    execer = title + "storage"
    to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


def hashStorage(title: str, key: str, hash: bytes, value: str) -> tx.Transaction:
    """
    hashStorage 构建哈希存证交易，返回Transaction类对象实例
    :param title: 链名前缀，比如user.p.huobi.     (主链填空字符串即可）
    :param key: 唯一标识，后面可以根据key来查询存证内容，如果不填则默认以txhash作为key
    :param hash: 存证内容
    :param value: 存证内容,用户可以先将Hash值 str
    :return:
    """
    v = storage_pb2.HashOnlyNotaryStorage()
    v.key = key
    v.value = value
    v.hash = hash
    action = storage_pb2.StorageAction(hashStorage=v)
    action.ty = 2
    execer = title + "storage"
    to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


def linkStorage(title: str, key: str, link: bytes, value: str) -> tx.Transaction:
    """
    linkStorage 构建链接存证交易，返回Transaction类对象实例
    :param title: 链名前缀，比如user.p.huobi.     (主链填空字符串即可）
    :param key: 唯一标识，后面可以根据key来查询存证内容，如果不填则默认以txhash作为key
    :param link: 存证内容
    :param value: 备注
    :return:
    """
    v = storage_pb2.LinkNotaryStorage()
    v.key = key
    v.value = value
    v.link = link
    action = storage_pb2.StorageAction(linkStorage=v)
    action.ty = 3
    execer = title + "storage"
    to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


def encryptStorage(title: str, key: str, contentHash: bytes, encryptContent: bytes, nonce: bytes,
                   value: str) -> tx.Transaction:
    """
    encryptStorage 构建加密存证交易，返回Transaction类对象实例
    :param title: 链名前缀，比如user.p.huobi.     (主链填空字符串即可）
    :param key: 唯一标识，后面可以根据key来查询存证内容，如果不填则默认以txhash作为key
    :param contentHash: 存证明文hash
    :param encryptContent: 密文
    :param nonce: 加密iv，通过AES进行加密时制定随机生成的iv,解密时需要使用该值
    :param value: 备注
    :return:
    """
    v = storage_pb2.EncryptNotaryStorage()
    v.key = key
    v.value = value
    v.contentHash = contentHash
    v.encryptContent = encryptContent
    v.nonce = nonce
    action = storage_pb2.StorageAction(encryptStorage=v)
    action.ty = 4
    execer = title + "storage"
    to = address.getExecAddress(execer)
    return tx.CreateTransaction(execer=bytes(execer, encoding='utf-8'), payload=action.SerializeToString(), expire=0,
                                to=to)


def parseJsonToStorage(data: json) -> storage_pb2.Storage:
    """
    parseJsonToStorage json rpc接口查询解析函数，将json对象解析成storage对象
    :param data: json字典集对象
    :return: storage_pb2.Storage
    """
    storage = storage_pb2.Storage
    if data['ty'] == 1:
        v = storage_pb2.ContentOnlyNotaryStorage()
        v.key = data["contentStorage"]["key"]
        v.value = data["contentStorage"]["value"]
        if data["contentStorage"]["content"] != None:
            v.content = data["contentStorage"]["content"]
        v.op = data["contentStorage"]["op"]
        storage = storage_pb2.Storage(contentStorage=v)
        storage.ty = 1
    if data['ty'] == 2:
        v = storage_pb2.HashOnlyNotaryStorage()
        v.key = data["hashStorage"]["key"]
        v.value = data["hashStorage"]["value"]
        if data["hashStorage"]["hash"] != None:
            v.hash = data["hashStorage"]["hash"]
        storage = storage_pb2.Storage(hashStorage=v)
        storage.ty = 2
    if data['ty'] == 3:
        v = storage_pb2.LinkNotaryStorage()
        v.key = data["linkStorage"]["key"]
        v.value = data["linkStorage"]["value"]
        if data["linkStorage"]["link"] != None:
            v.link = data["linkStorage"]["link"]
        storage = storage_pb2.Storage(linkStorage=v)
        storage.ty = 3
    if data['ty'] == 4:
        v = storage_pb2.EncryptNotaryStorage()
        v.key = data["encryptStorage"]["key"]
        v.value = data["encryptStorage"]["value"]
        if data["encryptStorage"]["contentHash"] != None:
            v.contentHash = data["encryptStorage"]["contentHash"]
        v.encryptContent = data["encryptStorage"]["encryptContent"]
        v.nonce = data["encryptStorage"]["nonce"]
        storage = storage_pb2.Storage(encryptStorage=v)
        storage.ty = 4
    return storage
