#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Kutina
# Mail: wang@kutina.cn
# Created Time:  2024-3-3
#############################################

from setuptools import setup, find_packages

setup(
    name = "fovbpsk",      #这里是pip项目发布的名称
    version = "1.0.1",  #版本号，数值大的会优先被pip
    keywords = ("pip", "Kutina"),
    description = "FOVBPS-Kkutina",
    long_description = "FOVBPSK-Kkutin",
    license = "MIT Licence",

    url = "https://github.com/Cache-Cloud/FOVBPSK-Kutina",
    author = "Kutina",
    author_email = "wang@kutina.cn",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["setuptools", "setuptools-scm", "numpy"]
)
