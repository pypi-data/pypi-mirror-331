# -*- coding: utf-8 -*-
"""
Project Name: zyt_validation_utils
File Created: 2025.01.17
Author: ZhangYuetao
File Name: data_check.py
Update: 2025.02.08
"""


def is_type(target_type, *datas):
    """
    检测所有数据是否都属于指定类型

    :param target_type: 目标类型（如 str, int, list 等）
    :param datas: 不定数量的待检测数据
    :return: 如果所有数据都属于目标类型，返回 True；否则返回 False
    """
    result = all(isinstance(data, target_type) for data in datas)
    return result


def is_all_unique(data):
    """
    检测所有列表或元组中是否有重复元素

    :param data: 列表或元组
    :return: 如果有重复元素，返回 True；否则返回 False
    """
    # 检查输入是否为列表或元组
    if not isinstance(data, (list, tuple)):
        raise TypeError("输入必须是列表或元组")

    seen = set()  # 用于存储已经见过的元素
    for item in data:
        if item in seen:  # 如果元素已经存在于集合中，说明有重复
            return False
        seen.add(item)  # 将当前元素添加到集合中
    return True  # 遍历完成后没有发现重复


def is_empty(*datas):
    """
    检测所有数据是否为空值。

    支持以下空值：
    - None
    - 空字符串 ("")
    - 空列表 ([])
    - 空字典 ({})
    - 空元组 (())
    - 空集合 (set())

    :param datas: 输入的数据。
    :return: 如果所有数据都为空值返回 True，否则返回 False。
    """
    for data in datas:
        # 检查是否为 None
        if data is None:
            continue
        # 检查是否为空容器
        if isinstance(data, (str, list, dict, set, tuple)):
            if len(data) != 0:
                return False
        else:
            # 其他情况不为空
            return False
    return True


def is_numeric(*datas):
    """
    检测所有数据是否为数值类型。

    :param datas: 输入的数据。
    :return: 如果所有数据都是数值类型返回 True，否则返回 False。
    """
    result = all(isinstance(data, (int, float)) for data in datas)
    return result


def is_can_to_int(*datas):
    """
    检测所有数据是否都可以转换为整数

    :param datas: 不定数量的待检测数据
    :return: 如果所有数据都可以转换为整数，返回 True；否则返回 False
    """
    for data in datas:
        try:
            int(data)
        except (ValueError, TypeError):
            return False
    return True


def is_can_to_numeric(*datas):
    """
    检测所有数据是否都可以转换为数值（整数或浮点数）

    :param datas: 不定数量的待检测数据
    :return: 如果所有数据都可以转换为数值，返回 True；否则返回 False
    """
    for data in datas:
        try:
            float(data)
        except (ValueError, TypeError):
            return False
    return True


def is_designated_nums(num_type, *datas, must_int=False):
    """
    检测所有数据是否为指定类型数值。

    :param num_type: 指定的类型（如 "odd", "even", "positive", "no_negative", "negative", "no_positive" 等）。
    :param datas: 输入的数据。
    :param must_int: 必须为整数，默认为False
    :return: 如果所有数据都是指定类型数值返回 True，否则返回 False。
    """
    # 如果 must_int为True，则检查数据是否为整数
    if must_int:
        if not is_type(int, *datas):
            return False
    else:
        # 否则检查数据是否为数值类型（整数或浮点数）
        if not is_numeric(*datas):
            return False

    # 根据指定的类型进行判断
    if 'odd' in num_type:
        result = all(data % 2 != 0 for data in datas)
    elif 'even' in num_type:
        result = all(data % 2 == 0 for data in datas)
    elif 'positive' in num_type:
        result = all(data > 0 for data in datas)
    elif 'no_negative' in num_type:
        result = all(data >= 0 for data in datas)
    elif 'negative' in num_type:
        result = all(data < 0 for data in datas)
    elif 'no_positive' in num_type:
        result = all(data <= 0 for data in datas)
    else:
        raise ValueError(f"不支持的指定类型: {num_type}")
    return result


def is_nums_in_range(range_str, *datas, must_int=False):
    """
    检测所有数据是否在指定范围内。

    :param range_str: 数据范围字符串，格式为 "(a, b)", "[a, b]", "(a, ]", "[a, )", "(, b)", "[, b]" 等。
    :param datas: 输入的数据。
    :param must_int: 必须为整数，默认为False
    :return: 如果所有数据都在指定范围内返回 True，否则返回 False。
    """
    # 如果 must_int为True，则检查数据是否为整数
    if must_int:
        if not is_type(int, *datas):
            return False
    else:
        # 否则检查数据是否为数值类型（整数或浮点数）
        if not is_numeric(*datas):
            return False

    # 解析范围字符串
    range_str = range_str.strip()
    if not (range_str.startswith(('(', '[')) and range_str.endswith((')', ']'))):
        raise ValueError("范围格式错误，必须以 '(' 或 '[' 开头，以 ')' 或 ']' 结尾。")

    # 提取上下限
    parts = range_str[1:-1].split(',')
    if len(parts) != 2:
        raise ValueError("范围格式错误，必须包含两个部分，用逗号分隔。")

    lower_bound, upper_bound = parts[0].strip(), parts[1].strip()

    # 解析下限
    if lower_bound == '':
        lower = float('-inf')  # 无下限
        include_lower = False
    else:
        try:
            lower = float(lower_bound)  # 尝试将下限转换为浮点数
        except ValueError:
            raise ValueError(f"下限 '{lower_bound}' 不是有效的数字。")
        include_lower = range_str.startswith('[')  # 是否包含等于

    # 解析上限
    if upper_bound == '':
        upper = float('inf')  # 无上限
        include_upper = False
    else:
        try:
            upper = float(upper_bound)  # 尝试将上限转换为浮点数
        except ValueError:
            raise ValueError(f"上限 '{upper_bound}' 不是有效的数字。")
        include_upper = range_str.endswith(']')  # 是否包含等于

    # 检查所有数据是否在范围内
    for data in datas:
        if not isinstance(data, (int, float)):
            return False  # 非数值类型直接返回 False

        # 检查下限
        if include_lower:
            if data < lower:
                return False
        else:
            if data <= lower:
                return False

        # 检查上限
        if include_upper:
            if data > upper:
                return False
        else:
            if data >= upper:
                return False

    return True


def is_valid_key(dictionary, *datas):
    """
    检测所有数据是否为字典的有效键。

    :param datas: 输入的数据。
    :param dictionary: 目标字典。
    :return: 如果所有数据都是字典的有效键，返回 True；否则返回 False。
    """
    result = all(data in dictionary for data in datas)
    return result
