# -*- coding: utf-8 -*-

import netCDF4
import h5py
import numpy as np
import datetime
import sys
"""
조사원 검증평가 mohid300m hdf5 -> mohid300m nc 파일 변환 스크립트
"YYYYMMDD" date str을 입력받으면 L2_Hydrodynamic, L2 Waterproperties hdf5 파일을 참조하여
nc파일을 생성한다.
2020 11 16 최남기 작성
"""


class GetMohidPointValue():

    def __init__(self, hydrodynamic_file:str, waterproperties_file:str):
        self.hyfp = h5py.File(hydrodynamic_file, 'r')
        self.wpfp = h5py.File(waterproperties_file)
        self.lat = self.hyfp['Grid']['Latitude'][:]
        self.lon = self.hyfp['Grid']['Longitude'][:]
        self.bathymetry = self.hyfp['Grid']['Bathymetry'][:]

        self.d_lat = self.diff_lat(self.lat)[0,:]
        self.d_lon = self.diff_lon(self.lon)[:,0]
        self.d_vertical = self.__get_diff_vertical_list()

    def make_netcdf4(self, INPUT_FILE_PATH):
        self.r_ncp = netCDF4.Dataset(INPUT_FILE_PATH, 'w')
        self._create_dimention()
        self._create_variable()
        self.__preprocessing()
        self._add_variable_property()
        self.r_ncp.close()

    def __preprocessing(self):

        self.r_ncp_var_lat[:] = self.d_lat
        self.r_ncp_var_lon[:] = self.d_lon
        self.r_ncp_var_vertical[:] = list(content+1 for content in range(40))
        print(np.shape(self.d_vertical))
        self.r_ncp_var_vertical_info[:,:,:,:] = np.transpose(self.d_vertical, (0, 1, 3, 2))

        self.r_ncp_var_bathymetry[:,:] = np.transpose(self.bathymetry, (1, 0))

        self.time = self.__get_time_list()
        self.r_ncp_var_time[:] = self.time
        self.time = None

        self.u = self.__get_u_list()
        self.r_ncp_var_u[:,:,:,:] = np.transpose(self.u, (0, 1, 3, 2))
        self.u = None

        self.v = self.__get_v_list()
        self.r_ncp_var_v[:,:,:,:] = np.transpose(self.v, (0, 1, 3, 2))
        self.v = None

        self.elev = self.__get_elev_list()
        self.r_ncp_var_elev[:,:,:] = np.transpose(self.elev, (0, 2, 1))
        self.elev = None

        self.temp = self.__get_temp_list()
        self.r_ncp_var_temp[:,:,:,:] = np.transpose(self.temp, (0, 1, 3, 2))
        self.temp = None

        self.salt = self.__get_salt_list()
        self.r_ncp_var_salt[:,:,:,:] = np.transpose(self.salt, (0, 1, 3, 2))
        self.salt = None

        self.hyfp.close()

    def _create_dimention(self):
        # 7 40 1620 1620
        self.r_ncp.createDimension('time', 25)
        self.r_ncp.createDimension('vertical', size = self.d_vertical.shape[1])
        self.r_ncp.createDimension('lon', size = self.d_lon.shape[0])
        self.r_ncp.createDimension('lat', size = self.d_lat.shape[0])
        
    def _create_variable(self):
        self.r_ncp_var_time = self.r_ncp.createVariable('time', 'f', 'time')
        self.r_ncp_var_lat = self.r_ncp.createVariable('lat', 'd', 'lat')
        self.r_ncp_var_lon = self.r_ncp.createVariable('lon', 'd', 'lon')
        self.r_ncp_var_vertical = self.r_ncp.createVariable('vertical', 'd', 'vertical')
        self.r_ncp_var_vertical_info = self.r_ncp.createVariable('verticalinfo', 'f', ('time', 'vertical', 'lat', 'lon'))
        self.r_ncp_var_bathymetry = self.r_ncp.createVariable('bathymetry', 'f', ('lat', 'lon'))
        self.r_ncp_var_u = self.r_ncp.createVariable('u', 'f', ('time', 'vertical', 'lat', 'lon'))
        self.r_ncp_var_v = self.r_ncp.createVariable('v', 'f', ('time', 'vertical', 'lat', 'lon'))
        self.r_ncp_var_temp = self.r_ncp.createVariable('temp', 'f', ('time', 'vertical', 'lat', 'lon'))
        self.r_ncp_var_salt = self.r_ncp.createVariable('salt', 'f', ('time', 'vertical', 'lat', 'lon'))
        self.r_ncp_var_elev = self.r_ncp.createVariable('elev', 'f', ('time', 'lat', 'lon'))

    def _add_variable_property(self):
        self.r_ncp_var_lat.units = 'degree_north'
        self.r_ncp_var_lat.standard_names = 'latgitude'
        self.r_ncp_var_lat.long_name = 'latgitude'

        self.r_ncp_var_lon.units = 'degree_east'
        self.r_ncp_var_lon.standard_names = 'longitude'
        self.r_ncp_var_lon.long_name = 'longitude'

        self.r_ncp_var_time.units = 'seconds since 1968-05-23 00:00:00 GMT'
        self.r_ncp_var_time.long_name = 'time since initialization'

        self.r_ncp_var_vertical.units = 'floor'
        self.r_ncp_var_vertical.long_name = 'vertical'

        self.r_ncp_var_vertical_info.units = 'meter'
        self.r_ncp_var_vertical_info.long_name = 'vertical_info'

        self.r_ncp_var_u.units = 'meter second-1'
        self.r_ncp_var_u.long_name = 'u-velocity'
        self.r_ncp_var_u.time = 'time'
        self.r_ncp_var_u.coordinates = 'lon lat vertical time'

        self.r_ncp_var_v.units = 'm/s'
        self.r_ncp_var_v.long_name = 'v-velocity'
        self.r_ncp_var_v.time = 'time'
        self.r_ncp_var_v.coordinates = 'lon lat vertical time'

        self.r_ncp_var_temp.units = 'degC'
        self.r_ncp_var_temp.long_name = 'temperature'
        self.r_ncp_var_temp.time = 'time'
        self.r_ncp_var_temp.coordinates = 'lon lat vertical time'

        self.r_ncp_var_salt.units = 'psu'
        self.r_ncp_var_salt.long_name = 'salinity'
        self.r_ncp_var_salt.time = 'time'
        self.r_ncp_var_salt.coordinates = 'lon lat vertical time'

        self.r_ncp_var_elev.units = 'm'
        self.r_ncp_var_elev.long_name = 'water_level'
        self.r_ncp_var_elev.time = 'time'
        self.r_ncp_var_elev.coordinates = 'lon lat vertical time'

        self.r_ncp_var_bathymetry.long_name = 'bathymetry'
        self.r_ncp_var_bathymetry.units = 'm'
    
    """ handling function """
    def __get_time_list(self) -> list:
        result_list = list()
        for index in range(25):
            if index <= 8:
                # input_list = [0] year [1] month [2] day [3] hour
                input_list = list(map(lambda x : int(x), self.hyfp['Time'][F'Time_0000{index + 1}'][:].tolist()))
                input_vlaue = str(input_list[0]) + '%02d' % input_list[1] + '%02d' % input_list[2] + '%02d' %input_list[3]
                result_list.append(int(input_vlaue))
            else:
                input_list = list(map(lambda x : int(x), self.hyfp['Time'][F'Time_000{index + 1}'][:].tolist()))
                input_vlaue = str(input_list[0]) + '%02d' % input_list[1] + '%02d' % input_list[2] + '%02d' %input_list[3]
                result_list.append(int(input_vlaue))                
        return np.array(result_list)

    def __get_u_list(self) -> list:
        result_list = list()
        for index in range(25):
            if index <= 8:
                result_list.append(self.hyfp['Results']['velocity U']['velocity U_0000' + str(index + 1)][:])
            else:
                result_list.append(self.hyfp['Results']['velocity U']['velocity U_000' + str(index + 1)][:])
        return np.array(result_list)

    def __get_v_list(self) -> list:
        result_list = list()
        for index in range(25):
            if index <= 8:
                result_list.append(self.hyfp['Results']['velocity V']['velocity V_0000' + str(index + 1)][:])
            else:
                result_list.append(self.hyfp['Results']['velocity V']['velocity V_000' + str(index + 1)][:])
        return np.array(result_list)

    def __get_elev_list(self) -> list:
        result_list = list()
        for index in range(25):
            if index <= 8:
                result_list.append(self.hyfp['Results']['water level']['water level_0000' + str(index + 1)][:])
            else:
                result_list.append(self.hyfp['Results']['water level']['water level_000' + str(index + 1)][:])
        return np.array(result_list)

    def __get_temp_list(self) -> list:
        result_list = list()
        for index in range(25):
            if index <= 8:
                result_list.append(self.wpfp['Results']['temperature']['temperature_0000' + str(index + 1)][:])
            else:
                result_list.append(self.wpfp['Results']['temperature']['temperature_000' + str(index + 1)][:])
        return np.array(result_list)

    def __get_salt_list(self) -> list:
        result_list = list()
        for index in range(25):
            if index <= 8:
                result_list.append(self.wpfp['Results']['salinity']['salinity_0000' + str(index + 1)][:])
            else:
                result_list.append(self.wpfp['Results']['salinity']['salinity_000' + str(index + 1)][:])
        return np.array(result_list)

    def __get_diff_vertical_list(self) -> list:
        result_list = list()
        for index in range(25):
            if index <= 8:
                result_list.append(self.diff_vertical(self.hyfp['Grid']['VerticalZ']['Vertical_0000' + str(index + 1)][:]))
            else:
                result_list.append(self.diff_vertical(self.hyfp['Grid']['VerticalZ']['Vertical_000' + str(index + 1)][:]))
        return np.array(result_list)

    """ calculator """
    def diff_lat(self, raw_latitude):
        diff_latitude = raw_latitude[:-1,:-1] + np.diff(raw_latitude[:-1,:],axis=1)/2
        return diff_latitude

    def diff_lon(self, raw_longitude):
        diff_longitude = raw_longitude[:-1,:-1] + np.diff(raw_longitude[:,:-1],axis=0)/2
        return diff_longitude

    def diff_vertical(self, raw_vertical):
        diff_vertical = raw_vertical[:-1,:,:] + np.diff(raw_vertical[:,:,:], axis=0)/2
        return diff_vertical

    def var_transpose(self, raw_var_list):
        transpose_var_list = np.transpose(raw_var_list, (0,2,1))
        return transpose_var_list

if __name__ == '__main__':
    ProcessingModule = GetMohidPointValue(sys.argv[1],sys.argv[2])
    ProcessingModule.make_netcdf4(sys.argv[3])

# python /DATA/PYTHON/source/mohid2k/Mohid2kVisNc.py /DATA/PYTHON/source/mohid2k/INPUT/L2_Hydrodynamic_1_2022110412.hdf5 /DATA/PYTHON/source/mohid2k/INPUT/L2_WaterProperties_1_2022110412.hdf5 /DATA/PYTHON/output/mohid2k/L2_Vis_2022110412.nc    