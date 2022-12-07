# -*- coding: utf-8 -*-


import datetime
import re
import sys
import os
import ast

import netCDF4
import numpy as np
import matplotlib.pyplot as plt


def find_near_array(array, point):
    result_value = np.abs(array[0] - point)
    for cal_index, content in enumerate(array):
        cal_result = np.abs(content - point)
        if result_value >= cal_result:
            (result_value, result_index) = (cal_result, cal_index)
            result_content = content
    return result_content, result_index


def vprofile(filepath, varname, latitude, longitude, xrange, time):
    ncp = netCDF4.Dataset(filepath, mode= 'r')
    lat_rho = ncp.variables['lat'][:]
    lon_rho = ncp.variables['lon'][:]
    bathymetry = ncp.variables['bathymetry'][:]

    # time parsing
    # number_string example = ['_2020040112']
    number_string = os.path.basename(filepath)
    number_string = number_string.split('_')[2]
    ocean_time = datetime.datetime(year=int(number_string[0:4]), month=int(number_string[4:6]),
                                   day=int(number_string[6:8]), hour=int(number_string[8:10]))
    cal_ocean_time = ocean_time + datetime.timedelta(hours= (int(time) * 3))

    # find near array lon lat
    _, lat_near_index = find_near_array(lat_rho, float(latitude))
    _, lon_near_index = find_near_array(lon_rho, float(longitude))

    # variable parsing
    if varname == 'sali':
        xunit = '[psu]'
        xlabel = 'Salinity' + xunit
        var = ncp.variables['salt'][int(time), :, lat_near_index, lon_near_index]
    elif varname == 'temp':
        xunit = '[℃]'
        xlabel = 'Temperature' + xunit
        var = ncp.variables['temp'][int(time), :, lat_near_index, lon_near_index]
    elif varname == 'u':
        xunit = '[m/s]'
        xlabel = 'U velocitiy' + xunit
        var = ncp.variables['u'][int(time), :, lat_near_index, lon_near_index]
    elif varname == 'v':
        xunit = '[m/s]'
        xlabel = 'V velocitiy' + xunit
        var = ncp.variables['v'][int(time), :, lat_near_index, lon_near_index]
    else:
        sys.exit()
    x_lim = ast.literal_eval(xrange)

    # depth parsing
    depth = ncp.variables['verticalinfo'][int(time), :, lat_near_index, lon_near_index]
    depth = depth[depth > -500]
    depth = -depth
    # var parsing
    var = var[var > -500]

    # check var, depth len
    if len(var) > len(depth):
        var = var[:len(depth)]
    if len(var) < len(depth):
        depth = depth[:len(var)]

    # file_name parsing
    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    last4digit = filename_without_ext[-4:]

    path1 = os.path.split(filepath)
    path2 = os.path.split(path1[0])
    foldername = path2[1]
    modelname = os.path.basename(path2[0])

    # matplot draw
    fig, ax = plt.subplots(figsize=[6, 5])
    ax.set_title(datetime.datetime.strftime(cal_ocean_time, '%Y-%m-%d %H:%M'), loc='left')
    ax.set_title(str(round(float(latitude), 4)) + 'N' + ',' +
                 str(round(float(longitude), 4)) + 'E', loc='right')
    ax.plot(var, depth, 'k-')
    ax.set_ylabel('Depth[m]')
    ax.set_xlabel(xlabel)
    ax.xaxis.tick_bottom()
    ax.xaxis.set_label_position('bottom')
    ax.set_xticks(np.arange(x_lim[0], x_lim[1]+0.1, x_lim[2]))
    ax.set_ylim(min(depth), 0)

    xrange_str = ''.join(xrange).replace('[', '').replace(']', '').split(',')

    plt.savefig('/DATA/PYTHON/output/mohid/vprofile/png/vprofile_%s_%s_%s_%s,%s_%s,%s,%s_%02d.png' % \
                (foldername.lower(), ocean_time.strftime("%Y%m%d%H"), varname, latitude, longitude,
                 xrange_str[0], xrange_str[1], xrange_str[2], int(time)), \
                bbox_inches='tight', dpi=300)

    with open('/DATA/PYTHON/output/mohid/vprofile/txt/vprofile_%s_%s_%s_%s,%s_%s,%s,%s_%02d.txt' % \
              (foldername.lower(), ocean_time.strftime("%Y%m%d%H"), varname, latitude, longitude,
               xrange_str[0], xrange_str[1], xrange_str[2], int(time)), "w") as ft:
        ft.write("%s\t%s\n" % ("depth[m] ", varname + xunit))
        for y in range(len(depth)):
            ft.write("%0.7f\t%0.7f" % (depth[y], var[y]))
            ft.write("\n")


if __name__ == "__main__":
    vprofile(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])