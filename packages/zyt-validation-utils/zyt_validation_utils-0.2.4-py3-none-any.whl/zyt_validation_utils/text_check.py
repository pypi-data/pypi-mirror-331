# -*- coding: utf-8 -*-
"""
Project Name: zyt_validation_utils
File Created: 2025.01.17
Author: ZhangYuetao
File Name: text_check.py
Update: 2025.01.23
"""

import re


def is_have_chinese(text):
    """
    判断字符串是否含有中文字符。

    :param text: 输入的文本。
    :return: 如果含有中文返回 True，否则返回 False。
    """
    result = any('\u4e00' <= char <= '\u9fff' for char in text)
    return result


def is_all_chinese(text):
    """
    判断字符串是否全部由中文字符组成。

    :param text: 输入的文本。
    :return: 如果全部是中文返回 True，否则返回 False。
    """
    result = all('\u4e00' <= char <= '\u9fff' for char in text)
    return result


def is_have_english(text):
    """
    判断字符串是否含有英文字符。

    :param text: 输入的文本。
    :return: 如果含有英文字符返回 True，否则返回 False。
    """
    result = any('a' <= char.lower() <= 'z' for char in text)
    return result


def is_all_english(text):
    """
    判断字符串是否全部由英文字符组成。

    :param text: 输入的文本。
    :return: 如果全部是英文字符返回 True，否则返回 False。
    """
    result = all('a' <= char.lower() <= 'z' for char in text)
    return result


def is_have_digit(text):
    """
    判断字符串是否含有数字。

    :param text: 输入的文本。
    :return: 如果含有数字返回 True，否则返回 False。
    """
    result = any(char.isdigit() for char in text)
    return result


def is_all_digit(text):
    """
    判断字符串是否全部由数字组成。

    :param text: 输入的文本。
    :return: 如果全部是数字返回 True，否则返回 False。
    """
    result = all(char.isdigit() for char in text)
    return result


def is_have_special_char(text):
    """
    判断字符串是否含有特殊字符（非字母、非数字、非中文）。

    :param text: 输入的文本。
    :return: 如果含有特殊字符返回 True，否则返回 False。
    """
    result = any(not ('a' <= char.lower() <= 'z' or char.isdigit() or '\u4e00' <= char <= '\u9fff') for char in text)
    return result


def is_all_special_char(text):
    """
    判断字符串是否全部由特殊字符组成（非字母、非数字、非中文）。

    :param text: 输入的文本。
    :return: 如果全部是特殊字符返回 True，否则返回 False。
    """
    result = all(not ('a' <= char.lower() <= 'z' or char.isdigit() or '\u4e00' <= char <= '\u9fff') for char in text)
    return result


def is_have_normal_space(text):
    """
    判断字符串是否含有空格字符。

    :param text: 输入的文本。
    :return: 如果含有空格字符返回 True，否则返回 False。
    """
    result = ' ' in text
    return result


def is_have_any_space(text):
    """
    判断字符串是否含有空白字符（包括空格、制表符、换行符等）。

    :param text: 输入的文本。
    :return: 如果含有空白字符返回 True，否则返回 False。
    """
    result = any(char.isspace() for char in text)
    return result


def is_have(text, check):
    """
    判断字符串中是否包含给定的字符或子字符串。

    :param text: 输入的文本。
    :param check: 需要检查的字符、子字符串或判断函数。
                 可以是单个字符、字符串、列表、集合或元组。
    :return: 如果包含给定的字符或子字符串返回 True，否则返回 False。
    """
    if isinstance(check, (list, set, tuple)):
        # 如果 check 是列表、集合或元组，检查是否包含其中任意一个字符串
        result = any(item in text for item in check)
        return result
    else:
        # 如果 check 是单个字符或子字符串，直接检查是否包含
        result = str(check) in text
        return result


def is_email(text):
    """
    判断字符串是否为有效邮箱地址。

    :param text: 输入的文本。
    :return: 如果是有效邮箱返回 True，否则返回 False。
    """
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    result = re.match(pattern, text) is not None
    return result


