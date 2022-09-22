import datetime
import DBInsertModule
import pandas as pd

# 해군에 가서는 7일 예측자료 no 변경필요

def get_log_sql(no, now_day):
		log_sql2 = f"select col_stat from mng_data_col_log where " \
									f"no='{no}' and data_date='{now_day}'"
		return log_sql2


# 자동
now_date = datetime.datetime.now()
now_day = now_date.strftime("%Y%m%d")

# 수동
# now_date = '20220608'
# now_date2 = datetime.datetime.strptime(now_date, "%Y%m%d")
# now_day = now_date2.strftime("%Y%m%d")


log_sql = f"select * from mng_data_col_log order by reg_date desc"
col_log_row = DBInsertModule.read_query(log_sql)
for no in ['102','103','104','105','191','242','244','245']:
# for no in ['103','104','105','191','242']:
		log_sql2 = get_log_sql(no, now_day)
		col_log_row = DBInsertModule.read_query(log_sql2)
		col_log_row_t = col_log_row.T
		# if now_datetime >= trans_date:
		if col_log_row_t[0].values == '1':
				col_stat = '1'
		elif col_log_row_t[0].values == '3':
				col_stat = '0'
		else: 
				continue
		# print(col_stat)
		sql_set = f"col_stat='{col_stat}'"
		sql_where = log_sql2.split('where')[1]
		DBInsertModule.log_db_update(sql_set, sql_where)
