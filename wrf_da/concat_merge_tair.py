import os
from sys import argv
import sys
from time import strptime
import netCDF4
import numpy as np
import datetime
import subprocess

def concat_merge_tair(filepath):
# output 폴더가 없으면 생성
		if not os.path.exists('/DATA/PYTHON+NCL/output/wrf_da'):
				os.makedirs('/DATA/PYTHON+NCL/output/wrf_da')  
		find_path = os.path.dirname(filepath)
		find_date = os.path.basename(filepath)
		date = find_date.split('_')[3]
		date1 = datetime.datetime.strptime(date, "%Y%m%d%H")
		file_today = date1
		wrfdm = find_date.split('_')[2]
		time_a = []
		lon_a = []
		lat_a = []
		Tair_a = []
		if wrfdm == 'wrfdm1':
			for i in range(3):
					wrfdm_to = find_path + '/' + 'concat_wrf_wrfdm1_' + (file_today + datetime.timedelta(days=i)).strftime('%Y%m%d%H') + '_Tair_regrid.nc'
					nc2read = netCDF4.Dataset(wrfdm_to, 'r')
					if i == 0:
						r_lat = nc2read.variables["lat"][:] 
						r_lon = nc2read.variables["lon"][:]
						r_time = nc2read.variables["time"][:]
						r_Tair = nc2read.variables["Tair"][:]
					if i == 1:
						r_lat = nc2read.variables["lat"][:] 
						r_lon = nc2read.variables["lon"][:]
						r_time = nc2read.variables["time"][:] + 25
						r_Tair = nc2read.variables["Tair"][:]
					if i == 2:
						r_lat = nc2read.variables["lat"][:] 
						r_lon = nc2read.variables["lon"][:]
						r_time = nc2read.variables["time"][:] + 50
						r_Tair = nc2read.variables["Tair"][:]
			# test = nc2read.variables[varname][:,:,:]
			# print(test)

					time_a.append(r_time)
					lon_a = r_lon
					lat_a = r_lat
					Tair_a.append(r_Tair)

			lon_data = np.array(lon_a)
			lat_data = np.array(lat_a)
			time_data = np.array(time_a)
			Tair_data = np.array(Tair_a)

			lon_re = lon_data.reshape(215)
			lat_re = lat_data.reshape(215)
			time_re = time_data.reshape(75)
			Tair_re = Tair_data.reshape(75,215,215)
			
			lon_u = nc2read.dimensions['lon']
			lat_u = nc2read.dimensions['lat']

			w_ncp = netCDF4.Dataset(find_path + '/' + 'concat_wrf_wrfdm1_' + (file_today + datetime.timedelta(days=0)).strftime('%Y%m%d%H') + '-' + (file_today + datetime.timedelta(days=2)).strftime('%Y%m%d%H') + '_Tair_regrid_merge.nc', 'w')
			w_ncp.createDimension('time', time_re.shape[0])
			w_ncp.createDimension('lon_u', lon_u.size)
			w_ncp.createDimension('lat_u', lat_u.size)

			lon = w_ncp.createVariable('lon', 'd', ('lon_u'))
			lat = w_ncp.createVariable('lat', 'd', ('lat_u'))
			time = w_ncp.createVariable('time', 'd', ('time'))
			Tair = w_ncp.createVariable('Tair', 'f', ('time', 'lat_u', 'lon_u'), fill_value=9.96921E36)

			lon[:] = lon_re
			lat[:] = lat_re
			time[:] = time_re
			Tair[:] = Tair_re

			year = date[0:4] 
			month = date[4:6]
			day = date[6:8]
			hour = date[8:10]
			print(f"hours since {year}-{month}-{day} {hour}:00:00")
			# datum = datetime(1968,5,23,0,0,0)
			# new_datum = datum + timedelta(seconds = r_time[0])
			# new_datum_str = 'hours since %s' % new_datum.strftime("%Y-%m-%d %H:%M:%S")
			# yyyymmddhh = new_datum.strftime("%Y%m%d%H")

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

			vout_long_name = "2 metre temperature"
			vout_units = "Celcius"
			vout_time = "time"
			vout_remap = "remapped via ESMF_regrid_with_weights: Bilinear"

			Tair.long_name = vout_long_name
			Tair.time = vout_time
			Tair.units = vout_units
			Tair.remap = vout_remap
			w_ncp.close()

		if wrfdm == 'wrfdm2':
			for i in range(3):
					wrfdm_to = find_path + '/' + 'concat_wrf_wrfdm2_' + (file_today + datetime.timedelta(days=i)).strftime('%Y%m%d%H') + '_Tair_regrid.nc'
					nc2read = netCDF4.Dataset(wrfdm_to, 'r')
					if i == 0:
						r_lat = nc2read.variables["lat"][:] 
						r_lon = nc2read.variables["lon"][:]
						r_time = nc2read.variables["time"][:]
						r_Tair = nc2read.variables["Tair"][:]
					if i == 1:
						r_lat = nc2read.variables["lat"][:] 
						r_lon = nc2read.variables["lon"][:]
						r_time = nc2read.variables["time"][:] + 25
						r_Tair = nc2read.variables["Tair"][:]
					if i == 2:
						r_lat = nc2read.variables["lat"][:] 
						r_lon = nc2read.variables["lon"][:]
						r_time = nc2read.variables["time"][:] + 50
						r_Tair = nc2read.variables["Tair"][:]
			# test = nc2read.variables[varname][:,:,:]
			# print(test)

					time_a.append(r_time)
					lon_a = r_lon
					lat_a = r_lat
					Tair_a.append(r_Tair)

			lon_data = np.array(lon_a)
			lat_data = np.array(lat_a)
			time_data = np.array(time_a)
			Tair_data = np.array(Tair_a)

			lon_re = lon_data.reshape(358)
			lat_re = lat_data.reshape(358)
			time_re = time_data.reshape(75)
			Tair_re = Tair_data.reshape(75,358,358)
			
			lon_u = nc2read.dimensions['lon']
			lat_u = nc2read.dimensions['lat']

			w_ncp = netCDF4.Dataset(find_path + '/' + 'concat_wrf_wrfdm2_' + (file_today + datetime.timedelta(days=0)).strftime('%Y%m%d%H') + '-' + (file_today + datetime.timedelta(days=2)).strftime('%Y%m%d%H') + '_Tair_regrid_merge.nc', 'w')
			w_ncp.createDimension('time', time_re.shape[0])
			w_ncp.createDimension('lon_u', lon_u.size)
			w_ncp.createDimension('lat_u', lat_u.size)

			lon = w_ncp.createVariable('lon', 'd', ('lon_u'))
			lat = w_ncp.createVariable('lat', 'd', ('lat_u'))
			time = w_ncp.createVariable('time', 'd', ('time'))
			Tair = w_ncp.createVariable('Tair', 'f', ('time', 'lat_u', 'lon_u'), fill_value=9.96921E36)

			lon[:] = lon_re
			lat[:] = lat_re
			time[:] = time_re
			Tair[:] = Tair_re

			year = date[0:4] 
			month = date[4:6]
			day = date[6:8]
			hour = date[8:10]
			print(f"hours since {year}-{month}-{day} {hour}:00:00")
			# datum = datetime(1968,5,23,0,0,0)
			# new_datum = datum + timedelta(seconds = r_time[0])
			# new_datum_str = 'hours since %s' % new_datum.strftime("%Y-%m-%d %H:%M:%S")
			# yyyymmddhh = new_datum.strftime("%Y%m%d%H")

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

			vout_long_name = "2 metre temperature"
			vout_units = "Celcius"
			vout_time = "time"
			vout_remap = "remapped via ESMF_regrid_with_weights: Bilinear"

			Tair.long_name = vout_long_name
			Tair.time = vout_time
			Tair.units = vout_units
			Tair.remap = vout_remap
			w_ncp.close()


if __name__ == "__main__":
		filepath = sys.argv[1]
		concat_merge_tair(filepath)