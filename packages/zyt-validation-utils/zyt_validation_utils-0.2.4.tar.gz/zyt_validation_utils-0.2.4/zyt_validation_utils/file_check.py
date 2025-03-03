# -*- coding: utf-8 -*-
"""
Project Name: zyt_validation_utils
File Created: 2025.01.17
Author: ZhangYuetao
File Name: file_check.py
Update: 2025.03.03
"""

import os
import sys
import time
from PIL import Image, UnidentifiedImageError
import filetype

import zyt_validation_utils.config as config


def is_file(path, raise_error=True):
    """
    判断路径是否为文件

    :param path: 文件路径
    :param raise_error: 是否抛出异常（默认 True）
    :return: True 如果是文件，否则 False
    """
    if not os.path.exists(path):
        if raise_error:
            raise FileNotFoundError(f'{path}不存在')
        else:
            return False
    if not os.path.isfile(path):
        return False
    return True


def is_empty_file(file_path):
    """
    判断文件是否为空文件

    :param file_path: 文件路径
    :return: True 如果是空文件，否则 False
    """
    if os.path.getsize(file_path) == 0:
        return True
    return False


def is_image(file_path, speed="normal", raise_error=True):
    """
    判断文件是否为图片文件

    :param file_path: 文件路径
    :param speed: 检测模式，'fast' 或 'normal'（默认）
    :param raise_error: 是否抛出异常（默认 True）
    :return: True 如果是图片文件，否则 False
    """
    if speed == 'fast':
        # 使用后缀名快速判断
        result = file_path.lower().endswith(tuple(config.IMAGE_MAP))
        return result
    else:
        # 使用 filetype 库进行判断
        try:
            result = filetype.is_image(file_path)
            return result
        except Exception as e:
            if raise_error:
                raise ValueError(f"检测图片文件失败: {file_path}, 错误: {e}")
            else:
                return False


def is_image_complete(image_path, speed="normal", raise_error=True):
    """
    判断图片文件是否完整

    :param image_path: 文件路径
    :param speed: 检测模式，'fast'、'normal'（默认）或 'strict'
    :param raise_error: 是否抛出异常（默认 True）
    :return: True 如果是图片文件且完整，否则 False
    """
    # 检查文件大小
    if os.path.getsize(image_path) == 0:
        return False

    # 快速模式：仅检查文件大小和文件头
    if speed == "fast":
        try:
            with open(image_path, "rb") as f:
                header = f.read(4)  # 读取文件头
                if not header:
                    return False
            return True
        except Exception as e:
            if raise_error:
                raise ValueError(f"快速模式检查失败: {image_path}, 错误: {e}")
            else:
                return False
    # 严格模式：检查文件大小、文件头、图像结构和像素数据
    elif speed == "strict":
        try:
            with Image.open(image_path) as img:
                img.verify()  # 验证图像结构
                img.load()    # 加载图像数据
                # 检查图像尺寸是否有效
                if img.size[0] == 0 or img.size[1] == 0:
                    return False
            return True
        except UnidentifiedImageError:
            return False
        except Exception as e:
            if raise_error:
                raise ValueError(f"严格模式检查失败: {image_path}, 错误: {e}")
            else:
                return False
    # 正常模式：检查文件大小、文件头和图像结构
    else:
        try:
            with Image.open(image_path) as img:
                img.verify()  # 验证图像结构
            return True
        except UnidentifiedImageError:
            return False
        except Exception as e:
            if raise_error:
                raise ValueError(f"正常模式检查失败: {image_path}, 错误: {e}")
            else:
                return False


def is_video(file_path, speed="normal", raise_error=True):
    """
    判断文件是否为视频文件

    :param file_path: 文件路径
    :param speed: 检测模式，'fast' 或 'normal'（默认）
    :param raise_error: 是否抛出异常（默认 True）
    :return: True 如果是视频文件，否则 False
    """
    if speed == 'fast':
        result = file_path.lower().endswith(tuple(config.VIDEO_MAP))
        return result
    else:
        try:
            result = filetype.is_video(file_path)
            return result
        except Exception as e:
            if raise_error:
                raise ValueError(f"检测视频文件失败: {file_path}, 错误: {e}")
            else:
                return False


def is_audio(file_path, speed="normal", raise_error=True):
    """
    判断文件是否为音频文件

    :param file_path: 文件路径
    :param speed: 检测模式，'fast' 或 'normal'（默认）
    :param raise_error: 是否抛出异常（默认 True）
    :return: True 如果是音频文件，否则 False
    """
    if speed == 'fast':
        result = file_path.lower().endswith(tuple(config.AUDIO_MAP))
        return result
    else:
        try:
            result = filetype.is_audio(file_path)
            return result
        except Exception as e:
            if raise_error:
                raise ValueError(f"检测音频文件失败: {file_path}, 错误: {e}")
            else:
                return False


def is_archive(file_path, speed="normal", raise_error=True):
    """
    判断文件是否为压缩文件

    :param file_path: 文件路径
    :param speed: 检测模式，'fast' 或 'normal'（默认）
    :param raise_error: 是否抛出异常（默认 True）
    :return: True 如果是压缩文件，否则 False
    """
    if speed == 'fast':
        result = file_path.lower().endswith(tuple(config.ARCHIVE_MAP))
        return result
    else:
        try:
            result = filetype.is_archive(file_path)
            return result
        except Exception as e:
            if raise_error:
                raise ValueError(f"检测压缩文件失败: {file_path}, 错误: {e}")
            else:
                return False


