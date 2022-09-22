# -*- coding: utf-8 -*-

import sys
import datetime
import pandas as pd

import DBInsertModule
import ParsingData
import PreMain
import ColManual

PROPERTY_PATH = '/DATA/NAVY/source/property.in'
PROPERTY = ParsingData.read_property(PROPERTY_PATH)


if __name__ == "__main__":
    date = sys.argv[1]
    time = sys.argv[2]

    result_list = list()
    get_head_sql = "select * from mng_data_col_head order by no;"
    col_head_row_list = DBInsertModule.read_query(get_head_sql)
    col_head_row_dict = pd.DataFrame.to_dict(col_head_row_list, orient='index')

    for column_idx in range(len(col_head_row_list)):
        process_start_time = datetime.datetime.now()
        col_head_row = col_head_row_dict.get(column_idx)
        column_no = col_head_row.get('no')
        data_cate1 = col_head_row.get('data_cate1')
        data_cate2 = col_head_row.get('data_cate2')

        if data_cate1 != 'obs':
            continue

        ColManual.manual_col_main(column_no, date, time)