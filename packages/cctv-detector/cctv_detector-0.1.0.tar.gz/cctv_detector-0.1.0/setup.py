#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取README文件
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

# 读取requirements.txt文件
with open('requirements.txt', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name="cctv-detector",
    version="0.1.0",
    description="智能货舱监控检测库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CCTV Team",
    author_email="example@example.com",
    url="https://github.com/example/cctv-detector",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "cctv-detector=cctv_detector.cli:main",
        ],
    },
) 