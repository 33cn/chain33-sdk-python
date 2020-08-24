import json


# 账户信息
class Account(object):
    def __init__(self, currency: int, balance: int, frozen: int, addr: str):
        self.currency = currency
        self.balance = balance
        self.frozen = frozen
        self.addr = addr

    # 自定义json序列化函数
    def obj_json(self, obj) -> object:
        return {
            "currency": obj.currency,
            "balance": obj.balance,
            "frozen": obj.frozen,
            "addr": obj.addr
        }


# 自定义反序函数
def jsonToClass(obj: json) -> Account:
    return Account(obj['currency'], obj['balance'], obj['frozen'], obj['addr'])


# 账户标签
class LabelAcc(object):
    def __init__(self, label: str, acc: Account):
        self.label = label
        self.acc = acc


# 区块头信息
class BlockHeader(object):
    def __init__(self, version: int, parent_hash: str, tx_hash: str, state_hash: str, height: int, block_time: int,
                 tx_count: int, hash_str: str, difficulty: int):
        self.version = version
        self.parentHash = parent_hash
        self.txHash = tx_hash
        self.stateHash = state_hash
        self.height = height
        self.blockTime = block_time
        self.txCount = tx_count
        self.hash = hash_str
        self.difficulty = difficulty


# 资产信息
class Asset(object):
    def __init__(self, exec: str, symbol: str, amount: int):
        self.exec = exec
        self.symbol = symbol
        self.amount = amount


# 交易信息
class TxInfo(object):
    def __init__(self, hash_str: str, height: int, index: int, assets: list):
        self.hash = hash_str
        self.height = height
        self.index = index
        self.assets = assets


# 版本信息
class Version(object):
    def __init__(self, title: str, app: str, chain33: str, local_db: str):
        self.title = title
        self.app = app
        self.chain33 = chain33
        self.localDb = local_db


# 区块信息
class Block(object):
    def __init__(self, version: int, parent_hash: str, tx_hash: str, state_hash: str, height: int, block_time: int,
                 txs: json):
        self.version = version
        self.parentHash = parent_hash
        self.txHash = tx_hash
        self.stateHash = state_hash
        self.height = height
        self.blockTime = block_time
        self.txs = txs


# 回执日志
class ReceiptDataResult(object):
    def __init__(self, ty: int, ty_name: str, logs: list):
        self.ty = ty
        self.tyName = ty_name
        self.logs = logs


# log
class ReceiptLog(object):
    def __init__(self, ty: int, ty_name: str, log: str, raw_log: str):
        self.ty = ty
        self.tyName = ty_name
        self.log = log
        self.rawLog = raw_log


if __name__ == '__main__':
    account = Account(currency=0, balance=1, frozen=2, addr="")
    json_str = json.dumps(account, default=account.obj_json)
    print(json_str)
    # 通过__dict__属性实现序列化
    json_str = json.dumps(account, default=lambda account: account.__dict__)
    print(json_str)
    # 将json对象实例化成一个类对象
    acc = json.loads(json_str, object_hook=jsonToClass)
    print(type(acc))
    print(acc.balance)
