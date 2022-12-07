# -*- coding: utf-8 -*-

import os
import sys

from datetime import datetime, timedelta

import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import ast


def find_thenearest_grd_pts(lat_array, lon_array, latitude, longitude):
    '''
    Find the nearerest grid point that is close to the user specified lat lon
    '''
    lon = lon_array[:] - float(longitude)
    lat = lat_array[:] - float(latitude)
    j_indices = np.where(lat.min())
    i_indices = np.where(lon.min())
    j = j_indices[0]
    i = i_indices[0]
    return j, i


def get_theta(a1, a2, b1, b2):
    '''
    Compute counterclockwise angle (in radians) between two non intersecting lines
    '''
    line1 = np.array(a2) - np.array(a1)
    line2 = np.array(b2) - np.array(b1)
    theta = np.math.atan2(np.linalg.det([line1, line2]), np.dot(line1, line2))

    if theta < 0:
        theta = theta + 2*np.pi
    return theta


def main(filepath, varname, latmin, lonmin, latmax, lonmax, cflevels, time):

    ncp = netCDF4.Dataset(filepath, mode='r')
    src_lat = ncp.variables['lat'][:]
    src_lon = ncp.variables['lon'][:]
    src_time = ncp.variables['time'][:]
    src_bath = ncp.variables['bathymetry'][:]
    src_vertical = ncp.variables['verticalinfo'][time, :, :, :]

    time_num = src_time[int(time)]

    if varname == 'u':
        var_array = ncp.variables['u'][time, :, :, :]
        vout1_long_name = 'sea surface u-momentum component'
        vout1_units = 'meter second-1'
        vout1_time = 'ocean_time'
        vout1_coordinates = 'lon lat time'
        fullvarname = 'U velocity[m/s]'
    elif varname == 'v':
        var_array = ncp.variables['v'][time, :, :, :]
        vout2_long_name = 'sea surface v-momentum component'
        vout2_units = 'meter second-1'
        vout2_time = 'time'
        vout2_coordinates = 'lon lat time'
        fullvarname = 'V velocity[m/s]'
    elif varname == 'temp':
        var_array = ncp.variables['temp'][time, :, :, :]
        vout_long_name = 'potential temperature'
        vout_units = 'Celcius'
        vout_time = 'time'
        vout_coordinates = 'lon lat time'
        fullvarname = 'Temperature'+'['+u"\u2103"+']'
    elif varname == 'sali':
        var_array = ncp.variables['salt'][time, :, :, :]
        vout_long_name = 'salinity'
        vout_units = 'psu'
        vout_time = 'time'
        vout_coordinates = 'lon lat time'
        fullvarname = 'Salinity[psu]'
    else:
        sys.exit('wrong_var_name_type')

    # Get x steps and y steps
    dl = (np.gradient(src_lon)[1].mean() + np.gradient(src_lat)[0].mean()) / 2
    siz = int(np.sqrt((float(latmax) - float(latmin))**2 +
                      (float(lonmax) - float(lonmin))**2) / dl)
    xs = np.linspace(float(lonmin), float(lonmax), siz)
    ys = np.linspace(float(latmin), float(latmax), siz)

    M = xs.size
    depth = np.zeros([40, M])
    line = np.zeros([40, M])
    var = np.zeros([40, M])
    var_u = np.zeros([40, M])
    var_v = np.zeros([40, M])
    j_ind = np.zeros([M])
    i_ind = np.zeros([M])


    # Extract along the line
    for ind in range(xs.size):
        j, i = find_thenearest_grd_pts(src_lat, src_lon, ys[ind], xs[ind])
        j_ind[ind] = j
        i_ind[ind] = i
        depth[:, ind] = src_vertical[:,j,i].reshape(-1)
        line[:, ind] = xs[ind]
        var[:, ind] = var_array[:, j, i].reshape(-1)

        if varname == 'u' or varname == 'v':
            var_u[:, ind] = var_array[:, j, i].flatten()
            var_v[:, ind] = var_array[:, j, i].flatten()
    j_ind = np.int64(j_ind)
    i_ind = np.int64(i_ind)

    # Calculate counterclockwise angle between the +u axis and the line
    a1 = [src_lon[0], src_lat[0]]
    a2 = [src_lon[0], src_lat[0]]
    b1 = [src_lon[i_ind[0]], src_lat[j_ind[0]]]
    b2 = [src_lon[i_ind[-1]], src_lat[j_ind[-1]]]
    theta = get_theta(a1, a2, b1, b2)

    if varname == 'temp':
        var = var
    elif varname == 'salt':
        var = var
    if varname == 'u':
        var = var_u * np.cos(theta) + var_v * np.sin(theta)
    if varname == 'v':
        var = - var_u * np.sin(theta) + var_v * np.cos(theta)

    var = np.ma.masked_where( var > 1000, var)


	# Get names ...
    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    last4digit = filename_without_ext[-4:]
    path1 = os.path.split(filepath)
    path2 = os.path.split(path1[0])
    foldername = path2[1]
    modelname = os.path.basename(path2[0])

    # Contour levels
    cflev = ast.literal_eval(sys.argv[7])
    cflev = np.arange(cflev[0], cflev[1], cflev[2])

    # Plot
    fig, ax = plt.subplots(figsize=[12, 6])
    print(line.shape)
    print(depth.shape)
    print(var.shape)
    CF = plt.contourf(line, depth, var, levels=cflev, extend='both', origin='upper')
    plt.colorbar(CF, orientation="horizontal", pad=0.07)
    C = plt.contour(line, depth, var, colors='k', levels=cflev)
    plt.clabel(C, fmt='%1.2f', colors='w')
    plt.ylabel('Depth[m]')
    plt.title('Vertical slice along the user-specified line', loc='center')
    plt.annotate(fullvarname, (1, 0), (0, -10),
                 xycoords='axes fraction', textcoords='offset points',
                 va='center', ha='right')
    # plt.annotate(datetime.strftime(time_num, '%Y-%m-%d %H:%M'),
    #              (0, 0), (0, -10),
    #              xycoords='axes fraction', textcoords='offset points',
    #              va='center', ha='left')
    plt.gca().patch.set_color('peru')
    ax.set_xticklabels([])
    ax.set_xticks([])

    # Save figure
    plt.savefig('/DATA/PYTHON/output/mohid2k/vslice/png/vslice_%s_%s_%s_%s_(%s,%s)_(%s,%s)_%s.png' % \
                (modelname.lower(), foldername, last4digit, varname, \
                 latmin, lonmin, latmax, lonmax, cflevels), bbox_inches='tight')



if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])