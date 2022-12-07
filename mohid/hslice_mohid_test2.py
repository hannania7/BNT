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
		for y in range(1620):
				for x in range(1620):
						# 2022.10.19 원태찬 정해진 높이보다 미달될 경우 그 지점 최대 수심이 들어감
						# check max bathmetry
						if bathmetry[x, y] < height:
							height = bathmetry[x, y]
						# continue
						temp = np.interp(height, vertical[:, x, y], value_array[:, y, x])
						# check max_value
						if temp > 999:
							continue
						else:
							# 2022.10.19 원태찬 height(m)로 interpolation하고 height(m)에서 단면으로 자른 값
							result_array[0, y, x] = temp
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
		for i in range(1,33):
			if height <= 15:
				break
			elif 15 + ((i-1) * 63.1390625) < height < 15 + (i * 63.1390625):
				floor = i + 8
				print(floor)
		src_vertical = ncp.variables['verticalinfo'][time, :, :, :]

		if varname == 'temp':
				var_array = ncp.variables['temp'][time, :, :, :]
				print(np.shape(var_array))
				vout_long_name = 'potential temperature'
				vout_units = 'Celcius'
				vout_time='time'
				vout_coordinates = 'lon lat time'
		elif varname == 'sali':
				var_array = ncp.variables['salt'][time, :, :, :]
				print(np.shape(var_array))
				vout_long_name = 'salinity'
				vout_units = 'psu'
				vout_time='time'
				vout_coordinates = 'lon lat time'
		else:
				sys.exit('wrong_var_name_type') 

		# interp value array use height
		interp_value_array = var_height_interp(vertical=src_vertical, value_array=var_array,bathmetry=src_bath, height=height)

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

		hslice_mohid_fname = '/DATA/PYTHON/test2/hslice_%s_%04d_%s_%02d.nc'% \
												(yyyymmdd12, int(time), varname, int(height))
		with open('/DATA/PYTHON/test2/hslice_%s_%04d_%s_%02d_minmax.json' % \
							(yyyymmdd12, int(time), varname, int(height)), "w") as f:
				json.dump(data, f)


		nc2write = netCDF4.Dataset(hslice_mohid_fname, mode='w', format="NETCDF3_CLASSIC")

		nc2write.createDimension('time', None)
		nc2write.createDimension('lon', size = src_lon.shape[0])
		nc2write.createDimension('lat', size = src_lat.shape[0])
		#nc2write.createDimension('vertical', size = vertical.shape[0])

		var = nc2write.createVariable(varname,'f',('time','lat','lon'),fill_value=-999.9)
		lat = nc2write.createVariable('lat','d','lat')
		lon = nc2write.createVariable('lon','d','lon')
		time =nc2write.createVariable('time','d','time')

		lat[:] = src_lat[:]
		lon[:] = src_lon[:]
		time[:] = time2
		# print(np.shape(interp_value_array))
		# print(var_array[10,:,:])
		#if height > 15:
			#var[0,:,:] = ncp.variables['temp'][time2, int(floor), :, :]
		#elif height <= 15:
		var[:] = interp_value_array[:]
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