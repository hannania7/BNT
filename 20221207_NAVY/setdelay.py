import datetime
import DBInsertModule

# 해군에 가서는 7일 예측자료 no 변경필요

col_stat = '2'
# 자동
now_date = datetime.datetime.now()
str_date = now_date.strftime('%Y%m%d')
str_date_year = str_date[0:4]
str_date_month = str_date[4:6]
str_date_day = str_date[6:8]

# 수동
# now_date = '20220608'
# now_date2 = datetime.datetime.strptime(now_date, "%Y%m%d")
# str_date = now_date2.strftime("%Y%m%d")

# mohid300m
log_data = tuple((102, str_date, '00:00', '09:00', col_stat, '0', '9999-01-01 00:00:00.000'))
DBInsertModule.log_db_insert(log_data)
# yes3k
log_data = tuple((103, str_date, '00:00', '09:00', col_stat, '0', '9999-01-01 00:00:00.000'))
DBInsertModule.log_db_insert(log_data)
# wrfdm1
log_data = tuple((104, str_date, '00:00', '09:00', col_stat, '0', '9999-01-01 00:00:00.000'))
DBInsertModule.log_db_insert(log_data)
# ww3
log_data = tuple((105, str_date, '00:00', '09:00', col_stat, '0', '9999-01-01 00:00:00.000'))
DBInsertModule.log_db_insert(log_data)
# mid
log_data = tuple((191, str_date, '00:00', '09:00', col_stat, '0', '9999-01-01 00:00:00.000'))
DBInsertModule.log_db_insert(log_data)
# TCSMap
log_data = tuple((242, str_date, '00:00', '21:00', col_stat, '0', '9999-01-01 00:00:00.000'))
DBInsertModule.log_db_insert(log_data)

# # yes3k_7D
# log_data = tuple((244, str_date, '00:00', '09:00', col_stat, '0', '9999-01-01 00:00:00.000'))
# DBInsertModule.log_db_insert(log_data)
# # wrfdm1_7D
# log_data = tuple((245, str_date, '00:00', '09:00', col_stat, '0', '9999-01-01 00:00:00.000'))
# DBInsertModule.log_db_insert(log_data)

