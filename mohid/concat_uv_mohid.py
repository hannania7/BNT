# -*- coding: utf-8 -*-

import os
from sys import argv
import sys
import netCDF4
import numpy as np
from datetime import datetime, timedelta

def concat_uv_mohid(filepath, s_rho):

    # output 폴더가 없으면 생성
    if not os.path.exists('/DATA/PYTHON/output/mohid'):
        os.makedirs('/DATA/PYTHON/output/mohid')    
    
    nc2read = netCDF4.Dataset(filepath)
    src_lat = nc2read.variables["lat"][:] 
    src_lon = nc2read.variables["lon"][:]
    src_time = nc2read.variables["time"][:]
       
    vout1 = nc2read.variables["u"][:,int(s_rho),:,:]
    vout1_long_name = 'sea surface u-momentum component'
    vout1_units = 'meter second-1'
    vout1_time='ocean_time'
    vout1_coordinates = 'lon lat time'
        
    vout2 = nc2read.variables["v"][:,int(s_rho),:,:]
    vout2_long_name = 'sea surface v-momentum component'
    vout2_units = 'meter second-1'
    vout2_time='time'
    vout2_coordinates = 'lon lat time'

    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    yyyymmdd12 = filename_without_ext[-10:]
    start_date = datetime.strptime(yyyymmdd12,"%Y%m%d%H")
    new_datum_str = 'hours since %s' % start_date.strftime("%Y-%m-%d %H:%M:%S")

    path1 = os.path.split(filepath)
    path2 = os.path.split(path1[0])
    foldername = path2[1]

    [t] = np.shape(src_time[:])
    new_time =[]
    for t_step in range(t):
        t_step = float(t_step)
        new_time.append(t_step)

    concat_fname = '/DATA/PYTHON/output/mohid/concat_%s_%s_uv_%s.nc'% \
                   (foldername.lower(),yyyymmdd12,s_rho)

    nc2write = netCDF4.Dataset(concat_fname, mode='w', format="NETCDF3_CLASSIC")

    nc2write.createDimension('time', None)
    nc2write.createDimension('lon', size = src_lon.shape[0])
    nc2write.createDimension('lat', size = src_lat.shape[0])

    u=nc2write.createVariable("u",'f',('time','lat','lon'),fill_value=-99.9)
    v=nc2write.createVariable("v",'f',('time','lat','lon'),fill_value=-99.9)
    lat=nc2write.createVariable('lat','d','lat')
    lon=nc2write.createVariable('lon','d','lon')
    time=nc2write.createVariable('time','d','time')

    lat[:] = src_lat[:]
    lon[:] = src_lon[:]
    time[:] = new_time[:]
    u[:,:,:] = vout1[:,:,:]
    v[:,:,:] = vout2[:,:,:]

    lon.long_name = 'longitude'
    lon.units = 'degree_east'
    lon.standard_names = 'longitude'

    lat.long_name = 'latitude'
    lat.units = 'degree_north'
    lat.standard_names = 'latitude'

    time.long_name = 'time since initialization'
    time.units = new_datum_str

    u.long_name = vout1_long_name
    u.units = vout1_units
    u.time= vout1_time
    u.coordinates = vout1_coordinates

    v.long_name = vout2_long_name
    v.units = vout2_units
    v.time= vout2_time
    v.coordinates = vout2_coordinates
    
    nc2write.close()

    return

if __name__ == "__main__":
    
    concat_uv_mohid(argv[1], argv[2])
