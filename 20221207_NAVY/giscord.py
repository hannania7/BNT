import json
import pandas as pd
# os가 기본 library인지 확인 필요
import os
import numpy as np
import datetime
import ParsingData
import psycopg2
import psycopg2.extras as extras

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

k_ap = list()
with open('/DATA/recv/2021/pred/test/giscoord.geojson', 'r') as f:
	json_data = json.load(f)
	for i in range(0, 44):
		k = json_data['features'][i]["properties"]['regid']
		k_ap.append(k)
# print(k_ap)

# 44개
k_ap = ['S1131100', 'S1131200', 'S1131300', 'S1132110', 'S1132120', 'S1132210', 'S1132220', \
				'S1151100', 'S1151200', 'S1151300', 'S1152010', 'S1152020', 'S1231100', 'S1231200', \
				'S1231300', 'S1231400', 'S1231500', 'S1232110', 'S1232120', 'S1232210', 'S1232220', \
				'S1251100', 'S1251200', 'S1251300', 'S1251400', 'S1252010', 'S1252020', 'S1311100', \
				'S1311200', 'S1311300', 'S1311400', 'S1312010', 'S1312020', 'S1321100', 'S1321200', \
				'S1322100', 'S1322200', 'S1323100', 'S1323200', 'S1323300', 'S1323400', 'S1324020', \
				'S1324110', 'S1324210']







# 해상	남해동부	남해동부먼바다	12B20200
# 해상	동해남부	동해남부남쪽먼바다	12C10201
# 해상	동해남부	동해남부북쪽먼바다	12C10202
# 해상	동해중부	동해중부먼바다	12C20200
# 해상	서해남부	서해남부북쪽먼바다	12A30201
# 해상	서해남부	서해남부남쪽먼바다	12A30202
# 해상	서해중부	서해중부먼바다	12A20200
# 해상	제주도남쪽먼바다	제주도남쪽먼바다	12B10400
# 해상	해상국지	인천·경기남부앞바다	12A20102
# 해상	해상국지	경기북부앞바다	12A20101
# 해상	해상국지	부산앞바다	12B20103
# 해상	해상국지	울산앞바다	12C10101
# 해상	해상국지	경남중부남해앞바다	12B20102
# 해상	해상국지	경남서부남해앞바다	12B20101
# 해상	해상국지	거제시동부앞바다	12B20104
# 해상	해상국지	경북남부앞바다	12C10102
# 해상	해상국지	경북북부앞바다	12C10103
# 해상	해상국지	전남북부서해앞바다	22A30103
# 해상	해상국지	전남중부서해앞바다	22A30104
# 해상	해상국지	전남남부서해앞바다	22A30105
# 해상	해상국지	전남서부남해앞바다	12B10101
# 해상	해상국지	전남동부남해앞바다	12B10102
# 해상	해상국지	전북북부앞바다	22A30101
# 해상	해상국지	전북남부앞바다	22A30102
# 해상	해상국지	충남북부앞바다	12A20103
# 해상	해상국지	충남남부앞바다	12A20104
# 해상	해상국지	강원북부앞바다	12C20103
# 해상	해상국지	강원중부앞바다	12C20102
# 해상	해상국지	강원남부앞바다	12C20101
# 해상	해상국지	제주도북부앞바다	12B10302
# 해상	해상국지	제주도남부앞바다	12B10303
# 해상	해상국지	제주도동부앞바다	12B10301
# 해상	해상국지	제주도서부앞바다	12B10304
# 해상	남해서부	남해서부서쪽먼바다	12B10201
# 해상	남해서부	남해서부동쪽먼바다	12B10202

# geojson는 해상이 44개,
gu = ['12C10101', '12C10102', '12C10103', '12C10201', '12C10201', '12C10202', '12C10202', \
			'12C20103', '12C20102', '12C20101', '12C20200', '12C20200', '22A30101', '22A30102', \
			'22A30103', '22A30104', '22A30105', '12A30201', '12A30201', '12A30202', '12A30202', \
			'12A20101', '12A20102', '12A20103', '12A20104', '12A20200', '12A20200', '12B20103', \
			'12B20101', '12B20102', '12B20104', '12B20200', '12B20200', '12B10101', '12B10102', \
			'12B10201', '12B10202', '12B10302', '12B10301', '12B10303', '12B10304', '12B10400', \
			'12B10400', '12B10400']
print(len(gu))

regko = ['해상국지', '해상국지', '해상국지', '동해남부', '동해남부', '동해남부', '동해남부',\
				 '해상국지', '해상국지', '해상국지', '동해중부', '동해중부', '해상국지', '해상국지',\
				 '해상국지', '해상국지', '해상국지', '서해남부', '서해남부', '서해남부', '서해남부',\
				 '해상국지', '해상국지', '해상국지', '해상국지', '서해중부', '서해중부', '해상국지',\
				 '해상국지', '해상국지', '해상국지', '남해동부', '남해동부', '해상국지', '해상국지',\
				 '남해서부', '남해서부', '해상국지', '해상국지', '해상국지', '해상국지', '제주도남쪽먼바다',\
				 '제주도남쪽먼바다', '제주도남쪽먼바다']

# 예보구역목록.xlsx는 53개
df = pd.read_csv('/DATA/recv/2021/pred/test/yebo.csv')
print(df['구역코드'])
sin = list()
for i in df['구역코드'][183:238]:
	sin.append(i)
# 53-2
sin.remove('12C10200')
sin.remove('12A30200')
# 51개
print(sin)

# 51개
sin = ['12F00200', '12F00100', '12B20100', '12B20200', '12B10100', '12D00000', '1.20E+01', \
			 '12C10100', '12C10201', '12C10202', '12C30100', '12C30200', '12C20100', '12C20200', \
			 '12A30100', '12A30201', '12A30202', '12A10100', '12A10200', '12A20200', '12A20100', \
			 '12G00000', '12B10400', '12B10300', '12A20102', '12A20101', '12B20103', '12C10101', \
			 '12B20102', '12B20101', '12B20104', '12C10102', '12C10103', '22A30103', '22A30104', \
			 '22A30105', '12B10101', '12B10102', '22A30101', '22A30102', '12A20103', '12A20104', \
			 '12C20103', '12C20102', '12C20101', '12B10302', '12B10303', '12B10301', '12B10304', \
			 '12B10201', '12B10202']


ground = ['해상'] * 44

# for i in zip(gu, k_ap, regko, regko_fullname, ground):

# data_sql = f"insert into sea_forecast_area (regid, regid_old, regko, regko_fullname, ground) values %s"

# with connect() as connection:
# 				with connection.cursor() as cursor:
# 								extras.execute_values(cursor, data_sql, ap32)
# 				cursor.close()
# connection.close()