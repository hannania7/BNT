import os
import sys
import math
import datetime
import netCDF4
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
	
def find_thenearest_grd_pts(lat_array,lon_array,latitude,longitude):
    lon = lon_array[: , :] - float(longitude)
    lat = lat_array[: , :] - float(latitude)
    diff = (lon * lon) + (lat * lat)
    j_indices, i_indices = np.where(diff==diff.min())
    j = j_indices[0]
    i = i_indices[0]
    # print(j)
    # print(i)
    return j, i
	
def make_mndarray2ndarray(array_p):
		array_p.set_fill_value(0)
		array_p = array_p.filled()
		return array_p
file_name = os.listdir('/DATA/opendap/observation/HFR')
for k in file_name:
	if k[5:9] == 'MOP2':
		continue
	if k[-19:-1] == '2020_05_26_0000.tu':
		for i in range(0, 10):
			if not os.path.exists(f'/DATA/HResolutionVisual/OUTPUT/json/{k[5:9]}/20211129/000{i}'):
				os.makedirs(f'/DATA/HResolutionVisual/OUTPUT/json/{k[5:9]}/20211129/000{i}')
		for i in range(10,24):
			if not os.path.exists(f'/DATA/HResolutionVisual/OUTPUT/json/{k[5:9]}/20211129/00{i}'):
				os.makedirs(f'/DATA/HResolutionVisual/OUTPUT/json/{k[5:9]}/20211129/00{i}')

		for i in range(0,24):
			if 0 <= i < 9:
				ncp = netCDF4.Dataset(f'/DATA/opendap/simulation/ocean/basin/YES3K/2021112800/his_yes3km_000{i+1}.nc', 'r')
			elif 9 <= i < 24:
				ncp = netCDF4.Dataset(f'/DATA/opendap/simulation/ocean/basin/YES3K/2021112800/his_yes3km_00{i+1}.nc', 'r')
			lon_rho2 = make_mndarray2ndarray(ncp.variables['lon_rho'][:])
			lat_rho2 = make_mndarray2ndarray(ncp.variables['lat_rho'][:])
			# hf radar 최대 최소
			with open(f"/DATA/opendap/observation/HFR/TOTL_{k[5:9]}_2020_05_26_0000.tuv", 'r', encoding='ISO-8859-1') as fp:
					read_obs_data_row = fp.readlines()[31:-24]
			lon_ap = list()
			lat_ap = list()
			u_ap = list()
			v_ap = list()
			for a, j in enumerate(read_obs_data_row):
					obs_row_list = j.split("\n")[0]
					lon = float(obs_row_list[3:14].strip(' '))
					lat = float(obs_row_list[16:26].strip(' '))
					ucomp = float(obs_row_list[29:35].strip(' '))
					vcomp = float(obs_row_list[37:44].strip(' '))
					lon_ap.append(lon)
					lat_ap.append(lat)
					u_ap.append(ucomp)
					v_ap.append(vcomp)
			hf_lon_min = np.min(lon_ap)
			hf_lon_max = np.max(lon_ap)
			hf_lat_min = np.min(lat_ap)
			hf_lat_max = np.max(lat_ap)
			# print(hf_lon_max)

			jmax, imax = find_thenearest_grd_pts(lat_rho2[:,:],lon_rho2[:,:],hf_lat_max,hf_lon_max)
			jmin, imin = find_thenearest_grd_pts(lat_rho2[:,:],lon_rho2[:,:],hf_lat_min,hf_lon_min)

			lon_rho = make_mndarray2ndarray(ncp.variables['lon_rho'][0, imin:imax])
			lat_rho = make_mndarray2ndarray(ncp.variables['lat_rho'][jmin:jmax, 0])
			print(len(lat_rho))
			print(len(lon_rho))
			lonlat_array = list()
			var_array = list()

			for y in range(lat_rho.shape[0]):
					for x in range(lon_rho.shape[0]):
						lonlat_array.append(lon_rho[x])
						lonlat_array.append(lat_rho[y])

			lon_min = lon_rho[0]
			lon_max = lon_rho[-1]
			lat_min = lat_rho[0]
			lat_max = lat_rho[-1]
			sampling_lon = len(lon_rho)
			sampling_lat = len(lat_rho)
			lon_delta = lon_max - lon_min
			lat_delta = lat_max - lat_min
			lon_interval = (lon_delta / sampling_lon)
			lat_interval = (lat_delta / sampling_lat)
			lonlat_array2 = np.array(lonlat_array).flatten().tolist()
			print(len(lonlat_array2))
			loalat_data = {'array': lonlat_array2, 'lonInterval': lon_interval, 'latInterval': lat_interval,
											'samplingLon': sampling_lon, 'samplingLat': sampling_lat,
											'lonMinVal': lon_min, 'latMinVal': lat_min, 'lonMaxVal': lon_max, 'latMaxVal': lat_max,
											'lonDelta': lon_delta, 'latDelta': lat_delta}
			if 0 <= i < 10:
				with open(f'/DATA/HResolutionVisual/OUTPUT/json/{k[5:9]}_lonlat.json', 'w') as lonlat_f:
						json.dump(loalat_data, lonlat_f)

				u_nc_arr = make_mndarray2ndarray(ncp.variables['u'][0,0,jmin:jmax, imin:imax])
				v_nc_arr = make_mndarray2ndarray(ncp.variables['v'][0,0,jmin:jmax, imin:imax])
				u_depth_arr = u_nc_arr[:]
				u_arr = np.where(u_depth_arr < -999, 0, u_depth_arr).astype(np.float64).flatten()
				v_depth_arr = v_nc_arr[:]
				v_arr = np.where(v_depth_arr < -999, 0, v_depth_arr).astype(np.float64).flatten()

				u_min = np.min(u_arr)
				u_max = np.max(u_arr)
				v_min = np.min(v_arr)
				v_max = np.max(v_arr)

				speed = list()
				for a in range(len(u_arr)):
					e = float(np.sqrt((u_arr[a] * u_arr[a]) + (v_arr[a] *v_arr[a])))
					speed.append(e)

				stream_data = {
						"lat_min": lat_min, "lat_max": lat_max, "lat_size": sampling_lat,
						"lat_array": lat_rho.tolist(),
						"lon_min": lon_min, "lon_max": lon_max, "lon_size": sampling_lon,
						"lon_array": lon_rho.tolist(),
						"u_array": u_arr.tolist(), "u_min": u_min, "u_max": u_max,
						"v_array": v_arr.tolist(), "v_min": v_min, "v_max": v_max,
						"speed_min": np.min(speed), "speed_max": np.max(speed)
				}
				with open(f'/DATA/HResolutionVisual/OUTPUT/json/{k[5:9]}/20211129/000{i}/stream.json', 'w') as var_f:
						json.dump(stream_data, var_f)

				uv_array = list()
				for y in range(u_arr.shape[0]):
								u = u_arr[y]
								v = v_arr[y]
								uv_array.append(u)
								uv_array.append(v)
				print(len(uv_array))
				uv_data = {"array" : uv_array, "speedArray" : speed}
				with open(f'/DATA/HResolutionVisual/OUTPUT/json/{k[5:9]}/20211129/000{i}/uv.json', 'w') as lonlat_f:
						json.dump(uv_data, lonlat_f)
			elif 10 <= i < 24:
					with open(f'/DATA/HResolutionVisual/OUTPUT/json/{k[5:9]}_lonlat.json', 'w') as lonlat_f:
						json.dump(loalat_data, lonlat_f)

					u_nc_arr = make_mndarray2ndarray(ncp.variables['u'][0,0,jmin:jmax, imin:imax])
					v_nc_arr = make_mndarray2ndarray(ncp.variables['v'][0,0,jmin:jmax, imin:imax])
					u_depth_arr = u_nc_arr[:]
					u_arr = np.where(u_depth_arr < -999, 0, u_depth_arr).astype(np.float64).flatten()
					v_depth_arr = v_nc_arr[:]
					v_arr = np.where(v_depth_arr < -999, 0, v_depth_arr).astype(np.float64).flatten()

					u_min = np.min(u_arr)
					u_max = np.max(u_arr)
					v_min = np.min(v_arr)
					v_max = np.max(v_arr)

					speed = list()
					for a in range(len(u_arr)):
						e = float(np.sqrt((u_arr[a] * u_arr[a]) + (v_arr[a] *v_arr[a])))
						speed.append(e)

					stream_data = {
							"lat_min": lat_min, "lat_max": lat_max, "lat_size": sampling_lat,
							"lat_array": lat_rho.tolist(),
							"lon_min": lon_min, "lon_max": lon_max, "lon_size": sampling_lon,
							"lon_array": lon_rho.tolist(),
							"u_array": u_arr.tolist(), "u_min": u_min, "u_max": u_max,
							"v_array": v_arr.tolist(), "v_min": v_min, "v_max": v_max,
							"speed_min": np.min(speed), "speed_max": np.max(speed)
					}
					with open(f'/DATA/HResolutionVisual/OUTPUT/json/{k[5:9]}/20211129/00{i}/stream.json', 'w') as var_f:
							json.dump(stream_data, var_f)

					uv_array = list()
					for y in range(u_arr.shape[0]):
									u = u_arr[y]
									v = v_arr[y]
									uv_array.append(u)
									uv_array.append(v)
					print(len(uv_array))
					uv_data = {"array" : uv_array, "speedArray" : speed}
					with open(f'/DATA/HResolutionVisual/OUTPUT/json/{k[5:9]}/20211129/00{i}/uv.json', 'w') as lonlat_f:
							json.dump(uv_data, lonlat_f)
       
					uv_data2 = {"model": k[5:9], "lon_min": lon_min, "lon_max": lon_max, "lat_min": lat_min, "lat_max": lat_max}
					with open(f'/DATA/HResolutionVisual/OUTPUT/json/a/{k[5:9]}_min_max.json', 'w') as lonlat_f:
							json.dump(uv_data2, lonlat_f)