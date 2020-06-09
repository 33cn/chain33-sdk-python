# chain33-sdk-python

## 版本

python版本为 3.7

## 安装

```
git clone https://github.com/33cn/chain33-sdk-python.git

cd  chain33-sdk-python

python3 setup.py install

```
## 模块说明

模块|功能
----|------
crypto| 提供基础的如secp256k,sm2,sm3等加密算法
protobuf|提供了交易序列化，反序列化得方法，实现了交易，交易组的构造，签名，及验签的方法
rpc|封装了与chain33底层 json rpc 交互的 client
account|提供生成账户的方法，交易的签名需要用到account模块