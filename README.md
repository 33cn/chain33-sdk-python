# chain33-sdk-python

## 版本

python版本为 3.7

## 安装

**在线安装** 

linux用户可以直接用pip工具安装
```
pip install chain33
```

**本地安装**
```
git clone https://github.com/33cn/chain33-sdk-python.git

cd  chain33-sdk-python

python3 setup.py install


```
## 模块说明

```
chain33
|
|
|------crypto
|        |
|        |--  ed25519         
                    |--ed25519Signer.py  ed25519签名算法实现 
|        |-- gm          
               |--sm2.py 国密2 签名算法实现   
               |--sm3.py 国密3 签名算法实现   
               |--sm4.py 国密4 签名算法实现 
|        |
|        |---account.py  账户模型 （可以新建一个账户，或者根据私实例一个account)
         |---address.py  提供封装的方法（比如getExecAddress获取合约地址）
|        |---pre.py  重加密算法封装实现
|        |---signer.py secp256k1 签名
|
|------dapp
        |-----coins.py   coins执行器中本地构建未签名交易方法的封装
        |-----manage.py  管理合约构建配置交易方法的封装
        |-----storage.py  存证合约构建未签名交易的方法
        |-----token.py    token合约中一个本地构建交易的方法
        |-----transaction.py  transaction模块则实现了交易，交易组的构造，签名，及验签的方法
|         
|------proto  存放定义的proto模板文件
       |---storage.proto
       |---manager.proto
       .....
|  
|------protobuf  生成的protobuf文件
       |-----manage_pb2.py
       .....       
|
|------rpc
       |-----jsonclient.py  jsonclient客户端的实现，用户可通过封装的方法与远程区块链服务端进行交互
|      |-----types.py  自定义一些类，用于接收client远程调用后返回的一些数据
      

```

# 快速上手

```
 参考 demo
```
        

