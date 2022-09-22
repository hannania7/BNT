#-*- coding:utf-8 -*-

import os
import sys
import datetime
import netCDF4
import numpy as np
import pandas as pd
import MakeFilePath
import DBInsertModule


def make_mndarray2ndarray(array_p):
    array_p.set_fill_value(10000)
    array_p = array_p.filled()
    return array_p

def calaulate_spddir(u_val, v_val):
    if u_val >= 9999:
        speed_val = 0
        direction_val = 0

    else:
        speed_val = np.sqrt((u_val * u_val) + (v_val * v_val))
        direction_rad = np.arctan2(v_val, u_val)
        direction_val = np.rad2deg(direction_rad) * -1
        if direction_val > 360:
            direction_val -= 360
        if direction_val < 0:
            direction_val + 360

    return speed_val, direction_val


def make_yes3k_speed_nc(ncp, output_path, speed_arr, direction_arr, data_name):
    print('make_yes3k_speed_nc output_path', output_path)
    w_ncp = netCDF4.Dataset(output_path, 'w')
    r_ocean_time = ncp.variables['ocean_time'][:]
    r_lat = ncp.variables['lat'][:]
    r_lon = ncp.variables['lon'][:]
    r_u = ncp.variables['u'][:]
    r_v = ncp.variables['v'][:]
    r_temp = ncp.variables['temp'][:]
    r_mask_rho = ncp.variables['mask_rho'][:]

    w_ncp.createDimension('ocean_time', r_ocean_time.shape[0])
    w_ncp.createDimension('lat', r_lat.shape[0])
    w_ncp.createDimension('lon', r_lon.shape[0])

    ocean_time = w_ncp.createVariable('ocean_time', 'd', ('ocean_time'))
    lat = w_ncp.createVariable('lat', 'd', ('lat'))
    lon = w_ncp.createVariable('lon', 'd', ('lon'))
    u = w_ncp.createVariable('u', 'f', ('ocean_time', 'lat', 'lon'))
    v = w_ncp.createVariable('v', 'f', ('ocean_time', 'lat', 'lon'))
    temp = w_ncp.createVariable('temp', 'f', ('ocean_time', 'lat', 'lon'), fill_value=-999.9)
    speed = w_ncp.createVariable('speed', 'f', ('ocean_time', 'lat', 'lon'), fill_value=-999.9)
    direction = w_ncp.createVariable('direction', 'f', ('ocean_time', 'lat', 'lon'), fill_value=-999.9)
    mask_rho = w_ncp.createVariable('mask_rho', 'd', ('lat', 'lon'), fill_value=-999.9)

    ocean_time[:] = r_ocean_time
    lat[:] = r_lat
    lon[:] = r_lon
    u[:] = r_u
    v[:] = r_v
    temp[:] = r_temp
    speed[:] = speed_arr
    direction[:] = direction_arr
    mask_rho[:] = r_mask_rho

    ocean_time.units = "seconds since 1968-05-23 00:00:00 GMT"
    ocean_time.long_name = "time since initialization"
    ocean_time.field = "time, scalar, series"
    ocean_time.calendar = "gregorian"

    lat.long_name = "latitude"
    lat.units = "degrees_north"

    lon.long_name = "longitude"
    lon.units = "degrees_east"

    u.long_name = "sea surface u-momentum component"
    u.units = "meter second-1"
    u.time = "ocean_time"
    u.field = "u-velocity, scalar, series"

    v.long_name = "sea surface v-momentum component"
    v.units = "meter second-1"
    v.time = "ocean_time"
    v.field = "v-velocity, scalar, series"

    temp.long_name = "potential temperature"
    temp.units = "Celsius"
    temp.time = "ocean_time"
    temp.field = "temperature, scalar, series"

    speed.units = "m/s"
    speed.time = "ocean_time"

    direction.units = "degree"
    direction.time = "ocean_time"

    mask_rho.long_name = "mask on RHO-points"
    mask_rho.flag_values = 0.0, 1.0
    mask_rho.flag_meanings = "land water"
    w_ncp.close()


