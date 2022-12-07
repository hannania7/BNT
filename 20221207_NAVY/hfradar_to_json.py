
import DBInsertModule
import pandas as pd
import ParsingData
import json

lon1 = list()
lat1 = list()
u1 = list()
v1 = list()
data = list()
for i in range(224, 242):
	get_col_head_row_sql = f"select data_name from mng_data_col_head where no={i}"
	a = DBInsertModule.read_query(get_col_head_row_sql)
	code = a['data_name'][0]
	file_path = f'/DATA/opendap/observation/HFR/TOTL_{code}_2020_05_31_1000.tuv'
	read_obs_data_row = ParsingData.read_tuv(file_path)
	print(len(read_obs_data_row))
	# if code == 'BAR2':
	for j in range(len(read_obs_data_row)):
		lon1.append(read_obs_data_row[j][0])
		lat1.append(read_obs_data_row[j][1])
		u1.append(read_obs_data_row[j][2])
		v1.append(read_obs_data_row[j][3])
		# data_type = ['type']
		# data_type_json = data_type * len(read_obs_data_row)
		# ty_pe = [a['data_name'][0]]
		# ty_pe_json = ty_pe * len(read_obs_data_row)
		# lon = ['lon']
		# lon_json = lon * len(read_obs_data_row)
		# lat = ['lat']
		# lat_json = lat * len(read_obs_data_row)
		# u = ['u']
		# u_json = u * len(read_obs_data_row)
		# v = ['v']
		# v_json = v * len(read_obs_data_row)

	all = {'lon' : lon1, 'lat' : lat1, 'u' : u1, 'v' : v1}
		# ty_pe_dict = dict(zip(data_type_json,ty_pe_json))
		# lon_dict = dict(zip(lon_json,lon1))
		# lat_dict = dict(zip(lat_json,lat1))
		# u_dict = dict(zip(u_json,u1))
		# v_dict = dict(zip(v_json,v1))
		# ty_pe_dict.update(lon_dict)
		# ty_pe_dict.update(lat_dict)
		# ty_pe_dict.update(u_dict)
		# ty_pe_dict.update(v_dict)
		# data.append(ty_pe_dict)
# print(len(data))
	with open(f'/DATA/opendap/observation/HFR_test/TOTL_{code}_2020_05_31_1000_output.json', 'w') as outfile:
		json.dump(all, outfile)
	# elif code == 'BARY':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'KYGW':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon3.append(read_obs_data_row[j][0])
	# 		lat3.append(read_obs_data_row[j][1])
	# 		u3.append(read_obs_data_row[j][2])
	# 		v3.append(read_obs_data_row[j][3])
	# elif code == 'KYGI':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'INPO':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'PTDJ':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'TAAN':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'TADA':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'MOPO':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'MOP2':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'YOSU':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'GWYA':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'PUGA':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'PUGE':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'POHA':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'DOSO':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'DONO':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])
	# elif code == 'ULSA':
	# 	for j in range(len(read_obs_data_row)):
	# 		lon2.append(read_obs_data_row[j][0])
	# 		lat2.append(read_obs_data_row[j][1])
	# 		u2.append(read_obs_data_row[j][2])
	# 		v2.append(read_obs_data_row[j][3])