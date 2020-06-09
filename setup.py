from setuptools import setup, find_packages

requires = [

]

setup(
    name='chain33-sdk-python',
    description='chain33 sdk python implementation',
    version='1.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)