def is_bin(file_path, speed="normal", raise_error=True):
    """
    判断文件是否为二进制.bin文件

    :param file_path: 文件路径
    :param speed: 检测模式，'fast' 或 'normal'（默认）
    :param raise_error: 是否抛出异常（默认 True）
    :return: True 如果是二进制文件，否则 False
    """

    endswith = file_path.lower().endswith('.bin')
    if not endswith:
        return False

    if speed == 'fast':
        return True
    else:
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)  # 读取前1024字节
                result = b'\0' in chunk
            return result
        except Exception as e:
            if raise_error:
                raise ValueError(f"检测二进制文件失败: {file_path}, 错误: {e}")
            else:
                return False


def is_current_file_frozen():
    """
    判断当前程序是否被打包成可执行文件。

    :return: 如果是打包的可执行文件返回 True，否则返回 False
    """
    # 检查 sys.frozen 属性
    if getattr(sys, 'frozen', False):
        return True
    # 检查是否在 PyInstaller 的临时解压目录中运行
    if hasattr(sys, '_MEIPASS'):
        return True
    # 其他打包工具的检查（可根据需要扩展）
    return False


def is_file_load_complete(file_path, timeout=60, raise_error=True):
    """
    检查文件是否完全复制完成。

    :param file_path: 文件路径
    :param timeout: 最大等待时间（秒）
    :param raise_error: 是否抛出异常（默认 True）
    :return: 如果文件复制完成则返回 True，否则返回 False
    """
    if raise_error:
        try:
            if not is_file(file_path, raise_error=True):
                raise ValueError(f'{file_path}不是文件')
        except FileNotFoundError:
            raise
    else:
        if not is_file(file_path, raise_error=False):
            return False

    initial_size = os.path.getsize(file_path)
    time.sleep(1)  # 等待1秒钟，给文件写入一些时间
    final_size = os.path.getsize(file_path)

    # 如果文件大小没有变化，认为文件已复制完成
    if initial_size == final_size:
        return True

    # 如果文件大小仍在变化，则继续等待
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(1)
        new_size = os.path.getsize(file_path)
        if new_size == final_size:
            return True
        final_size = new_size

    # 超过最大等待时间后认为文件未复制完成
    return False


def is_rgb_image(file_path, image_check_speed="normal", raise_error=True):
    """
    判断输入图像是否为彩色图

    :param file_path: 文件路径
    :param image_check_speed: 检测模式，继承自 is_image 的 'fast' 或 'normal'（默认）
    :param raise_error: 是否抛出异常（默认 True）
    :return: True 如果是彩色图像，否则 False
    """
    if raise_error:
        try:
            if not is_image(file_path, image_check_speed, raise_error=True):
                raise ValueError(f'{file_path}不是图像')
        except ValueError:
            raise
    else:
        if not is_image(file_path, image_check_speed, raise_error=False):
            return False

    try:
        with Image.open(file_path) as img:
            if img.mode in config.PIL_RGB_LIST:
                return True
            else:
                return False
    except Exception as e:
        if raise_error:
            raise f"图像类型判断失败，错误原因:{e}"
        else:
            return False


def is_gray_image(file_path, image_check_speed="normal", raise_error=True):
    """
    判断输入图像是否为灰度图

    :param file_path: 文件路径
    :param image_check_speed: 检测模式，继承自 is_image 的 'fast' 或 'normal'（默认）
    :param raise_error: 是否抛出异常（默认 True）
    :return: True 如果是灰度图像，否则 False
    """
    if raise_error:
        try:
            if not is_image(file_path, image_check_speed, raise_error=True):
                raise ValueError(f'{file_path}不是图像')
        except ValueError:
            raise
    else:
        if not is_image(file_path, image_check_speed, raise_error=False):
            return False

    try:
        with Image.open(file_path) as img:
            if img.mode in config.PIL_GRAY_LIST:
                return True
            else:
                return False
    except Exception as e:
        if raise_error:
            raise f"图像类型判断失败，错误原因:{e}"
        else:
            return False


def is_depth_image(file_path, image_check_speed="normal", raise_error=True):
    """
    判断输入图像是否为深度图

    :param file_path: 文件路径
    :param image_check_speed: 检测模式，继承自 is_image 的 'fast' 或 'normal'（默认）
    :param raise_error: 是否抛出异常（默认 True）
    :return: True 如果是深度图像，否则 False
    """
    if raise_error:
        try:
            if not is_image(file_path, image_check_speed, raise_error=True):
                raise ValueError(f'{file_path}不是图像')
        except ValueError:
            raise
    else:
        if not is_image(file_path, image_check_speed, raise_error=False):
            return False

    try:
        with Image.open(file_path) as img:
            if img.mode in config.PIL_DEPTH_LIST:
                return True
            else:
                return False
    except Exception as e:
        if raise_error:
            raise f"图像类型判断失败，错误原因:{e}"
        else:
            return False


def is_rgb_video(file_path, video_check_speed="normal", raise_error=True):
    """
    判断输入图像是否为彩色图视频

    :param file_path: 文件路径
    :param video_check_speed: 检测模式，继承自 is_video 的 'fast' 或 'normal'（默认）
    :param raise_error: 是否抛出异常（默认 True）
    :return: True 如果是彩色图像，否则 False
    """
    if raise_error:
        try:
            if not is_video(file_path, video_check_speed, raise_error=True):
                raise ValueError(f'{file_path}不是视频')
        except ValueError:
            raise
    else:
        if not is_video(file_path, video_check_speed, raise_error=False):
            return False

    try:
        with Image.open(file_path) as img:
            if img.mode in config.PIL_RGB_LIST:
                return True
            else:
                return False
    except Exception as e:
        if raise_error:
            raise f"视频类型判断失败，错误原因:{e}"
        else:
            return False
