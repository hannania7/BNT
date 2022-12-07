# -*- coding: utf-8 -*-


import os
import sys
import netCDF4
import json
import subprocess
import datetime
import numpy as np
import MakeFilePath
import ParsingData

PROPERTY_PATH = '/DATA/NAVY/source/property.in'
PROPERTY = ParsingData.read_property(PROPERTY_PATH)


def mohid300_var_height_interp(vertical: np.array, value_array: np.array, bathmetry:np.array, height: float) -> np.array:
    # vertical = src_vertical, value_array = var_array, bathmetry = src_bath, height = height
    # bathmetry = 지점 별 수심 값(m)
    # vertical = mohid층의 높이(meter)
    # vertical.shape = 40,1620,1620, value_array.shape = 40,1620,1620, bathmetry.shape: 1620,1620
    # result_array.shape = 1,1620,1620
    fill_value = -99.9
    result_array = np.full((1, 1620, 1620),fill_value=fill_value)
    for y in range(1620):
        for x in range(1620):
            # check max bathmetry
            if bathmetry[y, x] < height:
                continue
            temp = np.interp(height, vertical[:, y ,x], value_array[:, y, x])
            # check max_value
            if temp > 999:
                continue
            else:
                result_array[0, y, x] = temp
    return result_array


def yes3k_var_height_interp(vertical: np.array, value_array: np.array, bathmetry:np.array, height: float) -> np.array:
    # vertical = src_vertical, value_array = var_array, bathmetry = src_bath, height = height
    # bathmetry = 지점 별 수심 값(m)
    # vertical = mohid층의 높이(meter)
    # vertical.shape = 40,642,610, value_array.shape = 40,642,610, bathmetry.shape: 642,610
    # result_array.shape = 1,642,610
    fill_value = -99.9
    result_array = np.full((1, 642, 610),fill_value=fill_value)
    for y in range(642):
        for x in range(610):
            # check max bathmetry
            if bathmetry[y, x] < height:
                continue
            value = np.interp(height, vertical[:, y ,x], value_array[0,:, y, x])
            # check max_value
            if value > 999:
                continue
            else:
                result_array[0, y, x] = value
    return result_array


# Move u to central rho points
def move_u2rho(u_array_p):
    u_array_p = make_mndarray2ndarray(u_array_p)
    result_array = np.zeros([u_array_p.shape[0], u_array_p.shape[1], u_array_p.shape[2], u_array_p.shape[3] + 1],
                            dtype=float)
    result_array[:, :, :, 1:-1] = 0.5 * (u_array_p[:, :, :, :-1] + u_array_p[:, :, :, 1:])
    result_array[:, :, :, 0] = u_array_p[:, :, :, 0]
    result_array[:, :, :, -1] = u_array_p[:, :, :, -1]
    return result_array


# Move v to central rho points
def move_v2rho(v_array_p):
    v_array_p = make_mndarray2ndarray(v_array_p)
    result_array = np.zeros([v_array_p.shape[0], v_array_p.shape[1], v_array_p.shape[2] + 1, v_array_p.shape[3]],
                            dtype=float)
    result_array[:, :, 1:-1, :] = 0.5 * (v_array_p[:, :, :-1, :] + v_array_p[:, :, 1:, :])
    result_array[:, :, 0, :] = v_array_p[:, :, 0, :]
    result_array[:, :, -1, :] = v_array_p[:, :, -1, :]
    return result_array


def make_mndarray2ndarray(array_p):
    array_p.set_fill_value(10000)
    array_p = array_p.filled()
    return array_p


def zlevel(zeta, Vtransform, h, hc, s_rho, Cs_r, nc_p):
    # Preallocate a depth array
    nx, ny, nz = get_dimention_shape(nc_p)
    z = np.zeros((nz, ny, nx))

    # Convert the masked array to a nan-filled ndarray
    zeta = np.ma.filled(zeta, np.nan)

    # Depending on the Vtransform value, the corresponding formula should be used to transform sigma to zlevel
    """<Ocean s-coordinate, generic form 1 or 2>"""
    if Vtransform == 1:
        for k in range(nz):
            S = hc * s_rho[k] + (h - hc) * Cs_r[k]
            z[k, :, :] = S + zeta * (1.0 + S / h)
    elif Vtransform == 2:
        for k in range(nz):
            S = (hc * s_rho[k] + h * Cs_r[k]) / (hc + h)
            z[k, :, :] = zeta + (zeta + h) * S
    else:
        print("The Vtransform value should be either 1 or 2")
        sys.exit()
    return z


def get_dimention_shape(nc_p):
    dimention_p = nc_p.dimensions
    return len(dimention_p['xi_rho']), len(dimention_p['eta_rho']), len(dimention_p['s_rho'])


