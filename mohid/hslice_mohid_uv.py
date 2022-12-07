# -*- coding: utf-8 -*-


import os
import sys
import netCDF4
from datetime import datetime
import numpy as np

def move_u2rho(self, u_array_p):
    u_array_p = self.make_mndarray2ndarray(u_array_p)
    result_array = np.zeros([u_array_p.shape[0],u_array_p.shape[1],u_array_p.shape[2],u_array_p.shape[3]+1], dtype=float)
    result_array[:,:,:,1:-1] = 0.5*(u_array_p[:,:,:,:-1]+u_array_p[:,:,:,1:])
    result_array[:,:,:,0] = u_array_p[:,:,:,0]
    result_array[:,:,:,-1] = u_array_p[:,:,:,-1]
    return result_array

def move_v2rho(self, v_array_p):
    v_array_p = self.make_mndarray2ndarray(v_array_p)
    result_array = np.zeros([v_array_p.shape[0],v_array_p.shape[1],v_array_p.shape[2]+1,v_array_p.shape[3]], dtype=float)
    result_array[:,:,1:-1,:] = 0.5*(v_array_p[:,:,:-1,:]+v_array_p[:,:,1:,:])
    result_array[:,:,0,:] = v_array_p[:,:,0,:]
    result_array[:,:,-1,:] = v_array_p[:,:,-1,:]
    return result_array


def var_height_interp(vertical: np.array, value_array: np.array, bathmetry:np.array, height: float) -> np.array:
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


def main(filepath, height, time):
    # init
    height = int(height)
    time = int(time)

    ncp = netCDF4.Dataset(filepath, mode ='r')
    src_lat = ncp.variables['lat'][:]
    src_lon = ncp.variables['lon'][:]
    src_time = ncp.variables['time'][:]
    src_bath = ncp.variables['bathymetry'][:]
    src_vertical = ncp.variables['verticalinfo'][time, :, :, :]

    vout1 = ncp.variables["u"][time, :, :, :]
    vout1_long_name = 'sea surface u-momentum component'
    vout1_units = 'meter second-1'
    vout1_time = 'ocean_time'
    vout1_coordinates = 'lon lat time'

    vout2 = ncp.variables["v"][time, :, :, :]
    vout2_long_name = 'sea surface v-momentum component'
    vout2_units = 'meter second-1'
    vout2_time = 'time'
    vout2_coordinates = 'lon lat time'

    diff_vertical = src_vertical[:-1,:,:] + np.diff(src_vertical[:,:,:], axis=0)/2
    vout3 = move_u2rho(vout1)
    vout4 = move_v2rho(vout2)
    # interp value array use height
    interp_value_array1 = var_height_interp(vertical=diff_vertical, value_array=vout3,
                                           bathmetry=src_bath, height=height)
    interp_value_array2 = var_height_interp(vertical=diff_vertical, value_array=vout4,
                                           bathmetry=src_bath, height=height)

    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    yyyymmdd12 = filename_without_ext[-10:]
    start_date = datetime.strptime(yyyymmdd12,"%Y%m%d%H")
    path1 = os.path.split(filepath)
    path2 = os.path.split(path1[0])
    foldername = path2[1]

    [t] = np.shape(src_time[:])
    new_time =[]
    for t_step in range(t):
        t_step = float(t_step)
        new_time.append(t_step)

    new_datum_str = 'hours since %s' % start_date.strftime("%Y-%m-%d %H:%M:%S")

    hslice_mohid_fname = '/DATA/PYTHON/output/mohid/hslice_%s_%04d_uv_%02d.nc'% \
                        (yyyymmdd12, time, int(height))

    nc2write = netCDF4.Dataset(hslice_mohid_fname, mode='w', format="NETCDF3_CLASSIC")

    nc2write.createDimension('time', None)
    nc2write.createDimension('lon', size = src_lon.shape[0])
    nc2write.createDimension('lat', size = src_lat.shape[0])

    u_array=nc2write.createVariable("u",'f',('time','lat','lon'),fill_value=-99.9)
    v_array=nc2write.createVariable("v",'f',('time','lat','lon'),fill_value=-99.9)
    lat = nc2write.createVariable('lat','d','lat')
    lon = nc2write.createVariable('lon','d','lon')
    time =nc2write.createVariable('time','d','time')

    lat[:] = src_lat[:]
    lon[:] = src_lon[:]
    time[:] = new_time[:]

    u_array[:, :, :] = np.transpose(interp_value_array1[:, :, :], (0,2,1))
    v_array[:, :, :] = np.transpose(interp_value_array2[:, :, :], (0,2,1))

    lon.long_name = 'longitude'
    lon.units = 'degree_east'
    lon.standard_names = 'longitude'

    lat.long_name = 'latitude'
    lat.units = 'degree_north'
    lat.standard_names = 'latitude'

    time.long_name = 'time since initialization'
    time.units = new_datum_str

    u_array.long_name = vout1_long_name
    u_array.units = vout1_units
    u_array.time= vout1_time
    u_array.coordinates = vout1_coordinates

    v_array.long_name = vout2_long_name
    v_array.units = vout2_units
    v_array.time= vout2_time
    v_array.coordinates = vout2_coordinates

    nc2write.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])