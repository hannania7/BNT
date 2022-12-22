import os
import sys
import math
import datetime

import numpy as np
import pandas as pd
import ParsingData
import psycopg2
import json

# PYTHON, 주석확인
FILL_VALUE = 999999999
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

file_name = os.listdir('/DATA/recv/2021/obs/tw/')
zeta_data_append0 = list()
temp_data_append0 = list()
salt_data_append0 = list()
zeta_data_append1 = list()
temp_data_append1 = list()
salt_data_append1 = list()
zeta_data_append2 = list()
temp_data_append2 = list()
salt_data_append2 = list()
zeta_data_append3 = list()
temp_data_append3 = list()
salt_data_append3 = list()
zeta_data_append4 = list()
temp_data_append4 = list()
salt_data_append4 = list()
zeta_data_append5 = list()
temp_data_append5 = list()
salt_data_append5 = list()
zeta_data_append6 = list()
temp_data_append6 = list()
salt_data_append6 = list()
zeta_data_append7 = list()
temp_data_append7 = list()
salt_data_append7 = list()
zeta_data_append8 = list()
temp_data_append8 = list()
salt_data_append8 = list()
zeta_data_append9 = list()
temp_data_append9 = list()
salt_data_append9 = list()
zeta_data_append10 = list()
temp_data_append10 = list()
salt_data_append10 = list()
zeta_data_append11 = list()
temp_data_append11 = list()
salt_data_append11 = list()
zeta_data_append12 = list()
temp_data_append12 = list()
salt_data_append12 = list()
zeta_data_append13 = list()
temp_data_append13 = list()
salt_data_append13 = list()
zeta_data_append14 = list()
temp_data_append14 = list()
salt_data_append14 = list()
zeta_data_append15 = list()
temp_data_append15 = list()
salt_data_append15 = list()
zeta_data_append16 = list()
temp_data_append16 = list()
salt_data_append16 = list()
zeta_data_append17 = list()
temp_data_append17 = list()
salt_data_append17 = list()
zeta_data_append18 = list()
temp_data_append18 = list()
salt_data_append18 = list()
zeta_data_append19 = list()
temp_data_append19 = list()
salt_data_append19 = list()
zeta_data_append20 = list()
temp_data_append20 = list()
salt_data_append20 = list()
zeta_data_append21 = list()
temp_data_append21 = list()
salt_data_append21 = list()
zeta_data_append22 = list()
temp_data_append22 = list()
salt_data_append22 = list()
zeta_data_append23 = list()
temp_data_append23 = list()
salt_data_append23 = list()
for i in file_name:
	if i[-12:-4] == '20210602':
		print(i[0:-12])
		check_sql = f"select * from station where obs_post_id = '{i[0:-12]}';"
		check_result = read_query(check_sql)
		obs_post_id = check_result['obs_post_id'][0]
		# print(obs_post_id)
		name = check_result['name'][0]
		lat = check_result['latitude'][0]
		lon = check_result['longitude'][0]
		date_data = '20211129'
		with open(f"/DATA/recv/2021/obs/tw/{i}", 'r', encoding='ISO-8859-1') as fp:
				read_obs_data_row_len = fp.readlines()[4:]
				for j in read_obs_data_row_len:
					split_obs_data = j.split('\n')[0].split(',')
					# print(split_obs_data)
			#0
					if split_obs_data[0][0:16] == f'2021/06/02 00:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 00:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append0.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 00:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/00/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append0, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 00:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append0.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 00:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/00/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append0, var_f, ensure_ascii=False)

			#1
					if split_obs_data[0][0:16] == f'2021/06/02 01:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 01:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append1.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 01:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/01/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append1, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 01:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append1.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 01:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/01/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append1, var_f, ensure_ascii=False)
			#2
					if split_obs_data[0][0:16] == f'2021/06/02 02:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 02:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append2.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 02:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/02/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append2, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 02:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append2.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 02:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/02/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append2, var_f, ensure_ascii=False)
			#3
					if split_obs_data[0][0:16] == f'2021/06/02 03:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 03:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append3.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 03:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/03/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append3, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 03:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append3.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 03:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/03/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append3, var_f, ensure_ascii=False)
			#4
					if split_obs_data[0][0:16] == f'2021/06/02 04:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 04:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append4.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 04:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/04/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append4, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 04:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append4.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 04:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/04/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append4, var_f, ensure_ascii=False)

			#5
					if split_obs_data[0][0:16] == f'2021/06/02 05:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 05:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append5.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 05:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/05/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append5, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 05:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append5.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 05:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/05/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append5, var_f, ensure_ascii=False)

			#6
					if split_obs_data[0][0:16] == f'2021/06/02 06:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 06:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append6.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 06:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/06/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append6, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 06:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append6.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 06:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/06/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append6, var_f, ensure_ascii=False)
					
			#7
					if split_obs_data[0][0:16] == f'2021/06/02 07:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 07:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append7.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 07:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/07/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append7, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 07:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append7.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 07:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/07/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append7, var_f, ensure_ascii=False)
			
			#8
					if split_obs_data[0][0:16] == f'2021/06/02 08:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 08:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append8.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 08:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/08/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append8, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 08:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append8.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 08:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/08/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append8, var_f, ensure_ascii=False)
					
			#9
					if split_obs_data[0][0:16] == f'2021/06/02 09:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 09:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append9.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 09:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/09/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append9, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 09:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append9.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 09:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/09/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append9, var_f, ensure_ascii=False)

			#10
					if split_obs_data[0][0:16] == f'2021/06/02 10:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 10:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append10.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 10:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/10/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append10, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 10:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append10.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 10:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/10/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append10, var_f, ensure_ascii=False)

			#11
					if split_obs_data[0][0:16] == f'2021/06/02 11:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 11:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append11.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 11:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/11/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append11, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 11:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append11.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 11:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/11/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append11, var_f, ensure_ascii=False)

			#12
					if split_obs_data[0][0:16] == f'2021/06/02 12:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 12:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append12.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 12:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/12/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append12, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 12:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append12.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 12:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/12/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append12, var_f, ensure_ascii=False)
					
			#13
					if split_obs_data[0][0:16] == f'2021/06/02 13:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 13:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append13.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 13:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/13/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append13, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 13:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append13.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 13:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/13/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append13, var_f, ensure_ascii=False)
					
			#14
					if split_obs_data[0][0:16] == f'2021/06/02 14:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 14:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append14.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 14:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/14/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append14, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 14:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append14.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 14:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/14/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append14, var_f, ensure_ascii=False)
					
			#15
					if split_obs_data[0][0:16] == f'2021/06/02 15:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 15:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append15.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 15:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/15/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append15, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 15:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append15.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 15:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/15/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append15, var_f, ensure_ascii=False)
					
			#16
					if split_obs_data[0][0:16] == f'2021/06/02 16:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 16:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append16.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 16:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/16/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append16, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 16:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append16.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 16:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/16/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append16, var_f, ensure_ascii=False)
					
			#17
					if split_obs_data[0][0:16] == f'2021/06/02 17:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 17:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append17.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 17:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/17/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append17, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 17:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append17.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 17:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/17/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append17, var_f, ensure_ascii=False)

			#18
					if split_obs_data[0][0:16] == f'2021/06/02 18:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 18:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append18.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 18:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/18/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append18, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 18:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append18.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 18:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/18/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append18, var_f, ensure_ascii=False)
					
			#19
					if split_obs_data[0][0:16] == f'2021/06/02 19:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 19:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append19.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 19:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/19/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append19, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 19:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append19.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 19:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/19/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append19, var_f, ensure_ascii=False)
					
			#20
					if split_obs_data[0][0:16] == f'2021/06/02 20:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 20:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append20.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 20:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/20/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append20, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 20:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append20.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 20:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/20/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append20, var_f, ensure_ascii=False)
					
			#21
					if split_obs_data[0][0:16] == f'2021/06/02 21:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 21:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append21.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 21:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/21/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append21, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 21:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append21.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 21:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/21/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append21, var_f, ensure_ascii=False)
					
			#22
					if split_obs_data[0][0:16] == f'2021/06/02 22:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
          #temp
					if split_obs_data[0][0:16] == f'2021/06/02 22:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append22.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 22:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/22/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append22, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 22:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append22.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 22:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/22/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append22, var_f, ensure_ascii=False)
					
			#23
					if split_obs_data[0][0:16] == f'2021/06/02 23:00':
						time_data = split_obs_data[0][11:13]
						temp_data = split_obs_data[12]
						salt_data = split_obs_data[14]
						#temp
					if split_obs_data[0][0:16] == f'2021/06/02 23:00':
								temp_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": temp_data, "date": date_data, "time": time_data,
									}
								temp_data_append23.append(temp_data)
					if split_obs_data[0][0:16] == f'2021/06/02 23:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/23/temp.json', 'w', encoding="UTF-8") as var_f:
									json.dump(temp_data_append23, var_f, ensure_ascii=False)
						#salt
					if split_obs_data[0][0:16] == f'2021/06/02 23:00':
								salt_data = {
											"obs_post_id": obs_post_id, "name": name, "lat": lat,
											"lon": lon,
											"data": salt_data, "date": date_data, "time": time_data,
									}
								salt_data_append23.append(salt_data)
					if split_obs_data[0][0:16] == f'2021/06/02 23:00':
						with open('/DATA/HResolutionVisual/OUTPUT/json/zeta_salt_temp_tw/20211129/23/salt.json', 'w', encoding="UTF-8") as var_f:
									json.dump(salt_data_append23, var_f, ensure_ascii=False)
         