def z_interp_all_array(self, zoutput, var, h, depth_list):
    # zoutput.shape = [41, 642, 610]
    # var. shape = [41. 642. 610]
    result = np.zeros((zoutput.shape[0], zoutput.shape[1], zoutput.shape[2]))

    for index, deapth in enumerate(depth_list):
        result[index] = z_interp_array(zoutput, var, h, deapth)

    return result


def z_interp_array(zoutput, var, h, depth):
    # zoutput.shape = [41, 642, 610]
    # var. shape = [41. 642. 610]
    result = np.zeros((var.shape[1], var.shape[2]))

    for j in range(result.shape[0]):
        for i in range(result.shape[1]):
            result[j, i] = get_z_interp_value(zoutput, var, h, depth, j, i)

    return result


def get_z_interp_value(zoutput, var, h, deapth, j, i):
    return np.interp(-float(deapth), zoutput[:, j, i], var[:, j, i])


def find_near_index(array, value):
    result_value = np.abs(array[0] - value)
    for cal_index, content in enumerate(array):
        cal_result = np.abs(content - value)
        if result_value >= cal_result:
            (result_value, result_index) = (cal_result, cal_index)
            result_content = content
    return result_index


def make_txt_file(output_path, lat_arr, lon_arr, var_arr, xunit):
    txt_file_path = output_path.replace('nc', 'txt')
    var_units = f"{varname} [{xunit}]"
    max_val = -999
    sum_val = 0
    with open(txt_file_path, "w") as ft:
        ft.write("%s\t%s\t%s\n" % ("latitude ", "longitude   ", var_units))
        for lat_idx, lat in enumerate(lat_arr):
            for lon_idx, lon in enumerate(lon_arr):
                ft.write("%0.5f\t%0.5f\t%0.5f" % (lat, lon, var_arr[0,lat_idx,lon_idx]))
                ft.write("\n")
                if var_arr[0,lat_idx,lon_idx] <= 1000:
                    max_val = max(var_arr[0,lat_idx,lon_idx], max_val)
                    sum_val += var_arr[0,lat_idx,lon_idx]
            ft.write("\n")
    avg_val = sum_val / (lat_arr.shape[0] * lon_arr.shape[0])
    return max_val, avg_val


def split_yes3k_nc(regrid_path, output_path, lonlat_array, varname):
    nosplit_nc = netCDF4.Dataset(regrid_path, 'r')

    ocean_time = nosplit_nc.variables['ocean_time']
    lon_array = nosplit_nc.variables['lon'][:]
    lat_array = nosplit_nc.variables['lat'][:]
    var_array = nosplit_nc.variables[varname]

    lonlat_array = lonlat_array.split(',')
    # 2022년 6월 23일 원태찬 이해돕기 위해 주석달음 index 범위 지정
    lon_min_idx = find_near_index(lon_array, float(lonlat_array[0]))
    lon_max_idx = find_near_index(lon_array, float(lonlat_array[2]))
    lat_min_idx = find_near_index(lat_array, float(lonlat_array[1]))
    lat_max_idx = find_near_index(lat_array, float(lonlat_array[3]))

    lon_arr = lon_array[lon_min_idx:lon_max_idx]
    lat_arr = lat_array[lat_min_idx:lat_max_idx]
    var_arr = var_array[:, lat_min_idx:lat_max_idx, lon_min_idx:lon_max_idx]

    lon_size = lon_arr.shape[0]
    lat_size = lat_arr.shape[0]

    nc2write = netCDF4.Dataset(output_path, mode='w')

    nc2write.createDimension('ocean_time', None)
    time = nc2write.createVariable('ocean_time', 'd', 'ocean_time')

    nc2write.createDimension('lat', size=lat_size)
    nc2write.createDimension('lon', size=lon_size)

    var = nc2write.createVariable(varname, 'f', ('ocean_time', 'lat', 'lon'), fill_value=-99.9)
    lat = nc2write.createVariable('lat', 'd', ('lat'))
    lon = nc2write.createVariable('lon', 'd', ('lon'))

    lat[:] = lat_arr[:]
    lon[:] = lon_arr[:]
    time[:] = ocean_time[:]

    var[:, :] = var_arr[:, :]

    lon.long_name = 'longitude'
    lon.units = 'degree_east'
    lon.standard_names = 'longitude'

    lat.long_name = 'latitude'
    lat.units = 'degree_north'
    lat.standard_names = 'latitude'

    time.long_name = 'time since initialization'
    time.units = ocean_time.units

    var.long_name = var_array.long_name
    var.units = var_array.units
    var.time = var_array.time
    var.coordinates = 'lon lat ocean_time'

    nc2write.close()

    max_val, avg_val = make_txt_file(output_path, lat_arr, lon_arr, var_arr, var_array.units)
    return max_val, avg_val


