#!/usr/bin/python3.6

# time all 2022.7.1 원태찬 구분하기 위해 주석달음(apress, atemp구함)

import os
from sys import argv
import sys
import netCDF4 
import numpy as np  
import datetime
 
def concat(filepath,varname):
    # output 폴더가 없으면 생성
    if not os.path.exists('/DATA/PYTHON+NCL/output/wrf_da'):
        os.makedirs('/DATA/PYTHON+NCL/output/wrf_da')  
    
    nc2read = netCDF4.Dataset(filepath)
    r_lat = nc2read.variables["lat_rho"][:] 
    r_lon = nc2read.variables["lon_rho"][:]
    r_time = nc2read.variables["ocean_time"][:]
    eta_rho = nc2read.dimensions['eta_rho'].size
    xi_rho = nc2read.dimensions['xi_rho'].size
    # test = nc2read.variables[varname][:,:,:]
    # print(test)
    sepa_filepath = os.path.basename(filepath).split('_')[1]
    vout_append = list()   
    if varname == "Pair":
        vout_result = nc2read.variables[varname][:] / 100
        vout_long_name = "sea level air pressure"
        vout_units = "bar"
        vout_time = "time"
        vout_remap = "remapped via ESMF_regrid_with_weights: Bilinear"

    elif varname == "Tair":
        vout_result = nc2read.variables[varname][:,:,:]
        vout_long_name = "2 metre temperature"
        vout_units = "Celcius"
        vout_time = "time"
        vout_remap = "remapped via ESMF_regrid_with_weights: Bilinear"
            
    else:
        sys.exit()        

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

    concat_fname = '/DATA/PYTHON+NCL/output/wrf_da/concat_%s_%s_%s_%s.nc'% \
                   ("wrf_da",wrfdm,date,varname)

    nc2write = netCDF4.Dataset(concat_fname, mode='w')
    nc2write.createDimension('ocean_time', None)
    nc2write.createDimension('eta_rho', size = eta_rho)
    nc2write.createDimension('xi_rho', size = xi_rho)

    ocean_time=nc2write.createVariable('ocean_time','d','ocean_time')
    lon_rho=nc2write.createVariable('lon_rho','d',('eta_rho', 'xi_rho'))
    lat_rho=nc2write.createVariable('lat_rho','d',('eta_rho', 'xi_rho'))
    var=nc2write.createVariable(varname,'f',('ocean_time','eta_rho', 'xi_rho'), fill_value = 9.96921E36)

    lon_rho[:] = r_lon[:]
    lat_rho[:] = r_lat[:]
    # for i in range(0,25):
    #     new_ocean_time[i] = new_ocean_time[i] + int(count) * 25
    ocean_time[:] = new_ocean_time[:]
    var[:,:,:] = vout_result[:,:,:]    

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

    var.long_name = vout_long_name
    var.time = vout_time
    var.units = vout_units
    # var.remap = vout_remap
    if varname == 'Pair':
        var._CoordinateAxisType = "Pressure"
    nc2write.close()

    return concat_fname

if __name__ == "__main__":
    concat_fname = concat(argv[1], argv[2])
