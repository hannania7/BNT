# -*- coding: utf-8 -*-


import os
import sys
import netCDF4
import json
from datetime import datetime
import numpy as np
import pandas as pd

def var_height_interp(vertical: np.array, value_array: np.array, bathmetry:np.array, height: float) -> np.array:
    # vertical.shape = 40,1620,1620, value_array.shape = 40,1620,1620, bathmetry.shape: 1620,1620
    # result_array.shape = 1,1620,1620
		fill_value = -999.9
		result_array = np.full((1, 1620, 1620),fill_value=fill_value)
		ap1 = list()
		for y in range(1620):
				for x in range(1620):
						# 2022.10.19 원태찬 정해진 높이보다 미달될 경우 그 지점 최대 수심이 들어감
						# check max bathmetry
						if bathmetry[y, x] > height:
							height = bathmetry[y, x]
							ap1.append(height)
							continue
						temp = np.interp(height, vertical[:, y, x], value_array[:, y, x])
						# check max_value
						if temp > 999:
								continue
						else:
							# 2022.10.19 원태찬 height(m)로 interpolation하고 height(m)에서 단면으로 자른 값
							result_array[0, y, x] = temp
		print(len(ap1))
		return result_array


def main(filepath, varname, height, time):
		# init
		height = int(height)
		time2 = int(time)

		ncp = netCDF4.Dataset(filepath, mode ='r')
		src_lat = ncp.variables['lat'][:]
		src_lon = ncp.variables['lon'][:]
		src_time = ncp.variables['time'][:]
		src_bath = ncp.variables['bathymetry'][:]
		vertical = ncp.variables['vertical'][:]
		if 0 <= height <= 1.5:
			floor = 39
		elif 1.5 < height <= 3.32:
			floor = 38
		elif 3.32 < height <= 5.14:
			floor = 37
		elif 5.14 < height <= 7.11:
			floor = 36
		elif 7.11 < height <= 9.08:
			floor = 35
		elif 9.08 < height <= 11.05:
			floor = 34
		elif 11.05 < height <= 13.02:
			floor = 33
		elif 13.02 < height <= 15:
			floor = 32																										
		elif 15 < height <= 18:
			floor = 31
		elif 18 < height <= 25:
			floor = 30
		elif 25 < height <= 40:
			floor = 29
		elif 40 < height <= 62.5:
			floor = 28
		elif 62.5 < height <= 87.5:
			floor = 27
		elif 87.5 < height <= 112.5:
			floor = 26
		elif 112.5 < height <= 137.5:
			floor = 25
		elif 137.5 < height <= 175:
			floor = 24
		elif 175 < height <= 225:
			floor = 23
		elif 225 < height <= 275:
			floor = 22
		elif 275 < height <= 350:
			floor = 21
		elif 350 < height <= 450:
			floor = 20
		elif 450 < height <= 550:
			floor = 19
		elif 550 < height <= 650:
			floor = 18
		elif 650 < height <= 750:
			floor = 17
		elif 750 < height <= 850:
			floor = 16
		elif 850 < height <= 950:
			floor = 15
		elif 950 < height <= 1050:
			floor = 14
		elif 1050 < height <= 1150:
			floor = 13
		elif 1150 < height <= 1250:
			floor = 12
		elif 1250 < height <= 1350:
			floor = 11
		elif 1350 < height <= 1450:
			floor = 10
		elif 1450 < height <= 1625:
			floor = 9
		elif 1625 < height <= 1875:
			floor = 8
		elif 1875 < height <= 2195.9:
			floor = 7
		else:
			floor = 6
		print(floor)																																																															
		src_vertical = ncp.variables['verticalinfo'][time,:,:,:]

		if varname == 'temp':
				var_array = ncp.variables['temp'][time,:,:,:]
				vout_long_name = 'potential temperature'
				vout_units = 'Celcius'
				vout_time='time'
				vout_coordinates = 'lon lat time'
		elif varname == 'sali':
				var_array = ncp.variables['salt'][time,:,:,:]
				print(np.shape(var_array))
				vout_long_name = 'salinity'
				vout_units = 'psu'
				vout_time='time'
				vout_coordinates = 'lon lat time'
		else:
				sys.exit('wrong_var_name_type') 

		# interp value array use height
		# if height <= 15:
		# 	interp_value_array = var_height_interp(vertical=src_vertical, value_array=var_array,
		# 																				bathmetry=src_bath, height=height)

		filename_with_ext = os.path.basename(filepath)
		filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
		yyyymmdd12 = filename_without_ext[-10:]
		start_date = datetime.strptime(yyyymmdd12,"%Y%m%d%H")
		path1 = os.path.split(filepath)
		path2 = os.path.split(path1[0])
		foldername = path2[1]

		[t] = np.shape(src_time[:])
		new_time =[]
		for t_step in range(t):
				t_step = float(t_step)
				new_time.append(t_step)
		
		# interp_value_array = np.where(interp_value_array == np.NaN, -999.9, interp_value_array)
		# interp_value_array = np.ma.masked_where(interp_value_array <= -99.9, interp_value_array)
		var_array = np.ma.masked_where(var_array <= -99.9, var_array)
		data = [{"data": varname, "min": float(np.ma.min(var_array)), "max": float(np.ma.max(var_array))}]

		new_datum_str = 'hours since %s' % start_date.strftime("%Y-%m-%d %H:%M:%S")

		hslice_mohid_fname = '/DATA/PYTHON/output/mohid2k/hslice_%s_%04d_%s_%02d.nc'% \
												(yyyymmdd12, int(time), varname, int(height))
		with open('/DATA/PYTHON/output/mohid2k/hslice_%s_%04d_%s_%02d_minmax.json' % \
							(yyyymmdd12, int(time), varname, int(height)), "w") as f:
				json.dump(data, f)

		lon_d = ncp.dimensions['lon']
		lat_d = ncp.dimensions['lat']

		nc2write = netCDF4.Dataset(hslice_mohid_fname, mode='w', format="NETCDF3_CLASSIC")

		nc2write.createDimension('time', None)
		nc2write.createDimension('lon', size = lon_d.size)
		nc2write.createDimension('lat', size = lat_d.size)
		# nc2write.createDimension('vertical', size = vertical.shape[0])

		var = nc2write.createVariable(varname,'f',('time','lat','lon'),fill_value=-999.9)
		lat = nc2write.createVariable('lat','d','lat')
		lon = nc2write.createVariable('lon','d','lon')
		time =nc2write.createVariable('time','d','time')

		lat[:] = src_lat[:]
		lon[:] = src_lon[:]
		time[:] = int(time2)
		# print(np.shape(interp_value_array))
		# print(var_array[10,:,:])
		# if height > 15:
		var[0,:,:] = var_array[int(floor), :, :]
		# elif height <= 15:
		# 	var[:] = interp_value_array[:]
		print(var[:])


		lon.long_name = 'longitude'
		lon.units = 'degree_east'
		lon.standard_names = 'longitude'

		lat.long_name = 'latitude'
		lat.units = 'degree_north'
		lat.standard_names = 'latitude'

		time.long_name = 'time since initialization'
		time.units = new_datum_str

		var.long_name = vout_long_name
		var.units = vout_units
		var.time= vout_time
		var.coordinates = vout_coordinates

		nc2write.close()

if __name__ == "__main__":
		main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])