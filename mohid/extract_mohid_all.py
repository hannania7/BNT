# -*- coding: utf-8 -*-

import os
from sys import argv
import sys
import netCDF4
import numpy as np
from datetime import datetime, timedelta


def base_mohid(filepath, varname, s_rho, timestep):
    # output 폴더가 없으면 생성
    if not os.path.exists('/DATA/PYTHON/output/mohid'):
        os.makedirs('/DATA/PYTHON/output/mohid')

    nc2read = netCDF4.Dataset(filepath)
    src_lat = nc2read.variables["lat"][:]
    src_lon = nc2read.variables["lon"][:]
    src_time = nc2read.variables["time"][:]

    if varname == "u":
        vout = nc2read.variables[varname][int(timestep), int(s_rho), :, :]
        vout_long_name = 'sea surface u-momentum component'
        vout_units = 'meter second-1'
        vout_time = 'time'
        vout_coordinates = 'lon lat time'
    elif varname == "v":
        vout = nc2read.variables[varname][int(timestep), int(s_rho), :, :]
        vout_long_name = 'sea surface u-momentum component'
        vout_units = 'meter second-1'
        vout_time = 'time'
        vout_coordinates = 'lon lat time'
    elif varname == "temp":
        vout = nc2read.variables[varname][int(timestep), int(s_rho), :, :]
        vout_long_name = 'potential temperature'
        vout_units = 'Celcius'
        vout_time = 'time'
        vout_coordinates = 'lon lat time'
    elif varname == "sali":
        vout = nc2read.variables['salt'][int(timestep), int(s_rho), :, :]
        vout_long_name = 'salinity'
        vout_units = 'psu'
        vout_time = 'time'
        vout_coordinates = 'lon lat time'
    else:
        print("The variable name is incorrect! Program halted")
        sys.exit()

    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    yyyymmdd12 = filename_without_ext[-10:]
    start_date = datetime.strptime(yyyymmdd12, "%Y%m%d%H")
    new_datum_str = 'hours since %s' % start_date.strftime("%Y-%m-%d %H:%M:%S")

    path1 = os.path.split(filepath)
    path2 = os.path.split(path1[0])
    foldername = path2[1]


    base_fname = '/DATA/PYTHON/output/mohid/extract/extract_all_%s_%s_%s_%02d_%02d.nc' % \
                 (foldername.lower(), yyyymmdd12, varname, int(s_rho), int(timestep))

    nc2write = netCDF4.Dataset(base_fname, mode='w', format="NETCDF3_CLASSIC")

    nc2write.createDimension('time', None)
    nc2write.createDimension('lon', size=src_lon.shape[0])
    nc2write.createDimension('lat', size=src_lat.shape[0])

    var = nc2write.createVariable(varname, 'f', ('time', 'lat', 'lon'), fill_value=-99.9)
    lat = nc2write.createVariable('lat', 'd', 'lat')
    lon = nc2write.createVariable('lon', 'd', 'lon')
    time = nc2write.createVariable('time', 'd', 'time')

    lat[:] = src_lat[:]
    lon[:] = src_lon[:]
    time[:] = int(timestep)

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
    var.time = vout_time
    var.coordinates = vout_coordinates

    nc2write.close()

    return


if __name__ == "__main__":
    base_mohid(*argv[1:])
