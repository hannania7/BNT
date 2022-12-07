# -*- coding: utf-8 -*-


import os
import sys
import netCDF4
from datetime import datetime
import numpy as np


def find_near_array(array, point):
    result_value = np.abs(array[0] - point)
    for cal_index, content in enumerate(array):
        cal_result = np.abs(content - point)
        if result_value >= cal_result:
            (result_value, result_index) = (cal_result, cal_index)
            result_content = content
    return result_content, result_index


def main(filepath,varname,s_rho, latmin, lonmin, latmax, lonmax, time):
    # init
    s_rho = int(s_rho)
    time = int(time)

    ncp = netCDF4.Dataset(filepath, mode ='r')
    src_lat = ncp.variables['lat'][:]
    src_lon = ncp.variables['lon'][:]
    src_time = ncp.variables['time'][:]
    src_bath = ncp.variables['bathymetry'][:]
    src_vertical = ncp.variables['verticalinfo'][time, :, :, :]
    src_ocean_time = ncp.variables["time"][:]

    # right up point, left down point boxing calculate
    _, l_lat_index = find_near_array(src_lat, float(latmin))
    _, l_lon_index = find_near_array(src_lon, float(lonmin))
    _, r_lat_index = find_near_array(src_lat, float(latmax))
    _, r_lon_index = find_near_array(src_lon, float(lonmax))

    #split
    src_lat = src_lat[l_lat_index:r_lat_index]
    src_lon = src_lon[l_lon_index:r_lon_index]

    if varname == 'u':
        var_array = ncp.variables['u'][time, s_rho, l_lat_index:r_lat_index, l_lon_index:r_lon_index]
        vout_long_name = 'sea surface u-momentum component'
        vout_units = 'meter second-1'
        vout_time = 'ocean_time'
        vout_coordinates = 'lon lat time'
    elif varname == 'v':
        var_array = ncp.variables['v'][time, s_rho, l_lat_index:r_lat_index, l_lon_index:r_lon_index]
        vout_long_name = 'sea surface v-momentum component'
        vout_units = 'meter second-1'
        vout_time = 'time'
        vout_coordinates = 'lon lat time'
    elif varname == 'temp':
        var_array = ncp.variables['temp'][time, s_rho, l_lat_index:r_lat_index, l_lon_index:r_lon_index]
        vout_long_name = 'potential temperature'
        vout_units = 'Celcius'
        vout_time='time'
        vout_coordinates = 'lon lat time'
    elif varname == 'sali':
        var_array = ncp.variables['salt'][time, s_rho, l_lat_index:r_lat_index, l_lon_index:r_lon_index]
        vout_long_name = 'salinity'
        vout_units = 'psu'
        vout_time='time'
        vout_coordinates = 'lon lat time'
    else:
        sys.exit('wrong_var_name_type')

    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    yyyymmdd12 = filename_without_ext[-10:]


    path1 = os.path.split(filepath)
    path2 = os.path.split(path1[0])
    foldername = path2[1]
    modelname = os.path.basename(path2[0])

    extract_fname = '/DATA/PYTHON/output/mohid/extract/extract_bbox_%s_%s_%s_%s_%s,%s,%s,%s_%02d.nc' % \
                    (foldername.lower(), yyyymmdd12, varname, s_rho, latmin, lonmin, latmax, lonmax, int(time))

    nc2write = netCDF4.Dataset(extract_fname, mode='w', format="NETCDF3_CLASSIC")
    nc2write.createDimension('ocean_time', None)
    nc2write.createDimension('lat_rho', size = src_lat.shape[0])
    nc2write.createDimension('lon_rho', size = src_lon.shape[0])

    var=nc2write.createVariable(varname,'f',('ocean_time','lat_rho','lon_rho'),fill_value=1.0E37)
    lat_rho=nc2write.createVariable('lat_rho','d','lat_rho')
    lon_rho=nc2write.createVariable('lon_rho','d','lon_rho')
    ocean_time=nc2write.createVariable('ocean_time','d','ocean_time')

    lat_rho[:] = src_lat[:]
    lon_rho[:] = src_lon[:]
    ocean_time[:] = src_ocean_time[time]
    var[:,:,:] = var_array[:]

    lon_rho.long_name = 'longitude at RHO-points'
    lon_rho.units = 'degree_east'
    lon_rho.standard_names = 'longitude'
    lon_rho.field = 'lon_rho, scalar'
    lat_rho.long_name = 'latitude at RHO-points'
    lat_rho.units = 'degree_north'
    lat_rho.standard_names = 'latitude'
    ocean_time.long_name = 'time since initialization'
    ocean_time.units = 'seconds since 1968-05-23 00:00:00 GMT'
    ocean_time.field = 'time, scalar, series'
    var.long_name = vout_long_name
    var.units = vout_units
    var.time= vout_time
    var.coordinates = vout_coordinates


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])



