import pandas as pd
import os
import numpy as np
import datetime
import ParsingData
import psycopg2
import psycopg2.extras as extras
import DBInsertModule
import MakeFilePath2
import subprocess

# 긴 거는 나눠서 두 번 넣기

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

def check_dbinsert(ap1, ap2):
		time_sql = f"select * from model_middle_yebo_dataset where yebo_code='{ap1}' and announce_time='{ap2}'"
		result = DBInsertModule.read_query(time_sql)
		if len(result):
				return False
		return True

def check_selection(code, date):
		time_sql = f"select * from model_middle_yebo_dataset where yebo_code='{code}' and announce_time='{date}'"
		result = DBInsertModule.read_query(time_sql)
		if len(result):
				return False
		return True

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

		if data_cate2 == "middle" and data_name == 'yebo': 
				server_file_path = MakeFilePath2.get_middle_yebo_remote_path(date, code)
				save_file_path = MakeFilePath2.get_middle_yebo_save_file_path(column_row, date, code)

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

def check_file_size(no, file_path, date):
    get_file_size_sql = f'select * from public.mng_data_col_head where no={no};'
    data_row = DBInsertModule.read_query(get_file_size_sql)
    head_file_size = int(data_row['file_size'][0])
    if os.path.isfile(file_path):
        opendap_file_size = int(os.path.getsize(file_path))
    else:
        return '0'
    return '1' if head_file_size <= opendap_file_size else '0'


text_test2 = pd.read_csv('/DATA/recv/2021/fore/test/yebo2.csv')
df2 = pd.DataFrame(text_test2)
now_date = datetime.datetime.now()
date = now_date.strftime('%Y%m%d')

# for i in range(0, 236):
# 		code = df2['지역코드'][i]
# 		print(code)
		# if f'FCT_WO6_{code}_{date}0600.csv' == i:
		# 	text_test = pd.read_csv(f'/DATA/recv/2021/fore/test/mid/{i}', sep='#', encoding='CP949', header=None)

		# elif f'FCT_WO6_{code}_{date}1800.csv' == i:
		# 	text_test = pd.read_csv(f'/DATA/recv/2021/fore/test/mid/{i}', sep='#', encoding='CP949', header=None)

# code 수정
code = '12G00000'
data_no = 248	
get_col_head_row_sql = f"select * from mng_data_col_head where no={data_no}"
col_head_row = pd.DataFrame.to_dict(DBInsertModule.read_query(get_col_head_row_sql), orient='index')[0]
col_stat = '0'
date2 = '202207190000'
if check_selection(code, '202207190600'):
		date2 = '202207190600'
		col_datetime = datetime.datetime.strptime(date2, "%Y%m%d%H%M")
		col_stat, server_file_path, save_file_path, subpro_check = sshpass_fore(col_head_row, col_datetime, code)
		if subpro_check[1] == 'File exists':
			text_test = pd.read_csv(f"/DATA/recv/2021/fore/test/20220719/FCT_WO6_{code}_202207190600.csv", sep='#', encoding='CP949', header=None)
elif check_selection(code, '202207191800'):
		date2 = '202207191800'
		col_datetime = datetime.datetime.strptime(date2, "%Y%m%d%H%M")
		col_stat, server_file_path, save_file_path, subpro_check = sshpass_fore(col_head_row, col_datetime, code)
		if subpro_check[1] == 'File exists':
			text_test = pd.read_csv(f"/DATA/recv/2021/fore/test/20220719/FCT_WO6_{code}_202207191800.csv", sep='#', encoding='CP949', header=None)

col_date = date2[0:8]
obs_time_cal = date2[8:10]
if obs_time_cal == '06':
	obs_time = '06:00'
elif obs_time_cal == '18':
	obs_time = '18:00'
else:
	obs_time = '-'

pred_time = '00:00'
now_date = now_date