def make_wrf_speed_nc(ncp, output_path, speed_arr, direction_arr, data_name):
    print('make_wrf_speed_nc output_path', output_path)
    r_ocean_time = ncp.variables['time'][:]
    r_lat = ncp.variables['lat'][:]
    r_lon = ncp.variables['lon'][:]
    r_u = ncp.variables['Uwind'][:]
    r_v = ncp.variables['Vwind'][:]
    r_swrad = ncp.variables['Swrad'][:]
    r_tair = ncp.variables['Tair'][:]
    r_pair = ncp.variables['Pair'][:]

    w_ncp = netCDF4.Dataset(output_path, 'w')

    w_ncp.createDimension('ocean_time', r_ocean_time.shape[0])
    w_ncp.createDimension('lat', r_lat.shape[0])
    w_ncp.createDimension('lon', r_lon.shape[0])

    ocean_time = w_ncp.createVariable('ocean_time', 'd', ('ocean_time'))
    lat = w_ncp.createVariable('lat', 'd', ('lat'))
    lon = w_ncp.createVariable('lon', 'd', ('lon'))
    u = w_ncp.createVariable('Uwind', 'f', ('ocean_time', 'lat', 'lon'))
    v = w_ncp.createVariable('Vwind', 'f', ('ocean_time', 'lat', 'lon'))
    swrad = w_ncp.createVariable('Swrad', 'f', ('ocean_time', 'lat', 'lon'), fill_value=-999.9)
    tair = w_ncp.createVariable('Tair', 'f', ('ocean_time', 'lat', 'lon'), fill_value=-999.9)
    pair = w_ncp.createVariable('Pair', 'f', ('ocean_time', 'lat', 'lon'), fill_value=-999.9)
    speed = w_ncp.createVariable('speed', 'f', ('ocean_time', 'lat', 'lon'), fill_value=-999.9)
    direction = w_ncp.createVariable('direction', 'f', ('ocean_time', 'lat', 'lon'), fill_value=-999.9)

    ocean_time[:] = r_ocean_time[:]
    lat[:] = r_lat[:]
    lon[:] = r_lon[:]
    u[:] = r_u[:]
    v[:] = r_v[:]
    swrad[:] = r_swrad[:]
    tair[:] = r_tair[:]
    pair[:] = r_pair[:]
    speed[:] = speed_arr[:]
    direction[:] = direction_arr[:]
    print(np.min(speed_arr), np.max(speed_arr))

    ocean_time.units = "seconds since 1968-05-23 00:00:00 GMT"
    ocean_time.long_name = "time since initialization"
    ocean_time.calendar = "gregorian"
    ocean_time.field = "time, scalar, series"

    lat.long_name = "latitude"
    lat.units = "degrees_north"

    lon.long_name = "longitude"
    lon.units = "degrees_east"

    u.long_name = "WRF (10m) u winds [m/s]"
    u.units = "meter second-1"
    u.time = "ocean_time"

    v.long_name = "WRF (10m) v winds [m/s]"
    v.units = "meter second-1"
    v.time = "ocean_time"

    swrad.long_name = "potential temperature"
    swrad.units = "Celsius"
    swrad.time = "ocean_time"

    tair.long_name = "potential temperature"
    tair.units = "Celsius"
    tair.time = "ocean_time"

    pair.long_name = "potential temperature"
    pair.units = "Celsius"
    pair.time = "ocean_time"

    speed.units = "m/s"
    speed.time = "ocean_time"

    direction.units = "degree"
    direction.time = "ocean_time"
    w_ncp.close()


def main_yes3k(col_head_row, date, output_dir_path):
    model = col_head_row.get('data_cate2')
    data_name = col_head_row.get('data_name')
    if data_name == 'YES3K':
        input_path = MakeFilePath.get_yes3k_regrid_file_path(col_head_row, date)
    elif data_name == 'YES3K_7D':
        input_path = MakeFilePath.get_yes3k_regrid_file_7D_path(col_head_row, date)
    file_name = os.path.basename(input_path) 
    if (data_name == 'YES3K' and model == 'YES3K'):
        output_file_name = file_name.replace('2_regrid', 'speed')
    elif (data_name == 'YES3K_7D' and model == 'YES3K_7D'):
        output_file_name = file_name.replace('2_regrid', 'speed')
    output_path = f"{output_dir_path}/{output_file_name}"

    ncp = netCDF4.Dataset(input_path)

    r_u = ncp.variables['u']
    r_v = ncp.variables['v']

    r_u_arr = make_mndarray2ndarray(r_u[:])
    r_v_arr = make_mndarray2ndarray(r_v[:])

    speed_arr = np.zeros(r_u_arr.shape)
    direction_arr = np.zeros(r_v_arr.shape)
    for time_idx in range(r_u_arr.shape[0]):
        for lat_idx in range(r_u_arr.shape[1]):
            for lon_idx in range(r_u_arr.shape[2]):
                u_val = r_u_arr[time_idx, lat_idx, lon_idx]
                v_val = r_v_arr[time_idx, lat_idx, lon_idx]
                speed, direction = calaulate_spddir(u_val, v_val)
                speed_arr[time_idx, lat_idx, lon_idx] = speed
                direction_arr[time_idx, lat_idx, lon_idx] = direction

    make_yes3k_speed_nc(ncp, output_path, speed_arr, direction_arr, data_name)
    # os.remove(input_path)
    # 3일
    data_path = MakeFilePath.get_pred_save_dir_path(col_head_row, date)
    model_date = date.strftime("%Y%m%d00")
    if (data_name == 'YES3K' and model == 'YES3K'):
        yes3k_save_file_path = f"{data_path}/YES3K_{model_date}_2.nc"
    # 7일
    elif (data_name == 'YES3K_7D' and model == 'YES3K_7D'):
        yes3k_save_file_path = f"{data_path}/YES3K_{model_date}_7D_2.nc"
    os.remove(yes3k_save_file_path)
    os.remove(input_path)