def mohid300m_hslice(file_name, date, lonlat_array, varname, height, time, h_slice_path):
    height = int(height)
    time = int(time)

    start_date = datetime.datetime(year=int(date[0:4]), month=int(date[4:6]),
                                   day=int(date[6:8]), hour=int(time))

    model_nc_path = MakeFilePath.get_mohid_vis_file_path(date)
    ncp = netCDF4.Dataset(model_nc_path, mode ='r')
    src_lat = ncp.variables['lat'][:]
    src_lon = ncp.variables['lon'][:]
    src_time = ncp.variables['time'][:]
    src_bath = ncp.variables['bathymetry'][:]
    src_vertical = ncp.variables['verticalinfo'][time, :, :, :]

    if varname == 'temp':
        var_array = ncp.variables['temp'][time, :, :, :]
        vout_long_name = 'potential temperature'
        vout_units = 'Celcius'
        vout_time='time'
        vout_coordinates = 'lon lat time'
    elif varname == 'sali':
        var_array = ncp.variables['salt'][time, :, :, :]
        vout_long_name = 'salinity'
        vout_units = 'psu'
        vout_time='time'
        vout_coordinates = 'lon lat time'
    else:
        sys.exit('wrong_var_name_type')
    # var_array = np.transpose(var_array, (0, 2,1))

    # interp value array use height
    interp_value_array = mohid300_var_height_interp(vertical=src_vertical, value_array=var_array,
                                           bathmetry=src_bath, height=height)

    [t] = np.shape(src_time[:])
    new_time =[]
    for t_step in range(t):
        t_step = float(t_step)
        new_time.append(t_step)

    var_array = np.ma.masked_where(var_array <= -99.9, var_array)
    data = [{"data": varname, "min": float(np.ma.min(var_array)), "max": float(np.ma.max(var_array))}]
    print(data)
    new_datum_str = 'hours since %s' % start_date.strftime("%Y-%m-%d %H:%M:%S")

    hslice_mohid_fname = f'{h_slice_path}/{file_name}.nc'

    nc2write = netCDF4.Dataset(hslice_mohid_fname, mode='w', format="NETCDF3_CLASSIC")

    nc2write.createDimension('time', None)
    nc2write.createDimension('lon', size = src_lon.shape[0])
    nc2write.createDimension('lat', size = src_lat.shape[0])

    lat = nc2write.createVariable('lat','d','lat')
    lon = nc2write.createVariable('lon','d','lon')
    time =nc2write.createVariable('time','d','time')
    var = nc2write.createVariable(varname,'f',('time','lat','lon'),fill_value=-99.9)

    lat[:] = src_lat[:]
    lon[:] = src_lon[:]
    time[:] = new_time[:]

    var[:, :, :] = np.transpose(interp_value_array[:, :, :], (0,2,1))

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
    var.time= vout_time
    var.coordinates = vout_coordinates

    nc2write.close()

    if os.path.isfile(hslice_mohid_fname):
        return 'Success', data
    else:
        return 'Fail', data


