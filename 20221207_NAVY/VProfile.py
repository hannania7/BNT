# -*- coding: utf-8 -*-

import os
import sys
import ast
import datetime

import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import MakeFilePath


def find_near_array(array, point):
    result_value = np.abs(array[0] - point)
    for cal_index, content in enumerate(array):
        cal_result = np.abs(content - point)
        if result_value >= cal_result:
            (result_value, result_index) = (cal_result, cal_index)
            result_content = content
    return result_content, result_index


def find_thenearest_grd_pts(lat_array, lon_array, latitude, longitude):
    lon = lon_array[:, :] - float(longitude)
    lat = lat_array[:, :] - float(latitude)
    diff = (lon * lon) + (lat * lat)
    j_indices, i_indices = np.where(diff == diff.min())
    j = j_indices[0]
    i = i_indices[0]
    return j, i


def get_dimension_shape(nc_p):
    dimention_p = nc_p.dimensions
    return len(dimention_p['xi_rho']), len(dimention_p['eta_rho']), len(dimention_p['s_rho'])


def zlevel(zeta, Vtransform, h, hc, s_rho, Cs_r, nc_p):
    nx, ny, nz = get_dimension_shape(nc_p)
    z = np.zeros((nz, ny, nx))

    zeta = np.ma.filled(zeta, np.nan)

    if Vtransform == 1:
        for k in range(nz):
            S = hc * s_rho[k] + (h - hc) * Cs_r[k]
            z[k, :, :] = S + zeta * (1.0 + S / h)
    elif Vtransform == 2:
        for k in range(nz):
            S = (hc * s_rho[k] + h * Cs_r[k]) / (hc + h)
            z[k, :, :] = zeta + (zeta + h) * S
    else:
        print("The Vtransform value shoule be either 1 or 2")
        sys.exit()
    return z


def mohid_vprofile(file_name, date, varname, lonlat_array, xrange, time, v_profile_path):
    model = 'mohid300m'
    model_nc_path = MakeFilePath.get_mohid_vis_file_path(date)
    ncp = netCDF4.Dataset(model_nc_path, mode='r')
    lat_rho = ncp.variables['lat'][:]
    lon_rho = ncp.variables['lon'][:]
    bathymetry = ncp.variables['bathymetry'][:]

    # time parsing
    # number_string example = ['_2020040112']
    ocean_time = datetime.datetime(year=int(date[0:4]), month=int(date[4:6]),
                                   day=int(date[6:8]), hour=int(time))
    cal_ocean_time = ocean_time + datetime.timedelta(hours=-21)

    # variable parsing
    if varname == 'salt':
        xunit = '[psu]'
        xlabel = 'Salinity' + xunit
        var_array = ncp.variables['sail']
    elif varname == 'temp':
        xunit = '[℃]'
        xlabel = 'Temperature' + xunit
        var_array = ncp.variables['temp']
    elif varname == 'u':
        xunit = '[m/s]'
        xlabel = 'U velocitiy' + xunit
        var_array = ncp.variables['u']
    elif varname == 'v':
        xunit = '[m/s]'
        xlabel = 'V velocitiy' + xunit
        var_array = ncp.variables['v']
    else:
        sys.exit()

    # matplot draw
    fig, ax = plt.subplots(figsize=[6, 5])
    ax.set_title(datetime.datetime.strftime(cal_ocean_time, '%Y-%m-%d %H:%M'), loc='left')

    lonlat_float_array = ast.literal_eval(lonlat_array)
    min_depth = 10000

    ax.set_ylabel('Depth[m]')
    ax.set_xlabel(xlabel)
    ax.xaxis.tick_bottom()
    ax.xaxis.set_label_position('bottom')

    x_lim = ast.literal_eval(xrange)
    ax.set_xticks(np.arange(x_lim[0], x_lim[1] + 0.1, x_lim[2]))

    for longitude, latitude in lonlat_float_array:

        # find near array lon lat
        _, lat_near_index = find_near_array(lat_rho, float(latitude))
        _, lon_near_index = find_near_array(lon_rho, float(longitude))

        var = var_array[int(time), :, lat_near_index, lon_near_index]

        # depth parsing
        depth = ncp.variables['verticalinfo'][int(time), :, lat_near_index, lon_near_index]
        depth = depth[depth > -500]  # depth가 -500보다 큰것만 추출, 1차원 배열(-500보다 작으면 육지)
        depth = -depth  # depth는 -값임

        # var parsing
        var = var[var > -500]  # 바다 값만 추출

        # check var, depth len      # var과 depth 길이 맞춰주기
        if len(var) > len(depth):
            var = var[:len(depth)]
        if len(var) < len(depth):
            depth = depth[:len(var)]
        if min_depth < min(depth):
            min_depth = min(depth)

        ax.plot(var, depth, label=f'{longitude, latitude}')

    ax.set_ylim(-100, 0)
    ax.legend()

    png_file_path = f'{v_profile_path}/{model}/png/{file_name}.png'
    plt.savefig(png_file_path, bbox_inches='tight', dpi=300)

    txt_file_path = f'{v_profile_path}/{model}/txt/{file_name}.txt'
    with open(txt_file_path, "w") as ft:
        ft.write("%s\t%s\t%s\t%s\n" % ("longitude ", "latitude   ", "depth[m] ", varname + xunit))
        for longitude, latitude in lonlat_float_array:
            for y in range(len(depth)):
                ft.write("%0.7f\t%0.7f\t%0.7f\t%0.7f" % (longitude, latitude, depth[y], var[y]))
                ft.write("\n")
            ft.write("\n")


