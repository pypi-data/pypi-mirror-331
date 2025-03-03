# -*- coding: utf-8 -*-
#
# Auto created by: auto_generate_init.py
#
"""
Project Name: zyt_validation_utils
File Created: 2025.01.22
Author: ZhangYuetao
File Name: __init__.py
Update: 2025.03.03
"""

# 导入 data_check 模块中的函数
from .data_check import (
    is_type,
    is_all_unique,
    is_empty,
    is_numeric,
    is_can_to_int,
    is_can_to_numeric,
    is_designated_nums,
    is_nums_in_range,
    is_valid_key,
)

# 导入 dir_check 模块中的函数
from .dir_check import (
    is_dir,
    is_dir_empty,
    is_have_subdirectories,
    is_have_non_subdirectory_files,
)

# 导入 file_check 模块中的函数
from .file_check import (
    is_file,
    is_empty_file,
    is_image,
    is_image_complete,
    is_video,
    is_audio,
    is_archive,
    is_bin,
    is_current_file_frozen,
    is_file_load_complete,
    is_rgb_image,
    is_gray_image,
    is_depth_image,
    is_rgb_video,
)

# 导入 text_check 模块中的函数
from .text_check import (
    is_have_chinese,
    is_all_chinese,
    is_have_english,
    is_all_english,
    is_have_digit,
    is_all_digit,
    is_have_special_char,
    is_all_special_char,
    is_have_normal_space,
    is_have_any_space,
    is_have,
    is_email,
    is_url,
    is_ipv4_address,
    is_ipv6_address,
    is_ip_address,
    is_mac_address,
    is_date,
    is_color_num,
    is_hex_color,
    is_rgb_color,
    is_rgba_color,
    is_color,
    is_Chinese_id_card,
    is_Chinese_mobile_phone_number,
    is_Chinese_postal_code,
)


# 定义包的公共接口
__all__ = [

    # data_check
    'is_type',
    'is_all_unique',
    'is_empty',
    'is_numeric',
    'is_can_to_int',
    'is_can_to_numeric',
    'is_designated_nums',
    'is_nums_in_range',
    'is_valid_key',

    # dir_check
    'is_dir',
    'is_dir_empty',
    'is_have_subdirectories',
    'is_have_non_subdirectory_files',

    # file_check
    'is_file',
    'is_empty_file',
    'is_image',
    'is_image_complete',
    'is_video',
    'is_audio',
    'is_archive',
    'is_bin',
    'is_current_file_frozen',
    'is_file_load_complete',
    'is_rgb_image',
    'is_gray_image',
    'is_depth_image',
    'is_rgb_video',

    # text_check
    'is_have_chinese',
    'is_all_chinese',
    'is_have_english',
    'is_all_english',
    'is_have_digit',
    'is_all_digit',
    'is_have_special_char',
    'is_all_special_char',
    'is_have_normal_space',
    'is_have_any_space',
    'is_have',
    'is_email',
    'is_url',
    'is_ipv4_address',
    'is_ipv6_address',
    'is_ip_address',
    'is_mac_address',
    'is_date',
    'is_color_num',
    'is_hex_color',
    'is_rgb_color',
    'is_rgba_color',
    'is_color',
    'is_Chinese_id_card',
    'is_Chinese_mobile_phone_number',
    'is_Chinese_postal_code',

]
