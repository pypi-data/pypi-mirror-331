from distutils.core import setup
import setuptools
packages = ['logcsq']# 唯一的包名，自己取名
setup(name='logcsq',
	version='0.0.1',
	author='csq',
    packages=packages,
    package_dir={'requests': 'requests'},)