def yes3k_vprofile(file_name, date, varname, lonlat_array, xrange, time, v_profile_path):
    model = 'yes3k'
    var_list = varname.split(',')
    model_nc_path = MakeFilePath.get_yes3k_depth_file_path(date, time)
    vn = netCDF4.Dataset(model_nc_path)
    lat_vin = vn.variables['lat_rho'][:, :]
    lon_vin = vn.variables['lon_rho'][:, :]
    ocean_time = vn.variables['ocean_time'][:]

    yes3k_depth_path = MakeFilePath.get_depth_path(model)
    ncp_depth = netCDF4.Dataset(yes3k_depth_path)
    cs_r = ncp_depth.variables['Cs_r'][:]
    h = ncp_depth.variables['h'][:]
    zeta = ncp_depth.variables['zeta'][0, :, :]
    vtransform = ncp_depth.variables['Vtransform'][:]
    s_rho = ncp_depth.variables['s_rho'][:]
    hc = ncp_depth.variables['hc'][:]

    lat_vin = vn.variables['lat_rho'][:, :]
    lon_vin = vn.variables['lon_rho'][:, :]
    ocean_time = vn.variables['ocean_time'][:]

    datum = datetime.datetime(1968, 5, 23, 0, 0, 0)
    time_num = datum + datetime.timedelta(seconds=ocean_time[0])

    zlevel_depth = zlevel(zeta, vtransform, h, hc, s_rho, cs_r, ncp_depth)

    fig, ax = plt.subplots(figsize=[6, 5])
    date_str = datetime.datetime.strftime(time_num, '%Y-%m-%d %H:%M')
    ax.set_title(' '.join([model.upper(),date_str, varname]), loc='left')
    x_lim = ast.literal_eval(xrange)
    ax.set_ylabel('Depth[m]')
    ax.xaxis.tick_bottom()
    ax.xaxis.set_label_position('bottom')
    ax.set_xticks(np.arange(x_lim[0], x_lim[1] + 0.1, x_lim[2]))

    if len(var_list) != 1:
        var_dict = dict()
        var_dict[var_list[0]] = list()
        var_dict[var_list[1]] = list()
    depth_list = list()

    lonlat_float_array = ast.literal_eval(lonlat_array)
    for longitude, latitude in lonlat_float_array:
        j, i = find_thenearest_grd_pts(lat_vin[:, :], lon_vin[:, :],
                                       latitude, longitude)

        depth = zlevel_depth[:, j, i]
        depth_list.append(depth)
        if len(var_list) == 1:
            var = vn.variables[varname][0, :, j, i]

            if varname == 'temp':
                xunit = '[' + u"\u2103" + ']'
                xlabel = 'Temperature' + xunit
            elif varname == 'salt':
                xunit = '[psu]'
                xlabel = 'Salinity' + xunit
            elif varname == 'u':
                xunit = '[m/s]'
                xlabel = 'U velocity' + xunit
            elif varname == 'v':
                xunit = '[m/s]'
                xlabel = 'V velocity' + xunit
            else:
                sys.exit()
            ax.set_xlabel(xlabel)

            ax.plot(var, depth, label=f'{longitude, latitude}')

            ax.set_ylim(min(depth), 0)
            ax.legend()
        else:
            xunit_list = list()
            for var_name in var_list:
                var1 = vn.variables[var_name][0, :, j, i]
                var_arr = var_dict[var_name]
                var_arr.append(var1)
                var_dict[var_name] = var_arr

                if var_name == 'temp':
                    xunit_list.append('[' + u"\u2103" + ']')
                elif var_name == 'salt':
                    xunit_list.append('[psu]')
                elif var_name == 'u':
                    xunit_list.append('[m/s]')
                elif var_name == 'v':
                    xunit_list.append('[m/s]')

    if len(var_list) == 1:
        png_file_path = f'{v_profile_path}/{model}/png/{file_name}.png'
        plt.savefig(png_file_path, bbox_inches='tight', dpi=300)
        with open(f'{v_profile_path}/{model}/txt/{file_name}.txt', "w") as ft:
            ft.write("%s\t%s\n" % ("depth[m] ", varname + xunit))
            for y in range(len(depth)):
                ft.write("%0.7f\t%0.7f" % (depth[y], var[y]))
                ft.write("\n")

        txt_file_path = f'{v_profile_path}/{model}/txt/{file_name}.txt'
        with open(txt_file_path, "w") as ft:
            ft.write("%s\t%s\t%s\t%s\n" % ("longitude ", "latitude   ", "depth[m] ", varname + xunit))
            for longitude, latitude in lonlat_float_array:
                for y in range(len(depth)):
                    ft.write("%0.7f\t%0.7f\t%0.7f\t%0.7f" % (longitude, latitude, depth[y], var[y]))
                    ft.write("\n")
                ft.write("\n")
    else:
        png_file_path = f'{v_profile_path}/{model}/png/{file_name}.png'
        print(png_file_path)
        txt_file_path = f'{v_profile_path}/{model}/txt/{file_name}.txt'

        with open(txt_file_path, "w") as ft:
            ft.write("%s\t%s\t%s\t%s\t%s\n" % ("longitude ", "latitude   ", "depth[m] ", f'{var_list[0] + xunit_list[0]}      ', var_list[1] + xunit_list[1]))
            for idx, [longitude, latitude] in enumerate(lonlat_float_array):
                for y in range(len(depth_list[0])):
                    ft.write("%0.7f\t%0.7f\t%0.7f\t%0.7f\t%0.7f" % (longitude, latitude, depth_list[idx][y], var_dict[var_list[0]][idx][y], var_dict[var_list[1]][idx][y]))
                    ft.write("\n")
                ft.write("\n")

    if os.path.isfile(png_file_path):
        png_flag = 'Success'
    else:
        png_flag = 'Fail'

    if os.path.isfile(txt_file_path):
        txt_flag = 'Success'
    else:
        txt_flag = 'Fail'

    return png_flag, txt_flag


