# -*- coding: utf-8 -*-
"""
Project Name: zyt_validation_utils
File Created: 2025.01.22
Author: ZhangYuetao
File Name: setup.py
Update: 2025.03.03
"""
from setuptools import setup, find_packages

# 读取 README.md 文件内容作为长描述
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="zyt_validation_utils",
    version="0.2.4",
    author="ZhangYuetao",
    author_email="zhang894171707@gmail.com",
    description="A utility package for various validation checks",  # 简短描述
    long_description=long_description,  # 长描述，通常从 README.md 读取
    long_description_content_type="text/markdown",  # 长描述的内容类型
    url="https://github.com/yourusername",  # 项目主页
    packages=find_packages(),  # 自动查找包
    classifiers=[  # 分类器，用于 PyPI 上的分类
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Python 版本要求
    install_requires=[
        'Pillow',  # 图像处理库
        'filetype',  # 文件类型检测库
    ],
)