def main_wrf(col_head_row, date, output_dir_path):
    model = col_head_row.get('data_cate2')
    data_name = col_head_row.get('data_name')
    if data_name == 'DM1' or data_name == 'DM2':
        input_path = MakeFilePath.get_wrf_regrid_file_path(col_head_row, date)
    elif data_name == 'DM1_7D' or data_name == 'DM2_7D':
        input_path = MakeFilePath.get_wrf_regrid_file_7D_path(col_head_row, date)
    file_name = os.path.basename(input_path)      
    if model == 'WRF':
        output_file_name = file_name.replace('2_regrid', 'speed')
    elif model == 'WRF_7D' or model == 'WRF_7D_2':
        output_file_name = file_name.replace('2_regrid', 'speed')
    output_path = f"{output_dir_path}/{output_file_name}"

    ncp = netCDF4.Dataset(input_path)

    r_u = ncp.variables['Uwind']
    r_v = ncp.variables['Vwind']

    r_u_arr = make_mndarray2ndarray(r_u[:])
    r_v_arr = make_mndarray2ndarray(r_v[:])
    speed_arr = np.zeros(r_u_arr.shape)
    direction_arr = np.zeros(r_v_arr.shape)
    for time_idx in range(r_u_arr.shape[0]):
        for lat_idx in range(r_u_arr.shape[1]):
            for lon_idx in range(r_u_arr.shape[2]):
                u_val = r_u_arr[time_idx, lat_idx, lon_idx]
                # u_val /= 100
                v_val = r_v_arr[time_idx, lat_idx, lon_idx]
                # v_val /= 100
                speed, direction = calaulate_spddir(u_val, v_val)
                speed /= 100
                speed_arr[time_idx, lat_idx, lon_idx] = speed
                direction_arr[time_idx, lat_idx, lon_idx] = direction

    make_wrf_speed_nc(ncp, output_path, speed_arr, direction_arr, data_name)
    # os.remove(input_path)
    data_name = col_head_row.get('data_name').lower()
    data_path = MakeFilePath.get_pred_save_dir_path(col_head_row, date)
    start_date = date.strftime("%Y%m%d")
    if model == 'WRF':
        end_date = (date + datetime.timedelta(days=2)).strftime("%Y%m%d")
        wrfdm_save_file_path = f"{data_path}/wrf{data_name}_{start_date}_{end_date}_2.nc"
    elif model == 'WRF_7D':
            data = 'dm1'
            end_date = (date + datetime.timedelta(days=6)).strftime("%Y%m%d")
            wrfdm_save_file_path = f"{data_path}/wrf{data}_{start_date}_{end_date}_7D_2.nc"
    elif model == 'WRF_7D_2':
            data = 'dm2'
            end_date = (date + datetime.timedelta(days=6)).strftime("%Y%m%d")
            wrfdm_save_file_path = f"{data_path}/wrf{data}_{start_date}_{end_date}_7D_2.nc"
    os.remove(wrfdm_save_file_path)
    os.remove(input_path)

def main(model, date, data_name):
    date = datetime.datetime.strptime(date, '%Y%m%d')
    if model == 'WRFDM1':
        model = 'WRF'
        data_name = 'DM1'
    elif model == 'WRFDM1_7D':
        model = 'WRF_7D'
        data_name = 'DM1_7D'
    elif model == 'WRFDM2':
        model = 'WRF'
        data_name = 'DM2'
    elif model == 'WRFDM2_7D':
        model = 'WRF_7D_2'
        data_name = 'DM2_7D'
    elif data_name == 'YES3K':
        model = 'YES3K'
        data_name = 'YES3K'
    elif data_name == 'YES3K_7D':
        model = 'YES3K_7D'
        data_name = 'YES3K_7D'
    head_sql = f"select * from mng_data_col_head where data_cate1='pred' and data_cate2 = '{model}' and data_name='{data_name}'"
    col_head_row = pd.DataFrame.to_dict(DBInsertModule.read_query(head_sql), orient='index')[0]
    output_dir_path = MakeFilePath.get_pred_save_dir_path(col_head_row, date)

    if model == 'YES3K':
        main_yes3k(col_head_row, date, output_dir_path)
    elif model == 'YES3K_7D':
        main_yes3k(col_head_row, date, output_dir_path)
    elif model == 'WRF':
        main_wrf(col_head_row, date, output_dir_path)
    elif model == 'WRF_7D':
        main_wrf(col_head_row, date, output_dir_path)
    elif model == 'WRF_7D_2':
        main_wrf(col_head_row, date, output_dir_path)


if __name__ == "__main__":
    model = sys.argv[1]
    date = sys.argv[2]
    data_name = sys.argv[3]
    main(model, date, data_name)

    # model = 'YES3K'
    # date = '20220221'
    # main(model, date)
    # #
    # model = 'WRFDM1'
    # date = '20220303'
    # main(model, date)
