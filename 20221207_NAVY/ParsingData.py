# -*- coding: utf-8 -*-

"""
file path 등의 property가 저장되어 있는 파일 파싱
"""

import os
from typing import Tuple, List

def read_property(file_path):
    """
    parsing property file
    :param file_path: path to property file
    :return: property of dictionary form
    """
    with open(file_path, 'r') as pf:
        property_content = pf.read().splitlines()

    property_dict = dict()
    for content in property_content:
        label, content = content.split('=')[0], content.split('=')[1:]
        property_dict[label] = content[0].split('\t')[0]
    return property_dict


def read_tuv(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'r') as tf:
            tuv_contents = tf.read().splitlines()
        result = list()
        insert_flag = False
        for line in tuv_contents:
            if '%' in line:
                if 'TableStart' in line:
                    insert_flag = True
                    continue
                if 'TableEnd' in line:
                    break
            else:
                if insert_flag:
                    result.append(line.split())
        return result


def read_csv(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='ISO-8859-1') as fp:
            read_data = fp.readlines()[1:]
            data_list = get_parsing_csv(read_data)
        return data_list


def get_parsing_csv(data):
    data_list = list()
    for row_data in data:
        row_list = row_data.split(',')
        row_list[-1] = row_list[-1].split('\n')[0]
        data_list.append(row_list)
    return data_list
