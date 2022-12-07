#!/usr/bin/python3.6

import os
from sys import argv
import sys
import netCDF4
import numpy as np
import datetime

def u2rho(u):
    dims = u.shape
    dimY = dims[-2]
    dimX = dims[-1]
    ur = np.zeros([dims[0], dimY, dimX + 1], dtype=float)
    # ur[:, 1:dimX] = 0.5 * (u[:, :dimX - 1] + u[:, :, 1:dimX])
    # 20220802 원태찬 오류가 나서 수정
    ur[:, :, 1:dimX] = 0.5 * (u[:, :, :dimX - 1] + u[:, :, 1:dimX]) 
    ur[:, :, 0] = ur[:, :, 1]
    ur[:, :, dimX] = ur[:, :, dimX - 1]
    return ur

def v2rho(v):
    dims = v.shape
    dimY=dims[-2]
    dimX=dims[-1]
    vr = np.zeros([dims[0],dimY+1,dimX])
    vr[:,1:dimY,:] = 0.5*(v[:,:dimY-1,:]+v[:,1:dimY,:])
    vr[:,0,:] = vr[:,1,:]
    vr[:,dimY,:] = vr[:,dimY-1,:]
    return vr

def mask2ndarray(vin):
    vin.set_fill_value(0)
    vout = vin.filled()
    return vout

def extract_all(filepath, varname, time):
    nc = netCDF4.Dataset(filepath)
    src_lat_rho = nc.variables["lat"][:,:] 
    src_lon_rho = nc.variables["lon"][:,:]
    src_ocean_time = nc.variables["tim"][:]
    
    if varname == "Hsig":
        varname2 = "Hs"
        vout = nc.variables[varname2][:,:,:]
        vout_long_name = 'Significant Wave Height'
        vout_units = 'm'
        
    elif varname == "Rpeak":
        varname2 = "Tm"
        vout = nc.variables[varname2][:,:,:]
        vout_long_name = 'Mean Period T02'
        vout_units = 'sec'

    elif varname == "Wdir":
        varname2 = "wdir"
        vout = nc.variables[varname2][:,:,:]
        vout_long_name = 'Wave Mean Direction'
        vout_units = 'degree'

    else:
        sys.exit()

  
    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    yyyymmdd = filename_without_ext[-10:]
    start_date = datetime.datetime.strptime(yyyymmdd,"%Y%m%d%H")
    new_datum_str = 'hours since %s' % start_date.strftime("%Y-%m-%d %H:%M:%S")
    
    path1 = os.path.split(filepath)
    path2 = os.path.split(path1[0])
    foldername = path2[1]
    modelname = os.path.basename(path2[0])

    extract_fname = '/DATA/PYTHON/output/extract/extract_all_%s_%s_%s_%02d.nc'% \
                    (foldername.lower(),yyyymmdd,varname,int(time))
    nc2write = netCDF4.Dataset(extract_fname, mode='w', format="NETCDF3_CLASSIC")

    nc2write.createDimension('ocean_time', None)
    nc2write.createDimension('xi_rho', size = src_lon_rho.shape[1])
    nc2write.createDimension('eta_rho', size = src_lat_rho.shape[0])

    var=nc2write.createVariable(varname,'f',('ocean_time','eta_rho','xi_rho'),fill_value=1.0E37)
    lat_rho=nc2write.createVariable('lat_rho','d',('eta_rho','xi_rho'))
    lon_rho=nc2write.createVariable('lon_rho','d',('eta_rho','xi_rho'))
    ocean_time=nc2write.createVariable('ocean_time','d','ocean_time')

    lat_rho[:,:] = src_lat_rho[:,:]
    lon_rho[:,:] = src_lon_rho[:,:]
    ocean_time[0] = src_ocean_time[int(time)]
    var[0,:,:] = vout[int(time),:,:]

    lon_rho.long_name = 'Longitude'
    lon_rho.units = 'Degree_East'
    lon_rho._CoordinateAxisType = "Lon"

    lat_rho.long_name = 'Latitude'
    lat_rho.units = 'Degree_North'
    lat_rho._CoordinateAxisType = "Lat"

    ocean_time.long_name = 'Julian Day'
    ocean_time.units = new_datum_str

    var.long_name = vout_long_name
    var.units = vout_units
    var.time = 'ocean_time'
    var.coordinates = 'lon_rho lat_rho ocean_time'

    nc2write.close()

    return extract_fname

if __name__ == "__main__":
    extract_fname = extract_all(argv[1],argv[2],argv[3])

