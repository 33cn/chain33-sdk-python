from setuptools import setup, find_packages

requires = [
    "ecdsa == 0.15",
    "gmssl == 3.2.1",
    "requests == 2.20.0",
    "protobuf == 3.12.2",
    "pycryptodome == 3.9.7",
    "ed25519 == 1.5",
]

setup(
    name='chain33',
    version='0.1',
    description='Pure Python SDK for Chain33',
    author="harrylee",
    author_email="18761806026@163.com",
    url="https://github.com/33cn/chain33-sdk-python",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    keywords='blockchain,chain33,sdk'
)
