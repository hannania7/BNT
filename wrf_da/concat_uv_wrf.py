#!/usr/bin/python3.6

# time all 2022.7.1 원태찬 구분하기 위해 주석달음(windu, windv구함)

import os
from sys import argv
import sys
import netCDF4
import numpy as np
import datetime

def concat_uv(filepath):

    # output 폴더가 없으면 생성
    if not os.path.exists('/DATA/PYTHON+NCL/output/wrf_da'):
        os.makedirs('/DATA/PYTHON+NCL/output/wrf_da')  
    
    nc2read = netCDF4.Dataset(filepath)
    r_lat = nc2read.variables["lat_rho"][:] 
    r_lon = nc2read.variables["lon_rho"][:]
    r_time = nc2read.variables["ocean_time"][:]
    eta_rho = nc2read.dimensions['eta_rho'].size
    xi_rho = nc2read.dimensions['xi_rho'].size
    vin1 = nc2read.variables["Uwind"][:,:,:]
    vout1_long_name = "WRF (10m) u winds [m/s]"
    vout1_units = "meter second-1"
    vout1_time = "ocean_time"
    # vout1_remap = "remapped via ESMF_regrid_with_weights: Bilinear"

    vin2 = nc2read.variables["Vwind"][:,:,:]
    vout2_long_name = "WRF (10m) v winds [m/s]"
    vout2_units = "meter second-1"
    vout2_time = "ocean_time"
    # vout2_remap = "remapped via ESMF_regrid_with_weights: Bilinear"

    find_date = os.path.basename(filepath)
    date = find_date.split('_')[1].split('.')[0]
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    # hour = date[8:10]
    print(f"hours since {year}-{month}-{day} 00:00:00")

    # datum = datetime(1968,5,23,0,0,0)
    # new_datum = datum + timedelta(seconds = r_time[0])
    # new_datum_str = 'hours since %s' % new_datum.strftime("%Y-%m-%d %H:%M:%S")
    # yyyymmddhh = new_datum.strftime("%Y%m%d%H")

    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    wrfdm = filename_without_ext.split('_')[0]
    
    path = os.path.split(filepath)
    modelname = os.path.basename(path[0])

    [t] = np.shape(r_time[:])
    new_ocean_time =[]
    for t_step in range(t):
        t_step = float(t_step)
        new_ocean_time.append(t_step)
    
    filename_with_ext = os.path.basename(filepath)
    d_type = filename_with_ext.split('_')[0]
    if d_type == 'wrfdm1':
        wrfdm = 'wrfdm1'
    elif d_type == 'wrfdm2':
        wrfdm = 'wrfdm2'

    concat_fname = '/DATA/PYTHON+NCL/output/wrf_da/concat_%s_%s_%s_uv.nc'% \
                   ("wrf_da",wrfdm,date)

    nc2write = netCDF4.Dataset(concat_fname, mode='w')
    nc2write.createDimension('ocean_time', None)
    nc2write.createDimension('eta_rho', size = eta_rho)
    nc2write.createDimension('xi_rho', size = xi_rho)

    ocean_time=nc2write.createVariable('ocean_time','d','ocean_time')
    lon_rho=nc2write.createVariable('lon_rho','d',('eta_rho', 'xi_rho'))
    lat_rho=nc2write.createVariable('lat_rho','d',('eta_rho', 'xi_rho'))
    Uwind=nc2write.createVariable("Uwind",'f',('ocean_time','eta_rho', 'xi_rho'), fill_value = 9.96921E36)
    Vwind=nc2write.createVariable("Vwind",'f',('ocean_time','eta_rho', 'xi_rho'), fill_value = 9.96921E36)  

    lat_rho[:] = r_lat[:]
    lon_rho[:] = r_lon[:]
    # for i in range(0,25):
    #     new_ocean_time[i] = new_ocean_time[i] + int(count) * 25
    ocean_time[:] = new_ocean_time[:]
    Uwind[:,:,:] = vin1[:,:,:]
    Vwind[:,:,:] = vin2[:,:,:]

    ocean_time.field = "time, scalar, series"
    ocean_time.units = f"hours since {year}-{month}-{day} 00:00:00"
    ocean_time.calendar = "gregorian"
    ocean_time.long_name = "time since initialization"
    ocean_time._CoordinateAxisType = 'Time'

    lon_rho.long_name = "longitude of RHO-points"
    lon_rho.field = "time, scalar, series"
    lon_rho.standard_name = "longitude"
    lon_rho.units = "degrees_east"
    lon_rho._CoordinateAxisType = "Lon"

    lat_rho.long_name = "latitude of RHO-points"
    lat_rho.standard_name = "latitude"
    lat_rho.units = "degrees_north"
    lat_rho.field = "lat_rho, scalar"
    lat_rho._CoordinateAxisType = "Lat"

    Uwind.long_name = vout1_long_name
    Uwind.units = vout1_units
    Uwind.time = vout1_time
    # Uwind.remap = vout1_remap
    
    Vwind.long_name = vout2_long_name
    Vwind.units = vout2_units
    Vwind.time = vout2_time
    # Vwind.remap = vout2_remap

    nc2write.close()

    return concat_fname

if __name__ == "__main__":
    concat_fname = concat_uv(argv[1])
