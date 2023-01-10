"""
해군 통합해양정보체계
레이더영상, 위성영상 자료를 파싱하여 DB Insert까지 하는 모듈
2022.12.7 원태찬 작성
"""
import sys
import DBInsertModule
import pandas as pd
import os
import shutil
import datetime
import ParsingData
import psycopg2
import time
import ColManual
# PYTHON, 경로, no확인
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

def main(no, date, now_time):
		# mng_data_col_log 초기화
		no = int(no)
		obs_time2 = now_time
		log_sql = ColManual.get_log_sql(no, date, obs_time2 + ":00", "00:00")
		col_log_row = DBInsertModule.read_query(log_sql)
		print(col_log_row)
		# mng_data_col_log insert/update
		if len(col_log_row) > 0:
			pass
		else:
			data_no = no
			col_date = date
			obs_time2 = now_time + ":00"
			pred_time = "00:00"
			col_stat = '0'
			col_cnt = 1
			now_date = datetime.datetime.now()
			log_data = tuple((data_no, col_date, obs_time2, pred_time, col_stat, col_cnt, now_date))
			DBInsertModule.log_db_insert(log_data)
		
		data_path = '/data2/recv/2021/fore/png'
		# 경로 없으면 생성
		if not os.path.exists('/home/backup_navy2'):
			os.makedirs('/home/backup_navy2')

		file_name = os.listdir('/home/navy2/')
		file_name.sort() 
		ap8 = list()
		for i in file_name:
			col_stat = '0'
			ap6 = list()
			ap7 = list()
			file_name_day = i.split('_')[-1][0:8]
			file_name_time = i.split('_')[-1][8:10]
			if not os.path.exists(data_path + '/RDR' + f'/{file_name_day}'):
				os.makedirs(data_path + '/RDR' + f'/{file_name_day}')	
			if not os.path.exists(data_path + '/gk2a' + f'/{file_name_day}'):
				os.makedirs(data_path + '/gk2a' + f'/{file_name_day}')
			# RDR
			if no == 250 and i.split('_')[0] == 'RDR':
				if i.split('_')[-1][10:12] == '00':
						code_name = 'RDR'
						i2 = i.split('_')[-1][0:12]
						i3 = datetime.datetime.strptime(i2, "%Y%m%d%H%M")
						obs_time = i3.strftime("%Y-%m-%d %H:%M")
						file_name = data_path + '/' + code_name + '/' + file_name_day + '/' + i
						time1 = float(os.path.getmtime('/home/navy2/' + i))
						time2 = time.ctime(time1)
						print(time2)
						time3 = datetime.datetime.strptime(time2, "%a %b %d %H:%M:%S %Y")
						receive_time = time3.strftime("%Y-%m-%d %H:%M")
						get_st_id_count_sql = f"select count(*) from model_satel_data"
						row_count = read_query(get_st_id_count_sql)
						if row_count['count'][0] == 0:
								st_id = 1
						else:
								get_st_id_sql = f"select st_id from model_satel_data ORDER BY st_id DESC LIMIT 1"
								st_id = int(read_query(get_st_id_sql)['st_id'][0] + 1)
						ap6.append(st_id)
						ap6.append(code_name)
						ap6.append(obs_time)
						ap6.append(file_name)
						ap6.append(receive_time)
						data_sql = f"insert into model_satel_data (st_id, code_name, obs_time, file_name, receive_time) values (%s,%s,%s,%s,%s)"
						with connect() as connection:
										with connection.cursor() as cursor:
														cursor.execute(data_sql, tuple(ap6))
										cursor.close()
						connection.close()
			
						# 파일이동
						shutil.move('/home/navy2/' + i, data_path + f'/{code_name}' + f'/{file_name_day}/' + i)
						file_sort = os.listdir(f'{data_path}/{code_name}/{file_name_day}')
						col_stat = '1'
						ap8.append(col_stat)
					
						# mng_data_col_log 적재
						obs_time2 = file_name_time
						log_sql = ColManual.get_log_sql(no, file_name_day, obs_time2 + ":00", "00:00")
						col_log_row = DBInsertModule.read_query(log_sql)
						print(col_stat)
						# mng_data_col_log insert/update
						if len(col_log_row) > 0:
							# 로그가 있어도 일단 수집,
							col_cnt = str(int(col_log_row.get('col_cnt')) + 1)
							now_date = datetime.datetime.now()
							sql_set = f"col_stat='{col_stat}', col_cnt='{col_cnt}', reg_date='{now_date}'"
							sql_where = log_sql.split('where')[1]
							DBInsertModule.log_db_update(sql_set, sql_where)												
						else:		
							data_no = no
							col_date = file_name_day
							obs_time2 = file_name_time + ":00"
							pred_time = "00:00"
							col_cnt = 1
							now_date = datetime.datetime.now()
							log_data = tuple((data_no, col_date, obs_time2, pred_time, col_stat, col_cnt, now_date))
							DBInsertModule.log_db_insert(log_data)
       
				# 00분이 아니면
				else:
					shutil.move('/home/navy2/' + i, '/home/backup_navy2/' + i)
					os.remove('/home/backup_navy2/' + i)
			# gk2a
			elif no == 251 and i.split('_')[0] == 'gk2a':
				if i.split('_')[-1][10:12] == '00':
					code_name = 'gk2a'
					i2 = i.split('_')[-1][0:12]
					i3 = datetime.datetime.strptime(i2, "%Y%m%d%H%M")
					obs_time = i3.strftime("%Y-%m-%d %H:%M")
					file_name = data_path + '/' + code_name + '/' + file_name_day + '/' + i
					time1 = float(os.path.getmtime('/home/navy2/' + i))
					time2 = time.ctime(time1)
					print(time2)
					time3 = datetime.datetime.strptime(time2, "%a %b %d %H:%M:%S %Y")
					receive_time = time3.strftime("%Y-%m-%d %H:%M")
					get_st_id_count_sql = f"select count(*) from model_satel_data"
					row_count = read_query(get_st_id_count_sql)
					if row_count['count'][0] == 0:
							st_id = 1
					else:
							get_st_id_sql = f"select st_id from model_satel_data ORDER BY st_id DESC LIMIT 1"
							st_id = int(read_query(get_st_id_sql)['st_id'][0] + 1)
					ap7.append(st_id)
					ap7.append(code_name)
					ap7.append(obs_time)
					ap7.append(file_name)
					ap7.append(receive_time)

					data_sql = f"insert into model_satel_data (st_id, code_name, obs_time, file_name, receive_time) values (%s,%s,%s,%s,%s)"
					with connect() as connection:
									with connection.cursor() as cursor:
													cursor.execute(data_sql, tuple(ap7))
									cursor.close()
					connection.close()

					# 파일이동
					shutil.move('/home/navy2/' + i, data_path + f'/{code_name}' + f'/{file_name_day}/' + i)
					col_stat = '1'
					ap8.append(col_stat)
					file_sort = os.listdir(f'{data_path}/{code_name}/{file_name_day}')

					# mng_data_col_log 적재
					obs_time2 = file_name_time
					log_sql = ColManual.get_log_sql(no, file_name_day, obs_time2 + ":00", "00:00")
					col_log_row = DBInsertModule.read_query(log_sql)
					print(col_stat)
					# mng_data_col_log insert/update
					if len(col_log_row) > 0:
						# 로그가 있어도 일단 수집,
						col_cnt = str(int(col_log_row.get('col_cnt')) + 1)
						now_date = datetime.datetime.now()
						sql_set = f"col_stat='{col_stat}', col_cnt='{col_cnt}', reg_date='{now_date}'"
						sql_where = log_sql.split('where')[1]
						DBInsertModule.log_db_update(sql_set, sql_where)												
					else:		
						data_no = no
						col_date = file_name_day
						obs_time2 = file_name_time + ":00"
						pred_time = "00:00"
						col_cnt = 1
						now_date = datetime.datetime.now()
						log_data = tuple((data_no, col_date, obs_time2, pred_time, col_stat, col_cnt, now_date))
						DBInsertModule.log_db_insert(log_data)

				# 00분이 아니면
				else:
					shutil.move('/home/navy2/' + i, '/home/backup_navy2/' + i)
					os.remove('/home/backup_navy2/' + i)
if __name__ == "__main__":
		no = sys.argv[1]
		date = sys.argv[2]
		now_time = sys.argv[3]
		main(no, date, now_time)