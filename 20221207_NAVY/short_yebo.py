import pandas as pd
# os가 기본 library인지 확인 필요
import os
import numpy as np
import datetime
import ParsingData
import psycopg2
import psycopg2.extras as extras
import DBInsertModule
import MakeFilePath2
import subprocess

# 긴 거는 나눠서 세 번 넣기

FILL_VALUE = None

PROPERTY_PATH = '/DATA/NAVY/source/property.in'
PROPERTY = ParsingData.read_property(PROPERTY_PATH)

def connect():
    connection = psycopg2.connect(database=PROPERTY['DATABASE'],
                                  host=PROPERTY['DB_HOST'],
                                  port=PROPERTY['DB_PORT'],
                                  user=PROPERTY['DB_USER'],
                                  password=PROPERTY['DB_PW'])
    connection.autocommit = True
    return connection


def read_query(sql):
    connection = connect()
    result = pd.read_sql_query(sql, con=connection)
    return result

def get_log_sql(data_no, col_date, obs_time, pred_time):
    log_sql = f"select * from mng_data_col_log where no={data_no} and " \
                  f"data_date='{col_date}' and obs_time='{obs_time}' and pred_time='{pred_time}'"
    return log_sql

def	sshpass_fore(column_row, date, code):
		server_pw = PROPERTY['SERVER_PW']
		server = PROPERTY['SERVER']
		data_cate2 = column_row.get('data_cate2')
		data_name = column_row.get('data_name')
		date_before = date.strftime('%Y%m%d')
		date_str = datetime.datetime.strptime(date_before, "%Y%m%d")
		save_dir_path = MakeFilePath2.get_pred_save_dir_path(column_row, date_str)

		if not os.path.isdir(save_dir_path):
				subprocess.run(f'mkdir -p {save_dir_path}', shell=True)
		
		server_file_path = None
		save_file_path = None 

		if data_cate2 == "short" and data_name == 'yebo':  
				server_file_path = MakeFilePath2.get_short_yebo_remote_path(date, code) 
				save_file_path = MakeFilePath2.get_short_yebo_save_file_path(column_row, date, code)

		subpro_check = list(subprocess.getstatusoutput(f'sh /DATA/NAVY/source/status_test.sh {server_file_path} {server} {server_pw}'))
		# 대내연동수신서버에 파일이 있을 경우
		if subpro_check[1] == 'File exists':
				subprocess.run(f'sshpass -p {server_pw} scp -P 22 -o "StrictHostKeyChecking=no" -r {server}:{server_file_path} {save_dir_path}', shell=True)
		# 대내연동수신서버에 파일이 없을 경우
		elif subpro_check[1] == 'File does not exist':
				pass
		print(subpro_check[1])

		# 파일 점검하기(mng_data_col_head 테이블에서 file_size 비교)
		# 파일 사이즈가 맞으면 anal_stat = 1

		if save_file_path:
				anal_stat = check_file_size(column_row.get('no'), save_file_path, date)

		if save_file_path:
				col_stat = '1' if os.path.isfile(save_file_path) and anal_stat == '1' else '0'
		else:
				col_stat = '0'
		subprocess.run(f'sshpass -p {server_pw} ssh -o "StrictHostKeyChecking=no" {server} rm -f {server_file_path}', shell=True)
		server_remove_path = MakeFilePath2.get_server_remove_log_path(col_datetime) 
		remove_log = get_remove_log(server_file_path, save_file_path)
		write_log(server_remove_path, remove_log)
		return col_stat, server_file_path, save_file_path, subpro_check

def check_file_size(no, file_path, date):
    get_file_size_sql = f'select * from public.mng_data_col_head where no={no};'
    data_row = DBInsertModule.read_query(get_file_size_sql)
    head_file_size = int(data_row['file_size'][0])
    if os.path.isfile(file_path):
        opendap_file_size = int(os.path.getsize(file_path))
    else:
        return '0'
    return '1' if head_file_size <= opendap_file_size else '0'