def is_url(text):
    """
    判断字符串是否为有效URL。

    :param text: 输入的文本。
    :return: 如果是有效URL返回 True，否则返回 False。
    """
    pattern = r'^(http|https)://[^\s/$.?#].[^\s]*$'
    result = re.match(pattern, text) is not None
    return result


def is_ipv4_address(text):
    """
    判断字符串是否为有效IPv4地址。

    :param text: 输入的文本。
    :return: 如果是有效IPv4地址返回 True，否则返回 False。
    """
    # 使用正则表达式匹配 IPv4 地址格式
    if not re.match(r'^(\d{1,3}(\.|$)){4}', text):
        return False

    # 检查每个部分是否在 0 到 255 之间
    try:
        parts = list(map(int, text.split('.')))
        result = all(0 <= part <= 255 for part in parts)
        return result
    except (ValueError, AttributeError):
        return False


def is_ipv6_address(text):
    """
    判断字符串是否为有效IPv6地址。

    :param text: 输入的文本。
    :return: 如果是有效IPv6地址返回 True，否则返回 False。
    """
    # 正则表达式匹配 IPv6 地址
    ipv6_pattern = (
        r'^(?:'
        r'([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|'  # 标准格式
        r'([0-9a-fA-F]{1,4}:){1,7}:|'               # 省略开头的零组
        r'([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|'  # 省略中间的零组
        r'([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|'
        r'([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|'
        r'([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|'
        r'([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|'
        r'[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|'  # 省略结尾的零组
        r':((:[0-9a-fA-F]{1,4}){1,7}|:)|'               # 全零地址
        r'fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]+|'  # 链路本地地址
        r'::(ffff(:0{1,4})?:)?((25[0-5]|(2[0-4]|1?[0-9])?[0-9])\.){3}(25[0-5]|(2[0-4]|1?[0-9])?[0-9])|'  # IPv4 映射地址
        r'([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1?[0-9])?[0-9])\.){3}(25[0-5]|(2[0-4]|1?[0-9])?[0-9])'  # IPv4 兼容地址
        r')$'
    )
    result = re.match(ipv6_pattern, text) is not None
    return result


def is_ip_address(text):
    """
    判断字符串是否为有效IP地址（支持IPv4和IPv6）。

    :param text: 输入的文本。
    :return: 如果是有效IP地址返回 True，否则返回 False。
    """
    result = is_ipv4_address(text) or is_ipv6_address(text)
    return result


def is_mac_address(text):
    """
    判断字符串是否为有效的MAC地址。

    :param text: 输入的文本。
    :return: 如果是有效MAC地址返回 True，否则返回 False。
    """
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    result = re.match(pattern, text) is not None
    return result


def is_date(text, separator='-'):
    """
    判断字符串是否为有效日期（支持多种分隔符）。

    :param text: 输入的文本。
    :param separator: 分隔符，默认为 '-'。
    :return: 如果是有效日期返回 True，否则返回 False。
    """
    # 动态生成正则表达式
    pattern = fr'^(\d{{4}})\{separator}(\d{{2}})\{separator}(\d{{2}})$'
    match = re.match(pattern, text)
    if not match:
        return False

    # 提取年、月、日
    year, month, day = map(int, match.groups())

    # 检查月份范围
    if month < 1 or month > 12:
        return False

    # 检查日期范围
    if day < 1 or day > 31:
        return False

    # 检查月份对应的日期范围
    if month in {4, 6, 9, 11} and day > 30:  # 4月、6月、9月、11月最多30天
        return False
    if month == 2:  # 2月
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):  # 闰年
            if day > 29:
                return False
        else:  # 非闰年
            if day > 28:
                return False

    # 如果所有检查通过，返回 True
    return True


