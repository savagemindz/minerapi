#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="minerapi",
    version="0.2.0",
    author="Dmitri Bogomolov",
    author_email="4glitch@gmail.com",
    description="Python wrapper for the miners RPC API",
    license="MIT",
    keywords="cgminer",
    url="https://github.com/g1itch/minerapi",
    packages=["minerapi"],
    package_dir={"minerapi": "src"},
    long_description=read("README.rst"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
)