def get_remove_log(server_path, save_path):
    log_list = list()
    log_list.extend(['대내연동서버 파일 경로 :', server_path, ','])
    log_list.extend(['저장 파일 경로 :', save_path])
    log_list.extend(['실행 시간 :', datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%s')])
    log_list.extend(['\n'])
    log = ' '.join(log_list)
    return log

def write_log(log_path, log):
    if not os.path.isfile(log_path):
        log_file = open(log_path, 'w')
        log_file.close()
    with open(log_path, 'a', encoding='utf-8') as log_file:   
        log_file.write(log)


# text_test2 = pd.read_csv('/DATA/recv/2021/pred/test/yebo.csv', encoding='UTF8')
# df2 = pd.DataFrame(text_test2)
# print(df2)
now_date = datetime.datetime.now()
# path_dir = '/DATA/recv/2021/pred/test/short'
# file_list = os.listdir(path_dir)
# date = now_date.strftime('%Y%m%d')
# for i in file_list:
# for j in range(183,236):
	# code = (df2['구역코드'].values)[j]
	# code = i.split('_')[2]


# code, date 수정
code = '22A30105'
data_no = 247
# date = '202207190500'
# date = '202207191100'
date = '202207191700'

	# if f'FCT_DO3_{code}_{date}1100.csv' == i:
	# 	text_test = pd.read_csv(f'/DATA/recv/2021/pred/test/short/FCT_DO3_{code}_{date}1100.csv', sep='#', encoding='CP949', header=None)

	# elif f'FCT_DO3_{code}_{date}1700.csv' == i:
	# 	text_test = pd.read_csv(f'/DATA/recv/2021/pred/test/short/FCT_DO3_{code}_{date}1700.csv', sep='#', encoding='CP949', header=None)

	# elif f'FCT_DO3_{code}_{date}0500.csv' == i:
	# 	text_test = pd.read_csv(f'/DATA/recv/2021/pred/test/short/FCT_DO3_{code}_{date}0500.csv', sep='#', encoding='CP949', header=None)

if date == '202207191100':
			text_test = pd.read_csv(f'/DATA/recv/2021/fore/test/short/FCT_DO3_{code}_202207191100.csv', sep='#', encoding='CP949', header=None)

elif date == '202207191700':
			text_test = pd.read_csv(f'/DATA/recv/2021/fore/test/short/FCT_DO3_{code}_202207191700.csv', sep='#', encoding='CP949', header=None)

elif date == '202207190500':
			text_test = pd.read_csv(f'/DATA/recv/2021/fore/test/short/FCT_DO3_{code}_202207190500.csv', sep='#', encoding='CP949', header=None)

# FCT_DO3_12B20100_202207191100.csv, FCT_DO3_22A30105_202207190500.csv, FCT_DO3_22A30104_202207191700.csv
# text_test = pd.read_csv(f'/DATA/recv/2021/pred/test/short/FCT_DO3_22A30104_202207191700.csv', sep='#', encoding='CP949', header=None)
text_test = text_test.drop(15, axis=1)
	# print(text_test[1][0])

col_date = date[0:8]
obs_time_cal = date[8:10]
if obs_time_cal == '11':
	obs_time = '11:00'
elif obs_time_cal == '17':
	obs_time = '17:00'
elif obs_time_cal == '05':
	obs_time = '05:00'
else:
	obs_time = '-'

pred_time = '00:00'
now_date = now_date

log_sql = get_log_sql(data_no, col_date, obs_time, pred_time)
col_log_row = DBInsertModule.read_query(log_sql)

get_col_head_row_sql = f"select * from mng_data_col_head where no={data_no}"
col_head_row = pd.DataFrame.to_dict(DBInsertModule.read_query(get_col_head_row_sql), orient='index')[0]

col_datetime = datetime.datetime.strptime(date, "%Y%m%d%H%M")

col_stat, server_file_path, save_file_path, subpro_check = sshpass_fore(col_head_row, col_datetime, code)

if len(col_log_row) > 0:
		# 로그가 있어도 일단 수집,
		col_cnt = str(int(col_log_row.get('col_cnt')) + 1)
		# 실패 -> 성공
		if col_stat == '1' and subpro_check[1] == 'File exists':
				sql_set = f"col_stat='{col_stat}', col_cnt='{col_cnt}', reg_date='{now_date}'"
				sql_where = log_sql.split('where')[1]
				DBInsertModule.log_db_update(sql_set, sql_where)
		# 성공 -> 실패
		elif col_stat == '1':
				sql_set = f"col_cnt='{col_cnt}'"
				sql_where = log_sql.split('where')[1]
				DBInsertModule.log_db_update(sql_set, sql_where)
		# 실패 -> 실패                  
		elif col_stat == '0':
				sql_set = f"col_stat='{col_stat}', col_cnt='{col_cnt}', now_date='{now_date}'"
				sql_where = log_sql.split('where')[1]
				DBInsertModule.log_db_update(sql_set, sql_where) 

else:
		# 로그 없음, 처음 수집
		# 수집, 로그 남기기
		col_cnt = '1'
		# 성공
		if col_stat == '1' and subpro_check[1] == 'File exists':
			log_data = tuple((data_no, col_date, obs_time, pred_time, col_stat, col_cnt, now_date))
			DBInsertModule.log_db_insert(log_data)
		# 실패
		else:
			log_data = tuple((data_no, col_date, obs_time, pred_time, col_stat, col_cnt, now_date))
			DBInsertModule.log_db_insert(log_data)


ap = list()
if len(text_test) == 5:
	for i in range(0,5):
		for j in range(0,15):
			ap.append(text_test[j][i])
elif len(text_test) == 6:
	for i in range(0,6):
		for j in range(0,15):
			ap.append(text_test[j][i])
elif len(text_test) == 7:
	for i in range(0,7):
		for j in range(0,15):
			ap.append(text_test[j][i])
	# print(ap)
	# print(ap[0:15])
	# print(ap[15:30])
	# print(ap[30:45])
	# print(ap[45:60])
	# print(ap[60:75])

def check_dbinsert(ap2, ap3, ap4, ap5):
		time_sql = f"select * from short_range_forecast where ancem_gment_num='{ap2}' and forecast_regid='{ap3}' and ancem_dtime='{ap4}' and ferment_num='{ap5}'"
		result = DBInsertModule.read_query(time_sql)
		if len(result):
				return False
		return True

flag = '0'
ancem_gment_num = list()
forecast_regid = list()
ancem_dtime = list()
ferment_num = list()
forecaster_name = list()
wdir1 = list()
wdir_code = list()
wdir2 = list()
wspeed1 = list()
wspeed2 = list()
w_height1 = list()
w_height2 = list()
weather = list()
weather_code = list()
pre_code = list()
if len(text_test) == 5:
		for i in range(0, 75, 15):
			ap2 = int(ap[i]) # ancem_gment_num
			ap3 = str(ap[i + 1]) # forecast_regid
			ap4 = str(ap[i + 2]) # ancem_dtime
			ap5 = str(ap[i + 3]) # ferment_num
			ap6 = str(ap[i + 4]) # forecaster_name
			ap7 = str(ap[i + 5]) # wdir1
			ap8 = str(ap[i + 6]) # wdir_code
			ap9 = str(ap[i + 7]) # wdir2
			ap10 = float(ap[i + 8]) # wspeed1
			ap11 = float(ap[i + 9]) # wspeed2
			ap12 = float(ap[i + 10]) # w_height1
			ap13 = float(ap[i + 11]) # w_height2
			ap14 = str(ap[i + 12]) # weather
			ap15 = str(ap[i + 13]) # weather_code
			ap16 = str(ap[i + 14]) # pre_code
			ancem_gment_num.append(ap2)
			forecast_regid.append(ap3)
			ancem_dtime.append(ap4)
			ferment_num.append(ap5)
			forecaster_name.append(ap6)
			wdir1.append(ap7)
			wdir_code.append(ap8)
			wdir2.append(ap9)
			wspeed1.append(ap10)
			wspeed2.append(ap11)
			w_height1.append(ap12)
			w_height2.append(ap13)
			weather.append(ap14)
			weather_code.append(ap15)
			pre_code.append(ap16)		
			ap32 = list()
		for pair in zip(ancem_gment_num, forecast_regid, ancem_dtime, ferment_num, forecaster_name, wdir1, wdir_code, wdir2, wspeed1, wspeed2, w_height1, w_height2, weather, weather_code, pre_code):
			if check_dbinsert(ap2, ap3, ap4, ap5):
					data_sql = f"insert into short_range_forecast (ancem_gment_num, forecast_regid, ancem_dtime, ferment_num, forecaster_name, wdir1, wdir_code, wdir2, wspeed1, wspeed2,\
									w_height1, w_height2, weather, weather_code, pre_code) values %s"
					result_sql_param = pair
					ap32.append(result_sql_param)
					flag = '1'
			else:
				continue
		if flag == '1':
			with connect() as connection:
						with connection.cursor() as cursor:
										extras.execute_values(cursor, data_sql, ap32)
						cursor.close()
			connection.close()

elif len(text_test) == 6:
		for i in range(0, 90, 15):
			ap2 = int(ap[i]) # ancem_gment_num
			ap3 = str(ap[i + 1]) # forecast_regid
			ap4 = str(ap[i + 2]) # ancem_dtime
			ap5 = str(ap[i + 3]) # ferment_num
			ap6 = str(ap[i + 4]) # forecaster_name
			ap7 = str(ap[i + 5]) # wdir1
			ap8 = str(ap[i + 6]) # wdir_code
			ap9 = str(ap[i + 7]) # wdir2
			ap10 = float(ap[i + 8]) # wspeed1
			ap11 = float(ap[i + 9]) # wspeed2
			ap12 = float(ap[i + 10]) # w_height1
			ap13 = float(ap[i + 11]) # w_height2
			ap14 = str(ap[i + 12]) # weather
			ap15 = str(ap[i + 13]) # weather_code
			ap16 = str(ap[i + 14]) # pre_code
			ancem_gment_num.append(ap2)
			forecast_regid.append(ap3)
			ancem_dtime.append(ap4)
			ferment_num.append(ap5)
			forecaster_name.append(ap6)
			wdir1.append(ap7)
			wdir_code.append(ap8)
			wdir2.append(ap9)
			wspeed1.append(ap10)
			wspeed2.append(ap11)
			w_height1.append(ap12)
			w_height2.append(ap13)
			weather.append(ap14)
			weather_code.append(ap15)
			pre_code.append(ap16)
			ap32 = list()
		for pair in zip(ancem_gment_num, forecast_regid, ancem_dtime, ferment_num, forecaster_name, wdir1, wdir_code, wdir2, wspeed1, wspeed2, w_height1, w_height2, weather, weather_code, pre_code):
			if check_dbinsert(ap2, ap3, ap4, ap5):
					data_sql = f"insert into short_range_forecast (ancem_gment_num, forecast_regid, ancem_dtime, ferment_num, forecaster_name, wdir1, wdir_code, wdir2, wspeed1, wspeed2,\
									w_height1, w_height2, weather, weather_code, pre_code) values %s"
					result_sql_param = pair
					ap32.append(result_sql_param)
					flag = '1'
			else:
				continue
		if flag == '1':
			with connect() as connection:
						with connection.cursor() as cursor:
										extras.execute_values(cursor, data_sql, ap32)
						cursor.close()
			connection.close()

elif len(text_test) == 7:
		for i in range(0, 105, 15):
			ap2 = int(ap[i]) # ancem_gment_num
			ap3 = str(ap[i + 1]) # forecast_regid
			ap4 = str(ap[i + 2]) # ancem_dtime
			ap5 = str(ap[i + 3]) # ferment_num
			ap6 = str(ap[i + 4]) # forecaster_name
			ap7 = str(ap[i + 5]) # wdir1
			ap8 = str(ap[i + 6]) # wdir_code
			ap9 = str(ap[i + 7]) # wdir2
			ap10 = float(ap[i + 8]) # wspeed1
			ap11 = float(ap[i + 9]) # wspeed2
			ap12 = float(ap[i + 10]) # w_height1
			ap13 = float(ap[i + 11]) # w_height2
			ap14 = str(ap[i + 12]) # weather
			ap15 = str(ap[i + 13]) # weather_code
			ap16 = str(ap[i + 14]) # pre_code
			ancem_gment_num.append(ap2)
			forecast_regid.append(ap3)
			ancem_dtime.append(ap4)
			ferment_num.append(ap5)
			forecaster_name.append(ap6)
			wdir1.append(ap7)
			wdir_code.append(ap8)
			wdir2.append(ap9)
			wspeed1.append(ap10)
			wspeed2.append(ap11)
			w_height1.append(ap12)
			w_height2.append(ap13)
			weather.append(ap14)
			weather_code.append(ap15)
			pre_code.append(ap16) 
			ap32 = list()
		for pair in zip(ancem_gment_num, forecast_regid, ancem_dtime, ferment_num, forecaster_name, wdir1, wdir_code, wdir2, wspeed1, wspeed2, w_height1, w_height2, weather, weather_code, pre_code):
			if check_dbinsert(ap2, ap3, ap4, ap5):
					data_sql = f"insert into short_range_forecast (ancem_gment_num, forecast_regid, ancem_dtime, ferment_num, forecaster_name, wdir1, wdir_code, wdir2, wspeed1, wspeed2,\
									w_height1, w_height2, weather, weather_code, pre_code) values %s"
					result_sql_param = pair
					ap32.append(result_sql_param)
					flag = '1'
			else:
				continue
		if flag == '1':
			with connect() as connection:
						with connection.cursor() as cursor:
										extras.execute_values(cursor, data_sql, ap32)
						cursor.close()
			connection.close()







# ap32 = list()
# for pair in zip(ancem_gment_num, forecast_regid, ancem_dtime, ferment_num, forecaster_name, wdir1, wdir_code, wdir2, wspeed1, wspeed2, w_height1, w_height2, weather, weather_code, pre_code):
# 		print(pair)
# 		data_sql = f"insert into short_range_forecast (ancem_gment_num, forecast_regid, ancem_dtime, ferment_num, forecaster_name, wdir1, wdir_code, wdir2, wspeed1, wspeed2,\
# 								w_height1, w_height2, weather, weather_code, pre_code) values %s"
# 		result_sql_param = pair
# 		ap32.append(result_sql_param)
# with connect() as connection:
# 				with connection.cursor() as cursor:
# 								extras.execute_values(cursor, data_sql, ap32)
# 				cursor.close()
# connection.close()






# 예보구역목록
# df = pd.DataFrame(text_test)
# for i in range(0,236):
# 	if list(df[1].values)[0] == list(df2['구역코드'].values)[i]:
# 		# mapping할 때
# 		df[1] = df[1].replace(df[1], df2['구역명'][i])
# 		print(df)

# 삭제하기
# for i in file_list:
#			delete = f'/DATA/recv/2021/pred/test/short/{i}'
# 		os.remove(delete)