log_sql = get_log_sql(data_no, col_date, obs_time, pred_time)
col_log_row = DBInsertModule.read_query(log_sql)

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
		# 중기예보문
		# FCT_WO6_12A10000_202207190600.csv, FCT_WO6_12A10000_202207191800.csv
# filepath = os.path.basename('/DATA/recv/2021/fore/test/mid/FCT_WO6_12A10000_202207191800.csv')
# filepath_sepa = filepath.split('_')[3][9]

# 파일명 수정
filepath_sepa =f"/DATA/recv/2021/fore/test/20220719/FCT_WO6_{code}_202207191800.csv".split('_')[3][9]

		# text_test2 = os.path.basename(f'/DATA/recv/2021/fore/test/mid/{i}')
		# filepath_sepa = date2[9]
		# print(filepath_sepa)
flag = '0'
if filepath_sepa == '6':
			text_test = pd.read_csv(f'/DATA/recv/2021/fore/test/mid/FCT_WO6_{code}_202207190600.csv', sep='#', encoding='CP949', header=None)
			# text_test3 = text_test.drop(107, axis=1)
			# text_test4 = text_test3.drop(108, axis=1)
			ap1 = list()
			print(text_test)
			for i in range(0, 108):
				if str(type(text_test[i][0])) == "<class 'numpy.int64'>":
					ap2 = int(text_test[i][0])
				elif str(type(text_test[i][0])) == "<class 'numpy.float64'>":
					ap2 = 'nan'
				else:
					ap2 = text_test[i][0]
				ap1.append(ap2)

			for i in range(9, 109, 8):
				ap1[i] = float(ap1[i])
			for i in range(10, 109, 8):
				ap1[i] = float(ap1[i])
			print(ap1)

			get_st_id_count_sql = f"select count(*) from model_middle_yebo_data"
			row_count = read_query(get_st_id_count_sql)
			if row_count['count'][0] == 0:
					st_id = 1
			else:
					get_st_id_sql = f"select st_id from model_middle_yebo_data ORDER BY st_id DESC LIMIT 1"
					st_id = int(read_query(get_st_id_sql)['st_id'][0] + 1)

			ap3 = list()
			ap4 = list()
			ap5 = list()
			ap6 = list()
			ap7 = list()
			ap8 = list()
			ap9 = list()
			ap10 = list()
			ap11 = list()
			ap11 = [st_id] * 13 # st_id
			for i in range(4, 108, 8):
				ap3.append(ap1[i]) # separate_time
				ap4.append(ap1[i+1]) # time_section
				ap5.append(ap1[i+2]) # weather
				ap6.append(ap1[i+3]) # weather_code
				ap7.append(ap1[i+4]) # separate_rain
				ap8.append(ap1[i+5]) # wave_height1
				ap9.append(ap1[i+6]) # wave_height2
				ap10.append(ap1[i+7]) # confidence
			for pair in zip(ap11, ap3, ap4, ap5, ap6, ap7, ap8, ap9, ap10):
					data_value_set = "(st_id, separate_time, time_section, weather, weather_code, separate_rain, wave_height1, wave_height2, confidence)"					
					data_sql = f"insert into model_middle_yebo_data {data_value_set} values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
					with connect() as connection:
							with connection.cursor() as cursor:
									cursor.execute(data_sql, tuple(pair))
							cursor.close()
					connection.close()

			ap12 = list()
			ap12.append(st_id)
			for i in range(0, 4):
					ap12.append(ap1[i]) # dataset
					
			data_value_set = "(st_id, announce_no, yebo_code, announce_time, yebo_name)"					
			data_sql = f"insert into model_middle_yebo_dataset {data_value_set} values (%s, %s, %s, %s, %s)"
			with connect() as connection:
					with connection.cursor() as cursor:
							cursor.execute(data_sql, tuple(ap12))
					cursor.close()
			connection.close()
			


