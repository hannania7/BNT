import os
from sys import argv
import sys
from time import strptime
import netCDF4
import numpy as np
import datetime
import subprocess

def concat_merge_uv(filepath):
		find_date = os.path.basename(filepath)
		date = find_date.split('_')[3].split('+')[0]
		print(date)

		date1 = datetime.datetime.strptime(date, "%Y%m%d%H")
		file_today = date1
		file_tomorrow = file_today + datetime.timedelta(days=1)
		file_after_2days = file_today + datetime.timedelta(days=2)

		# tr_file_today = file_today.strftime('%Y%m%d%H')
		# tr_file_tomorrow = file_tomorrow.strftime('%Y%m%d%H')
		# tr_file_after_2days = file_after_2days.strftime('%Y%m%d%H')
		# find_file_today = file_today.strftime('%Y%m%d')

		find_path = os.path.dirname(filepath)
		print(find_path)
		dm_type = find_date.split('_')[0]
		print(dm_type)
		var_type = find_date.split('_')[4]
		wrfdm = find_date.split('_')[2]
		print(wrfdm)

		time_a = []
		lon_a = []
		lat_a = []
		Uwind_a = []
		Vwind_a = []
		if wrfdm == 'wrfdm1':
			for i in range(3):
				if dm_type == 'concat' and var_type == 'uv':
					wrfdm_to = find_path + '/' + 'concat_wrf_wrfdm1_' + (file_today + datetime.timedelta(days=i)).strftime('%Y%m%d%H') + '_uv_regrid.nc'
					ncp = netCDF4.Dataset(wrfdm_to, mode ='r')
					if i == 0:
						ncp_time = ncp.variables['time'][:]
						ncp_lon = ncp.variables['lon'][:]
						ncp_lat = ncp.variables['lat'][:]
						ncp_Uwind = ncp.variables['Uwind'][:]
						ncp_Vwind = ncp.variables['Vwind'][:]
					elif i == 1:
						ncp_time = ncp.variables['time'][:] + 25
						ncp_lon = ncp.variables['lon'][:]
						ncp_lat = ncp.variables['lat'][:]
						ncp_Uwind = ncp.variables['Uwind'][:]
						ncp_Vwind = ncp.variables['Vwind'][:]
					elif i == 2:
						ncp_time = ncp.variables['time'][:] + 50
						ncp_lon = ncp.variables['lon'][:]
						ncp_lat = ncp.variables['lat'][:]
						ncp_Uwind = ncp.variables['Uwind'][:]
						ncp_Vwind = ncp.variables['Vwind'][:]

					time_a.append(ncp_time)
					lon_a = ncp_lon
					lat_a = ncp_lat
					Uwind_a.append(ncp_Uwind)
					Vwind_a.append(ncp_Vwind)

			lon_data = np.array(lon_a)
			lat_data = np.array(lat_a)
			time_data = np.array(time_a)
			Uwind_data = np.array(Uwind_a)
			Vwind_data = np.array(Vwind_a)

			lon_re = lon_data.reshape(215)
			lat_re = lat_data.reshape(215)
			time_re = time_data.reshape(75)
			Uwind_re = Uwind_data.reshape(75,215,215)
			Vwind_re = Vwind_data.reshape(75,215,215)
		
			lon_u = ncp.dimensions['lon']
			lat_u = ncp.dimensions['lat']

			w_ncp = netCDF4.Dataset(find_path + '/' + 'concat_wrf_wrfdm1_' + (file_today + datetime.timedelta(days=0)).strftime('%Y%m%d%H') + '-' + (file_today + datetime.timedelta(days=2)).strftime('%Y%m%d%H') + '_uv_regrid_merge.nc', 'w')
			w_ncp.createDimension('time', time_re.shape[0])
			w_ncp.createDimension('lon_u', lon_u.size)
			w_ncp.createDimension('lat_u', lat_u.size)

			lon = w_ncp.createVariable('lon', 'd', ('lon_u'))
			lat = w_ncp.createVariable('lat', 'd', ('lat_u'))
			time = w_ncp.createVariable('time', 'd', ('time'))
			Uwind = w_ncp.createVariable('Uwind', 'f', ('time', 'lat_u', 'lon_u'), fill_value=9.96921E36)
			Vwind = w_ncp.createVariable('Vwind', 'f', ('time', 'lat_u', 'lon_u'), fill_value=9.96921E36)


			lon[:] = lon_re
			lat[:] = lat_re
			time[:] = time_re
			Uwind[:] = Uwind_re
			Vwind[:] = Vwind_re

			find_date = os.path.basename(filepath)
			date = find_date.split('_')[3]
			year = date[0:4]
			month = date[4:6]
			day = date[6:8]
			hour = date[8:10]

			time.field = "time, scalar, series"
			time.units = f"hours since {year}-{month}-{day} {hour}:00:00"
			time.long_name = "time since initialization"
			time._CoordinateAxisType = 'Time'


			lon.long_name = "longitude"
			lon.units = "degrees_east"
			lon._CoordinateAxisType = "Lon"

			lat.long_name = "latitude"
			lat.units = "degrees_north"
			lat._CoordinateAxisType = "Lat"

			vout1_long_name = "WRF (10m) u winds [m/s]"
			vout1_units = "meter second-1"
			vout1_time = "time"
			vout1_remap = "remapped via ESMF_regrid_with_weights: Bilinear"

			vout2_long_name = "WRF (10m) v winds [m/s]"
			vout2_units = "meter second-1"
			vout2_time = "time"
			vout2_remap = "remapped via ESMF_regrid_with_weights: Bilinear"

			Uwind.long_name = vout1_long_name
			Uwind.units = vout1_units
			Uwind.time = vout1_time
			Uwind.remap = vout1_remap

			Vwind.long_name = vout2_long_name
			Vwind.units = vout2_units
			Vwind.time = vout2_time
			Vwind.remap = vout2_remap

			w_ncp.close()

		if wrfdm == 'wrfdm2':
			for i in range(3):
				if dm_type == 'concat' and var_type == 'uv':
					wrfdm_to = find_path + '/' + 'concat_wrf_wrfdm2_' + (file_today + datetime.timedelta(days=i)).strftime('%Y%m%d%H') + '_uv_regrid.nc'
					ncp = netCDF4.Dataset(wrfdm_to, mode ='r')
					if i == 0:
						ncp_time = ncp.variables['time'][:]
						ncp_lon = ncp.variables['lon'][:]
						ncp_lat = ncp.variables['lat'][:]
						ncp_Uwind = ncp.variables['Uwind'][:]
						ncp_Vwind = ncp.variables['Vwind'][:]
					elif i == 1:
						ncp_time = ncp.variables['time'][:] + 25
						ncp_lon = ncp.variables['lon'][:]
						ncp_lat = ncp.variables['lat'][:]
						ncp_Uwind = ncp.variables['Uwind'][:]
						ncp_Vwind = ncp.variables['Vwind'][:]
					elif i == 2:
						ncp_time = ncp.variables['time'][:] + 50
						ncp_lon = ncp.variables['lon'][:]
						ncp_lat = ncp.variables['lat'][:]
						ncp_Uwind = ncp.variables['Uwind'][:]
						ncp_Vwind = ncp.variables['Vwind'][:]

					time_a.append(ncp_time)
					lon_a = ncp_lon
					lat_a = ncp_lat
					Uwind_a.append(ncp_Uwind)
					Vwind_a.append(ncp_Vwind)

			lon_data = np.array(lon_a)
			print(len(lon_data))
			lat_data = np.array(lat_a)
			time_data = np.array(time_a)
			Uwind_data = np.array(Uwind_a)
			Vwind_data = np.array(Vwind_a)

			lon_re = lon_data.reshape(358)
			lat_re = lat_data.reshape(358)
			time_re = time_data.reshape(75)
			Uwind_re = Uwind_data.reshape(75,358,358)
			Vwind_re = Vwind_data.reshape(75,358,358)
			
			lon_u = ncp.dimensions['lon']
			lat_u = ncp.dimensions['lat']

			w_ncp = netCDF4.Dataset(find_path + '/' + 'concat_wrf_wrfdm2_' + (file_today + datetime.timedelta(days=0)).strftime('%Y%m%d%H') + '-' +  (file_today + datetime.timedelta(days=2)).strftime('%Y%m%d%H') + '_uv_regrid_merge.nc', 'w')
			w_ncp.createDimension('time', time_re.shape[0])
			w_ncp.createDimension('lon_u', lon_u.size)
			w_ncp.createDimension('lat_u', lat_u.size)

			lon = w_ncp.createVariable('lon', 'd', ('lon_u'))
			lat = w_ncp.createVariable('lat', 'd', ('lat_u'))
			time = w_ncp.createVariable('time', 'd', ('time'))
			Uwind = w_ncp.createVariable('Uwind', 'f', ('time', 'lat_u', 'lon_u'), fill_value=9.96921E36)
			Vwind = w_ncp.createVariable('Vwind', 'f', ('time', 'lat_u', 'lon_u'), fill_value=9.96921E36)


			lon[:] = lon_re
			lat[:] = lat_re
			time[:] = time_re
			Uwind[:] = Uwind_re
			Vwind[:] = Vwind_re

			find_date = os.path.basename(filepath)
			date = find_date.split('_')[3]
			year = date[0:4]
			month = date[4:6]
			day = date[6:8]
			hour = date[8:10]

			time.field = "time, scalar, series"
			time.units = f"hours since {year}-{month}-{day} {hour}:00:00"
			time.long_name = "time since initialization"
			time._CoordinateAxisType = 'Time'


			lon.long_name = "longitude"
			lon.units = "degrees_east"
			lon._CoordinateAxisType = "Lon"

			lat.long_name = "latitude"
			lat.units = "degrees_north"
			lat._CoordinateAxisType = "Lat"

			vout1_long_name = "WRF (10m) u winds [m/s]"
			vout1_units = "meter second-1"
			vout1_time = "time"
			vout1_remap = "remapped via ESMF_regrid_with_weights: Bilinear"

			vout2_long_name = "WRF (10m) v winds [m/s]"
			vout2_units = "meter second-1"
			vout2_time = "time"
			vout2_remap = "remapped via ESMF_regrid_with_weights: Bilinear"

			Uwind.long_name = vout1_long_name
			Uwind.units = vout1_units
			Uwind.time = vout1_time
			Uwind.remap = vout1_remap

			Vwind.long_name = vout2_long_name
			Vwind.units = vout2_units
			Vwind.time = vout2_time
			Vwind.remap = vout2_remap
			w_ncp.close()
			# 	if dm_type == 'concat' and var_type == 'Pair':
			# 			wrfdm_to = find_path + '/' + 'concat_wrf_wrfdm1_' + tr_file_today + '_Pair_regrid.nc'
			# 			wrfdm_tomo = find_path +  '/' + 'concat_wrf_wrfdm1_' + tr_file_tomorrow + '_Pair_regrid.nc'
			# 			wrfdm_2days = find_path +  '/' + 'concat_wrf_wrfdm1_' + tr_file_after_2days + '_Pair_regrid.nc'
			# 	if dm_type == 'concat' and var_type == 'Tair':
			# 			wrfdm_to = find_path + '/' + 'concat_wrf_wrfdm1_' + tr_file_today + '_Tair_regrid.nc'
			# 			wrfdm_tomo = find_path +  '/' + 'concat_wrf_wrfdm1_' + tr_file_tomorrow + '_Tair_regrid.nc'
			# 			wrfdm_2days = find_path +  '/' + 'concat_wrf_wrfdm1_' + tr_file_after_2days + '_Tair_regrid.nc'

			# if wrfdm == 'wrfdm2':
			# 	if dm_type == 'concat' and var_type == 'uv':
			# 			wrfdm_to = find_path + '/' + 'concat_wrf_wrfdm1_' + tr_file_today + '_uv_regrid.nc'
			# 			wrfdm_tomo = find_path +  '/' + 'concat_wrf_wrfdm1_' + tr_file_tomorrow + '_uv_regrid.nc'
			# 			wrfdm_2days = find_path +  '/' + 'concat_wrf_wrfdm1_' + tr_file_after_2days + '_uv_regrid.nc'
			# 	elif dm_type == 'concat' and var_type == 'Pair':
			# 			wrfdm_to = find_path + '/' + 'concat_wrf_wrfdm1_' + tr_file_today + '_Pair_regrid.nc'
			# 			wrfdm_tomo = find_path +  '/' + 'concat_wrf_wrfdm1_' + tr_file_tomorrow + '_Pair_regrid.nc'
			# 			wrfdm_2days = find_path +  '/' + 'concat_wrf_wrfdm1_' + tr_file_after_2days + '_Pair_regrid.nc'
			# 	elif dm_type == 'concat' and var_type == 'Tair':
			# 			wrfdm_to = find_path + '/' + 'concat_wrf_wrfdm1_' + tr_file_today + '_Tair_regrid.nc'
			# 			wrfdm_tomo = find_path +  '/' + 'concat_wrf_wrfdm1_' + tr_file_tomorrow + '_Tair_regrid.nc'
			# 			wrfdm_2days = find_path +  '/' + 'concat_wrf_wrfdm1_' + tr_file_after_2days + '_Tair_regrid.nc'

if __name__ == "__main__":
		filepath = sys.argv[1]
		# day = 20220627
		concat_merge_uv(filepath)