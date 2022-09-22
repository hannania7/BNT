# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
import datetime
import subprocess

import DBInsertModule
import MakeFilePath
import ParsingData

PROPERTY_PATH = '/DATA/NAVY/source/property.in'
PROPERTY = ParsingData.read_property(PROPERTY_PATH)


def remove_obs(column_row, date):
    save_dir_path = column_row.get('data_path')
    remove_file_path = MakeFilePath.get_obs_save_file_path(col_head_row, date, save_dir_path)
    if os.path.isfile(remove_file_path):
        os.remove(remove_file_path)


def remove_pred(column_row, date):
    data_cate2 = column_row.get('data_cate2')
    data_name = column_row.get('data_name')
    save_dir_path = MakeFilePath.get_pred_save_dir_path(column_row, date)
    remove_flag = False
    if data_cate2 == 'MOHID300M':
        remove_file_path = MakeFilePath.get_mohid300_save_file_path(column_row, date)

    elif data_cate2 == "YES3K":
        remove_file_path = MakeFilePath.get_yes3k_save_file_path(column_row, date)

    elif data_cate2 == "WRF":
        remove_file_path = MakeFilePath.get_wrf_save_file_path(column_row, date)

    elif data_cate2 == "WW3":
        remove_file_path = MakeFilePath.get_ww3_save_file_path(column_row, date)

    elif data_cate2 == 'SATELLITE':
        remove_flag = True
        if data_name == "RGB":
            remove_dir_path = MakeFilePath.get_pred_save_dir_path(column_row, date)
        elif data_name == "DETECT":
            remove_file_path = ''

    elif data_cate2 == 'sf':
        remove_file_path = MakeFilePath.get_sf_save_file_path(column_row, date)

    elif data_cate2 == "MID":
        remove_file_path = MakeFilePath.get_mid_save_path(column_row, date)

    if not remove_flag:
        if os.path.isfile(remove_file_path):
            os.remove(remove_file_path)


def remove_anal(column_row, date):
    remove_file_path = ''
    data_cate2 = column_row.get('data_cate2')
    if data_cate2 == 'MOHID300M':
        remove_file_path = MakeFilePath.get_anal_vis_save_file_path(column_row, date)
    elif data_cate2 == "YES3K":
        remove_file_path = MakeFilePath.get_anal_yes3k_save_file_path(column_row, date)

    if remove_file_path:
        if os.path.isfile(remove_file_path):
            os.remove(remove_file_path)


if __name__ == "__main__":
    now_time = datetime.datetime.now()

    date = now_time.strftime("%Y%m%d")
    time = now_time.strftime("%H")
    result_list = list()

    get_head_sql = "select * from mng_data_col_head order by no;"
    col_head_row_list = DBInsertModule.read_query(get_head_sql)
    col_head_row_dict = pd.DataFrame.to_dict(col_head_row_list, orient='index')

    for column_idx in range(len(col_head_row_list)):
        process_start_time = datetime.datetime.now()
        col_head_row = col_head_row_dict.get(column_idx)
        data_cate1 = col_head_row.get('data_cate1')
        data_cate2 = col_head_row.get('data_cate2')

        get_setting_row_sql = f"select * from mng_data_col_setting where data_cate1='{data_cate1}' and data_cate2='{data_cate2}';"
        setting_row_list = DBInsertModule.read_query(get_setting_row_sql)
        setting_row = pd.DataFrame.to_dict(setting_row_list, orient='index')[0]
        del_cycle = int(setting_row.get('auto_del_cycle'))
        del_datetime = now_time - datetime.timedelta(days=del_cycle)

        save_folder_path = col_head_row.get('data_path')

        if data_cate1 == 'obs':
            remove_obs(col_head_row, del_datetime)
        elif data_cate1 == 'pred':
            remove_pred(col_head_row, del_datetime)
        elif data_cate1 == 'anal':
            remove_anal(col_head_row, del_datetime)
        elif data_cate1 == 'sea':
            continue