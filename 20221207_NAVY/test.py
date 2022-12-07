import netCDF4
# from datetime import datetime
import pandas as pd
import numpy as np
import pyproj
import MakeFilePath
import ParsingData
import subprocess
import json
import matplotlib.pyplot as plt
# import folium
# import geopandas as gpd

PROPERTY_PATH = '/DATA/NAVY/source/property.in'
PROPERTY = ParsingData.read_property(PROPERTY_PATH)

with open("/DATA/recv/2021/obs/hf/TOTL_YOSU_2022_01_01_0100.tuv", 'r', encoding='ISO-8859-1') as fp:
    read_obs_data_row = fp.readlines()[31:-22]
lon = list()
lat = list()
u = list()
v = list()
speed = list()
for i in read_obs_data_row:
		obs_row_list = i.split("\n")
		a = float(obs_row_list[0][3:14].strip(' '))
		b = float(obs_row_list[0][16:26].strip(' '))
		c = float(obs_row_list[0][28:35].strip(' '))
		d = float(obs_row_list[0][37:44].strip(' '))
		e = float(np.sqrt(c**2 + d**2))
		lon.append(a)
		lat.append(b)
		u.append(c)
		v.append(d)
		speed.append(e)

e = list()
f = list()
a = list()
k = 127.7853112
for i in range(459):
	k += lon[i+1] - lon[i]
	if np.abs(k - lon[i]) > 0.0000169:
		k = k - (lon[i+1] - lon[i]) / 2
		e.append(k)
		k = k + (lon[i+1] - lon[i]) / 2
e.append(127.7853112)
# print(len(e))
# print(e)

h = 34.7444523
for j in range(459):
	h += lat[j+1] - lat[j]
	if np.abs(h - lat[j]) > 0.009015:
		h = h - (lat[j+1] - lat[j])/2
		f.append(h)
		h = h + (lat[j+1] - lat[j])/2
# print(f)

lon_s = lon + e
lat_s = lat + f
m = list()
# print(m)
	
lon = np.array(lon_s)
lat = np.array(lat_s)
u = np.array(u)
v = np.array(v)
speed = np.array(speed)
lat_min = min(lat)
lat_max = max(lat)
lat_size = len(lat)
lat_array = np.around(lat, 3).tolist()
lon_min = min(lon)
lon_max = max(lon)
lon_size = len(lon)
lon_array = np.around(lon, 3).tolist()
u_array = np.round(u, 3).tolist()
u_min = min(u)
u_max = max(u)
v_array = np.round(v, 3).tolist()
v_min = min(v)
v_max = max(v)
speed_min = min(speed)
speed_max = max(speed)
stream_data = {
					"lat_min": lat_min, "lat_max": lat_max, "lat_size": lat_size,
					"lat_array": lat_array,
					"lon_min": lon_min, "lon_max": lon_max, "lon_size": lon_size,
					"lon_array": lon_array,
					"u_array": u_array, "u_min": u_min, "u_max": u_max,
					"v_array": v_array, "v_min": v_min, "v_max": v_max,
					"speed_min": speed_min, "speed_max": speed_max
			}
# with open('/DATA/recv/2021/obs/stream.json', 'w') as var_f:
# 		json.dump(stream_data, var_f)

# 		uv_array = u_array + v_array
# 		uv_data = {"array" : uv_array, "speedArray" : speed.tolist()}
# with open('/DATA/recv/2021/obs/uv.json', 'w') as uv_f:
# 	json.dump(uv_data, uv_f)


plt.plot(lon_s, lat_s, 'ro')
plt.xlabel('longitude')
plt.ylabel('latitude')
plt.show()
plt.savefig('/DATA/recv/2021/obs/lon_lat.png')