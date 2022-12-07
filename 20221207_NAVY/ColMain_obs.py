# -*- coding: utf-8 -*-

import datetime
import pandas as pd

import DBInsertModule
import ParsingData
import PreMain
import ColManual_obs

PROPERTY_PATH = '/DATA/NAVY/source/property.in'
PROPERTY = ParsingData.read_property(PROPERTY_PATH)


def correct_col_time(time, col_head_row, col_setting_row):
    data_cate1 = col_head_row.get('data_cate1')
    data_cate2 = col_head_row.get('data_cate2')
    col_time = col_setting_row.get('col_time')
    col_cycle = int(col_setting_row.get('col_cycle'))
    if col_cycle == 1:
        return True

    # 변경(예측자료 수집하지않도록)
    elif col_cycle == 24:
        if data_cate2 == 'SATELLITE':
            col_hour = int(time.strftime("%H"))
            if col_hour >= 8 and col_hour <= 16:
                return True
            else:
                return False
        else:
            if time.strftime('%H:00') == col_time:
                return True
    else:
        col_datetime = time + datetime.timedelta(hours=col_cycle)
        return True if col_time == col_datetime.strftime('%H:00') else False
    return False


if __name__ == "__main__":
		now_time = datetime.datetime.now()
		# now_time = datetime.datetime(2022,1,17,9)

		result_list = list()
		get_head_sql = "select * from mng_data_col_head order by no;"
		col_head_row_list = DBInsertModule.read_query(get_head_sql)
		col_head_row_dict = pd.DataFrame.to_dict(col_head_row_list, orient='index')

		for column_idx in range(len(col_head_row_list)):
				process_start_time = datetime.datetime.now()
				col_head_row = col_head_row_dict.get(column_idx)
				data_cate1 = col_head_row.get('data_cate1')
				data_cate2 = col_head_row.get('data_cate2')

				if data_cate1 == 'sea':
						continue
				
				if data_cate1 == 'obs':
					now_date_cal = now_time
					now_time_cal = now_date_cal.strftime("%Y%m%d%H%M")
					now_date = datetime.datetime.strptime(now_time_cal, "%Y%m%d%H%M")
					if int(now_time_cal[10:12]) < 30:  
						date = now_date.strftime("%Y%m%d")
						time = now_date.strftime("%H")
					else:
						date = now_date.strftime("%Y%m%d")
						time = now_date.strftime("%H") + "30" # 30분으로 수정
				else:
					now_date = now_time - datetime.timedelta(hours=1)
					date = now_date.strftime("%Y%m%d")
					time = now_date.strftime("%H")					

				column_no = int(col_head_row.get('no'))
				reg_date = datetime.datetime.now()
				get_setting_sql = f"select * from mng_data_col_setting where data_cate1='{data_cate1}' and data_cate2='{data_cate2}';"
				col_setting_row_pd = DBInsertModule.read_query(get_setting_sql)
				col_setting_row = pd.DataFrame.to_dict(col_setting_row_pd, orient='index').get(0)

				# 수집 시간이 맞는지 확인
				if not correct_col_time(now_date, col_head_row, col_setting_row):
						# if 수집시간이 아니면: continue => 건너뜀
						continue

				if col_head_row.get('data_cate1') == 'obs':
						obs_time = now_date.strftime("%H") + ":00"
						pred_time = "00:00"
				else:
						obs_time = "00:00"
						pred_time = PreMain.get_model_pred_time(col_head_row, now_date)

				log_sql = ColManual_obs.get_log_sql(column_no, now_date, obs_time, pred_time)
				col_log_row = DBInsertModule.read_query(log_sql)

				if len(col_log_row) > 0:
						if int(col_log_row.get('col_cnt')) >= int(col_log_row.get('auto_col_num')):
								continue
				ColManual_obs.manual_col_main(column_no, date, time)