def yes3k_hslice(file_name, date, lonlat_array, varname, height, time, h_slice_path):
    yes3k_depth_path = MakeFilePath.get_depth_path('yes3k')
    ncl_file_path = f'{PROPERTY["NCL_PATH"]}/hslice_regrid_yes3k.ncl'
    weight_file_path = f'{PROPERTY["WEIGHT_PATH"]}/wgt_file_yes3k.nc'

    height = int(height)
    time = int(time)

    start_date = datetime.datetime.strptime(date, "%Y%m%d")
    start_date = start_date.replace(hour=time)

    model_nc_path = MakeFilePath.get_yes3k_depth_file_path(date, time)
    ncp = netCDF4.Dataset(model_nc_path, mode='r')
    src_lat = ncp.variables['lat_rho'][:]
    src_lon = ncp.variables['lon_rho'][:]

    src_ocean_time = ncp.variables['ocean_time'][:]
    src_eta_rho = ncp.dimensions['eta_rho']
    src_xi_rho = ncp.dimensions['xi_rho']

    ncp_depth = netCDF4.Dataset(yes3k_depth_path, mode='r')
    src_vtransform = int(ncp_depth.variables["Vtransform"][:])
    src_h = ncp_depth.variables["h"][:, :]
    src_hc = float(ncp_depth.variables["hc"][:])
    src_s_rho = ncp_depth.variables["s_rho"][:]
    src_cs_r = ncp_depth.variables["Cs_r"][:]
    src_zeta = ncp_depth.variables["zeta"][:, :, :]

    datum = datetime.datetime(1968, 5, 23, 0, 0, 0)
    time_num = datum + datetime.timedelta(seconds=src_ocean_time[0])

    if varname == 'temp':
        var_array = ncp.variables['temp'][:]
        vout_long_name = 'potential temperature'
        vout_units = 'Celcius'
        vout_time = 'time'
        vout_coordinates = 'lon_rho lat_rho ocean_time'
    elif varname == 'sali':
        var_array = ncp.variables['salt'][:]
        vout_long_name = 'salinity'
        vout_units = 'psu'
        vout_time = 'time'
        vout_coordinates = 'lon_rho lat_rho ocean_time'
    elif varname == 'u':
        var_array = ncp.variables['u'][:]
        var_array = move_u2rho(var_array)
        vout_long_name = 'u-momentum component'
        vout_units = 'meter second-1'
        vout_time = 'ocean_time'
        vout_coordinates = 'lon lat ocean_time'
    elif varname == 'v':
        var_array = ncp.variables['v'][:]
        var_array = move_v2rho(var_array)
        vout_long_name = 'v-momentum component'
        vout_units = 'meter second-1'
        vout_time = 'ocean_time'
        vout_coordinates = 'lon lat ocean_time'
    else:
        sys.exit('wrong_var_name_type')

    z_output = zlevel(src_zeta, src_vtransform, src_h, src_hc, src_s_rho, src_cs_r, ncp)
    # interp value array use height
    interp_value_array = yes3k_var_height_interp(vertical=z_output, value_array=var_array,
                                           bathmetry=src_h, height=height)

    [t] = np.shape(src_ocean_time[:])
    new_time = []
    for t_step in range(t):
        t_step = float(t_step)
        new_time.append(t_step)

    var_array = np.ma.masked_where(var_array <= -90, var_array)
    new_datum_str = 'hours since %s' % start_date.strftime("%Y-%m-%d %H:%M:%S")
    
    hslice_yes3k_fname = f'{h_slice_path}/{file_name}_nonregrid.nc'
    hslice_yes3k_regrid_fname = f'{h_slice_path}/{file_name}_regrid.nc'
    hslice_yes3k_regrid = f'{h_slice_path}/{file_name}.nc'

    nc2write = netCDF4.Dataset(hslice_yes3k_fname, mode='w', format="NETCDF3_CLASSIC")

    nc2write.createDimension('ocean_time', None)
    time = nc2write.createVariable('ocean_time', 'd', 'ocean_time')

    nc2write.createDimension('eta_rho', size=src_eta_rho.size)
    nc2write.createDimension('xi_rho', size=src_xi_rho.size)

    var = nc2write.createVariable(varname, 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=-99.9)
    lat = nc2write.createVariable('lat', 'd', ('eta_rho', 'xi_rho'))
    lon = nc2write.createVariable('lon', 'd', ('eta_rho', 'xi_rho'))

    lat[:] = src_lat[:]
    lon[:] = src_lon[:]
    time[:] = new_time[:]

    var[:,:,:] = interp_value_array[:,:,:]

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

    subprocess.run(F'ncl ipath=\\"{hslice_yes3k_fname}\\" opath=\\"{hslice_yes3k_regrid_fname}\\" '
                   + F'wpath=\\"{weight_file_path}\\" variable=\\"{varname}\\" '
                   + ncl_file_path
                   , shell=True)

    max_val, avg_val = split_yes3k_nc(hslice_yes3k_regrid_fname, hslice_yes3k_regrid, lonlat_array, varname)
    data = [float(np.ma.min(var_array)), max_val, avg_val]

    os.remove(hslice_yes3k_regrid_fname)
    os.remove(hslice_yes3k_fname)
    if os.path.isfile(hslice_yes3k_regrid):
        return 'Success', data
    else:
        return 'Fail', data


def main(file_name, model, date, lonlat_array, varname, height, time, h_slice_path):
    success_flag, data = 'Fail', None
    if model == 'mohid300m':
        success_flag, data = mohid300m_hslice(file_name, date, lonlat_array, varname, height, time, h_slice_path)
    elif model == 'yes3k':
        success_flag, data = yes3k_hslice(file_name, date, lonlat_array, varname, height, time, h_slice_path)
    return success_flag, data


if __name__ == "__main__":
    # file_name = sys.argv[1]
    # model = sys.argv[2]
    # date = sys.argv[3]
    # lonlat_array = sys.argv[4]
    # varname = sys.argv[5]
    # height = sys.argv[6]
    # time = sys.argv[7]
    # h_slice_path = sys.argv[8]

    now = datetime.datetime.now()
    file_name = f'pred_hslice_yes3k_201231_123,30,125,32_10_u_30_{now.strftime("%Y%m%d%H%M%s")}'
    model = 'yes3k'
    date = '20201231'
    lonlat_array = '123,30,125,32'
    # yes3k는 u와 v만 가능
    varname = 'u'
    height = '30'
    time = '10'
    h_slice_path = '/DATA/PYTHON/output/hslice'
    print(main(file_name, model, date, lonlat_array, varname, height, time, h_slice_path))