def is_color_num(text):
    """
    判断输入是否为颜色编码数字:int(0-255)。

    :param text: 输入的文本。
    :return: 如果是有效颜色编码数字返回 True，否则返回 False。
    """
    try:
        # 尝试将输入转换为整数
        num = int(text)
        # 检查是否在 0 到 255 之间
        result = 0 <= num <= 255
        return result
    except (ValueError, TypeError):
        # 如果转换失败或输入不是数字，返回 False
        return False


def is_hex_color(text):
    """
    判断输入是否为有效的十六进制颜色代码。

    :param text: 输入的文本。
    :return: 如果是有效的十六进制颜色代码返回 True，否则返回 False。
    """
    # 正则表达式匹配十六进制颜色代码
    hex_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    result = re.match(hex_pattern, text) is not None
    return result


def is_rgb_color(text):
    """
    判断输入是否为有效的 RGB 颜色格式。

    :param text: 输入的文本。
    :return: 如果是有效的 RGB 颜色格式返回 True，否则返回 False。
    """
    # 正则表达式匹配 RGB 格式
    rgb_pattern = r'^\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$'
    match = re.match(rgb_pattern, text)
    if not match:
        return False

    # 提取 R, G, B 值
    r, g, b = match.groups()

    # 检查每个值是否为 0-255 的整数
    result = is_color_num(r) and is_color_num(g) and is_color_num(b)
    return result


def is_rgba_color(text):
    """
    判断输入是否为有效的 RGBA 颜色格式（支持透明度为 0-1 或 0-255）。

    :param text: 输入的文本。
    :return: 如果是有效的 RGBA 颜色格式返回 True，否则返回 False。
    """
    # 正则表达式匹配 RGBA 格式
    rgba_pattern = r'^\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([01]?\.\d+|[01]|\d{1,3})\s*\)$'
    match = re.match(rgba_pattern, text)
    if not match:
        return False

    # 提取 R, G, B, A 值
    r, g, b, a = match.groups()

    # 检查 R, G, B 是否为 0-255 的整数
    if not (is_color_num(r) and is_color_num(g) and is_color_num(b)):
        return False

    # 检查 A 是否为 0-1 的浮点数或 0-255 的整数
    try:
        a_val = float(a)
        # 如果 A 是 0-255 的整数
        if a_val.is_integer() and 0 <= a_val <= 255:
            return True
        # 如果 A 是 0-1 的浮点数
        elif 0 <= a_val <= 1:
            return True
        else:
            return False
    except (ValueError, TypeError):
        return False


def is_color(text):
    """
    判断输入是否为有效的颜色格式（支持十六进制、RGB、RGBA）。

    :param text: 输入的文本。
    :return: 如果是有效的颜色格式返回 True，否则返回 False。
    """
    result = is_hex_color(text) or is_rgb_color(text) or is_rgba_color(text)
    return result


def is_Chinese_id_card(text, allow_lower_x=False):
    """
    判断字符串是否为有效中国身份证号。

    :param text: 输入的文本。
    :param allow_lower_x: 是否允许小写x，默认False
    :return: 如果是有效身份证号返回 True，否则返回 False。
    """
    # 正则表达式检查格式
    if allow_lower_x:
        pattern = r'^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$'
    else:
        pattern = r'^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dX]$'
    if not re.match(pattern, text):
        return False

    # 校验码验证
    factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = '10X98765432'
    try:
        total = sum(int(text[i]) * factors[i] for i in range(17))
        result = check_codes[total % 11] == text[-1].upper()
        return result
    except (ValueError, IndexError, AttributeError):
        return False


def is_Chinese_mobile_phone_number(text):
    """
    判断字符串是否为有效中国手机号。

    :param text: 输入的文本。
    :return: 如果是有效手机号返回 True，否则返回 False。
    """
    pattern = r'^1[3-9]\d{9}$'
    result = re.match(pattern, text) is not None
    return result


def is_Chinese_postal_code(text):
    """
    判断字符串是否为有效中国邮政编码。

    :param text: 输入的文本。
    :return: 如果是有效邮政编码返回 True，否则返回 False。
    """
    pattern = r'^\d{6}$'
    result = re.match(pattern, text) is not None
    return result
