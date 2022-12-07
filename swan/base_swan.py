#!/usr/bin/python3.6

import os
from sys import argv
import sys
import netCDF4
import numpy as np
from datetime import datetime, timedelta

def base(filepath,varname,timestep):

    # output 폴더가 없으면 생성
    if not os.path.exists('/DATA/PYTHON+NCL/output/swan'):
        os.makedirs('/DATA/PYTHON+NCL/output/swan')  

    nc2read = netCDF4.Dataset(filepath)
    src_lat_rho = nc2read.variables["lat"][:,:] 
    src_lon_rho = nc2read.variables["lon"][:,:]
       
    if varname == "Hsig":
        varname2 = "Hs"
        vout = nc2read.variables[varname2][:,:,:]
        vout_long_name = 'Significant Wave Height'
        vout_units = 'm'
        
    elif varname == "Rpeak":
        varname2 = "Tm"
        vout = nc2read.variables[varname2][:,:,:]
        vout_long_name = 'Mean Period T02'
        vout_units = 'sec'

    elif varname == "Wdir":
        varname2 = "wdir"
        vout = nc2read.variables[varname2][:,:,:]
        vout_long_name = 'Wave Mean Direction'
        vout_units = 'degree'

    else:
        sys.exit()
    
    vout[np.isnan(vout)] = 1.0E37
    vout=np.ma.masked_where(vout<-998,vout)

    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    yyyymmdd = filename_without_ext[-10:]
    start_date = datetime.strptime(yyyymmdd,"%Y%m%d%H")
    new_datum_str = 'hours since %s' % start_date.strftime("%Y-%m-%d %H:%M:%S")
    
    #new_datum_str = 'matlab date format'
    
    modelname = "swan"
    print(varname2)
    base_fname = '/DATA/PYTHON+NCL/output/swan/base_%s_%s+%04d_%s.nc'% \
                   (modelname,yyyymmdd,int(timestep),varname)

    nc2write = netCDF4.Dataset(base_fname, mode='w', format="NETCDF3_CLASSIC")
    nc2write.createDimension('ocean_time', None)
    nc2write.createDimension('lon', size = src_lon_rho.shape[1])
    nc2write.createDimension('lat', size = src_lat_rho.shape[0])

    var=nc2write.createVariable(varname,'d',('ocean_time','lat','lon'),fill_value=1.0E37)
    lat_rho=nc2write.createVariable('lat_rho','d',('lat','lon'))
    lon_rho=nc2write.createVariable('lon_rho','d',('lat','lon'))
    ocean_time=nc2write.createVariable('ocean_time','d','ocean_time')

    lat_rho[:,:] = src_lat_rho[:,:]
    lon_rho[:,:] = src_lon_rho[:,:]
    ocean_time[:] = int(timestep)
    var[0,:,:] = vout[int(timestep),:,:]

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

    return base_fname

if __name__ == "__main__":
    base_fname = base(argv[1], argv[2], argv[3])