elif filepath_sepa == '8':
			text_test = pd.read_csv(f'/DATA/recv/2021/fore/test/mid/FCT_WO6_{code}_202207191800.csv', sep='#', encoding='CP949', header=None)
			# text_test3 = text_test.drop(107, axis=1)
			# text_test4 = text_test3.drop(108, axis=1)
			ap1 = list()
			print(text_test)
			for i in range(0, 4):
				if str(type(text_test[i][0])) == "<class 'numpy.int64'>":
					ap2 = int(text_test[i][0])
				elif str(type(text_test[i][0])) == "<class 'numpy.float64'>":
					ap2 = 'nan'
				else:
					ap2 = text_test[i][0]
				ap1.append(ap2)
			for i in range(4, 92):
				if str(type(text_test[i][0])) == "<class 'numpy.int64'>":
					ap2 = int(text_test[i][0])
				elif str(type(text_test[i][0])) == "<class 'numpy.float64'>":
					ap2 = 'nan'
				else:
					ap2 = text_test[i][0]
				ap1.append(ap2)

			for i in range(9, 92, 8):
				ap1[i] = float(ap1[i])
			for i in range(10, 92, 8):
				ap1[i] = float(ap1[i])

			get_st_id_count_sql = f"select count(*) from model_middle_yebo_data"
			row_count = read_query(get_st_id_count_sql)
			if row_count['count'][0] == 0:
					st_id = 1
			else:
					get_st_id_sql = f"select st_id from model_middle_yebo_data ORDER BY st_id DESC LIMIT 1"
					st_id = read_query(get_st_id_sql)['st_id'][0] + 1

			ap3 = list()
			ap4 = list()
			ap5 = list()
			ap6 = list()
			ap7 = list()
			ap8 = list()
			ap9 = list()
			ap10 = list()
			ap11 = list()
			ap11 = [st_id] * 11 # st_id
			for i in range(4, 92, 8):
				ap3.append(ap1[i]) # separate_time
				ap4.append(ap1[i+1]) # time_section
				ap5.append(ap1[i+2]) # weather
				ap6.append(ap1[i+3]) # weather_code
				ap7.append(ap1[i+4]) # separate_rain
				ap8.append(ap1[i+5]) # wave_height1
				ap9.append(ap1[i+6]) # wave_height2
				ap10.append(ap1[i+7]) # confidence
			for pair in zip(ap11, ap3, ap4, ap5, ap6, ap7, ap8, ap9, ap10):
					data_value_set = "(st_id, separate_time, time_section, weather, weather_code, separate_rain, wave_height1, wave_height2, confidence)"					
					data_sql = f"insert into model_middle_yebo_data {data_value_set} values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
					with connect() as connection:
							with connection.cursor() as cursor:
									cursor.execute(data_sql, tuple(pair))
							cursor.close()
					connection.close()

			ap12 = list()
			ap12.append(st_id)
			for i in range(0, 4):
				ap12.append(ap1[i]) # dataset
					
			data_value_set = "(st_id, announce_no, yebo_code, announce_time, yebo_name)"					
			data_sql = f"insert into model_middle_yebo_dataset {data_value_set} values (%s, %s, %s, %s, %s)"
			with connect() as connection:
					with connection.cursor() as cursor:
							cursor.execute(data_sql, tuple(ap12))
					cursor.close()
			connection.close()







# # 예보구역목록
# text_test2 = pd.read_csv('/DATA/recv/2021/pred/test/yebo.csv', encoding='UTF8')
# df = pd.DataFrame(text_test)
# df2 = pd.DataFrame(text_test2)
# for i in range(0,236):
# 	if list(df[1].values)[0] == list(df2['구역코드'].values)[i]:
# 		# mapping할 때
# 		df[1] = df[1].replace(df[1], df2['구역명'][i])
# 		print(df)



# 삭제하기
# for i in file_list:
#			delete = f'/DATA/recv/2021/pred/test/mid/{i}'
# 		os.remove(delete)