def main(file_name, model, date, varname, lonlat_array, xrange, time, v_profile_path):
    if model == 'mohid300m':
        png_flag, txt_flag = mohid_vprofile(file_name, date, varname, lonlat_array, xrange, time, v_profile_path)
    elif model == 'yes3k':
        png_flag, txt_flag = yes3k_vprofile(file_name, date, varname, lonlat_array, xrange, time, v_profile_path)
    return png_flag, txt_flag


if __name__ == "__main__":
    # file_name = sys.argv[1]
    # model = sys.argv[2]
    # date = sys.argv[3]
    # varname = sys.argv[4]
    # lonlat_array = sys.argv[5]
    # xrange = sys.argv[6]
    # time = sys.argv[7]
    # v_profile_path = sys.argv[8]
    # print(main(file_name, model, date, varname, lonlat_array, xrange, time, v_profile_path))

    # file_name = 'pred_vprofile_mohid300m_200401_1_temp_10,11,0.1_YYYYMMDDHHmmss'
    # file_name_format = '{type}_vprofile_{model}_{date_yymmdd}_{time}_{variable}_{xrange}_{create time_YYYYMMDDHHmmss}'
    # model = 'mohid300m'
    # date = '20200401'
    # varname = 'temp'
    # lonlat_array='[[124.84,35.348],[125.981,37.5191],[127.89,34.59],[129.679,38.2274]]'
    # xrange='[6,14,0.5]'
    # time='1'
    #
    now_date = datetime.datetime.now()
    print(now_date)
    datetime_str = now_date.strftime('%Y%m%d%H%M%S')
    file_name = f'pred_vprofile_yes3k_201231_7_u,v_30,33,0.5_{datetime_str}'
    file_name_format = '{type}_vprofile_{model}_{date_yymmdd}_{time}_{variable}_{xrange}_{create time_YYYYMMDDHHmmss}'
    model = 'yes3k'
    date = '20201231'
    # yes3k는 u와 v만 가능
    varname = 'u,v'
    # 165,103/375,145/215,268/184,377/515,562
    lonlat_array = '[[123,33],[126,34],[127,34],[130,36],[132,37]]'
    xrange = '[30,33,0.5]'
    time = '7'
    v_profile_path = '/DATA/PYTHON/output/vprofile'
    print(main(file_name, model, date, varname, lonlat_array, xrange, time, v_profile_path))
