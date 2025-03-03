# -*- coding: utf-8 -*-
"""
Project Name: zyt_validation_utils
File Created: 2025.01.22
Author: ZhangYuetao
File Name: dir_check.py
Update: 2025.01.22
"""

import os


def is_dir(path, raise_error=True):
    """
    判断给定路径是否是一个目录
    :param path: 路径
    :param raise_error: 是否抛出异常（默认 True）
    :return: 如果是目录返回 True，否则返回 False
    """
    if not os.path.exists(path):
        if raise_error:
            raise FileNotFoundError(f'{path}不存在')
        else:
            return False
    if not os.path.isdir(path):
        return False
    return True


def is_dir_empty(dir_path):
    """
    判断文件夹是否为空
    :param dir_path: 文件夹路径
    :return: 如果文件夹为空返回True，否则返回False
    """
    return not os.listdir(dir_path)


def is_have_subdirectories(dir_path):
    """
    判断文件夹下是否含有子文件夹
    :param dir_path: 文件夹路径
    :return: 如果文件夹下含有子文件夹返回True，否则返回False
    """
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            return True
    return False


def is_have_non_subdirectory_files(dir_path):
    """
    判断当前文件夹下是否含有非子文件夹的文件
    :param dir_path: 文件夹路径
    :return: 如果文件夹下含有非子文件夹的文件返回True，否则返回False
    """
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if not os.path.isdir(item_path):
            return True
    return False
