#-*- coding:utf-8 -*-

"""
해군 통합해양정보체계
관측자료를 파싱하는 모듈
IE_STATION, KG_STATION, TIDAL_STATION, TW_STATION
2021.08.27 이민지 작성
"""

import os
import sys
import math
import datetime

import numpy as np
import pandas as pd
import DBInsertModule
import ParsingData

FILL_VALUE = 999999999
PROPERTY_PATH = '/DATA/NAVY/source/property.in'
PROPERTY = ParsingData.read_property(PROPERTY_PATH)


def get_station_folder_path(station_name, data_name):
    get_obs_folder_path_sql = f"select * from mng_data_col_head where data_cate1='obs' and data_cate2='{station_name}' and data_name='{data_name}';"
    obs_folder_path = DBInsertModule.read_query(get_obs_folder_path_sql).get('data_path')[0]
    return obs_folder_path


def get_station_post_id(name):
    get_post_id_sql = f"select obs_post_id from public.station where obs_post_id='{name}'"
    station_filenames = DBInsertModule.read_query(get_post_id_sql)
    return station_filenames['obs_post_id'][0]


class ObsObject:
    def __init__(self, folder_path, file_name, obs_date):
        self.obs_date = obs_date
        self.time_delta = datetime.timedelta(hours=1)
        self.obs_datetime = self._str_to_datetime(obs_date)
        self.station_name = folder_path.split('/')[-1]
        self.file_name = file_name.upper()
        self.obs_post_name = get_station_post_id(file_name)

        self.file_path = self.get_file_path(folder_path)

    def _str_to_datetime(self, str_date):
        """
        "YYYYMMDDHH:mm" => datetime
        """
        str_datetime = datetime.datetime.strptime(str_date, "%Y%m%d%H:%M")
        return str_datetime

    def get_file_path(self, folder_path):
        return f"{folder_path}/{self.file_name}{self.obs_date[0:8]}.dat"

    def read_obs_data(self):
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r', encoding='ISO-8859-1') as fp:
                read_obs_data_row = fp.readlines()[4:]
                self.start_data_idx = self.find_insert_index(read_obs_data_row)
                self.obs_data_list = self.get_parsing_dat(read_obs_data_row)
            if self.start_data_idx == -1:
                return False
            return True
        return False

    def get_obs_data_time(self, data_obs_time):
        data_obs_time = data_obs_time.replace('/', '-')
        data_obs_datetime = datetime.datetime.strptime(data_obs_time, "%Y-%m-%d %H:%M:%S")
        data_obs_datetime = data_obs_datetime.replace(second=0)
        return data_obs_datetime

    def find_insert_index(self, obs_data):
        for data_idx, data in enumerate(obs_data):
            data_obs_time = data.split(',')[0]
            data_obs_datetime = self.get_obs_data_time(data_obs_time)

            if self.obs_datetime == data_obs_datetime:
                return data_idx
        return -1

    def get_parsing_dat(self, obs_data):
        obs_row_data = obs_data[self.start_data_idx]
        obs_row_list = obs_row_data.split(",")
        obs_row_list[-1] = obs_row_list[-1].split('\n')[0]
        obs_row_time = self.get_obs_data_time(obs_row_list[0])
        db_insert_value_list = list()

        str_obs_row_time = datetime.datetime.strftime(obs_row_time, "%Y-%m-%d %H:%M:%S")
        db_insert_value_list.append(self.obs_post_name)
        obs_value_list = self.check_null(obs_row_list[1:])

        # make db insert tuple
        db_insert_value_list.append(str_obs_row_time)
        db_insert_value_list += obs_value_list
        if self.station_name == 'kg' or self.station_name =='tw':
            print(db_insert_value_list)
            # 2022.6.23 원태찬 참고사항 적음 lon, lat 제거(db에 없음)
            db_insert_value_list.pop(2)
            db_insert_value_list.pop(2)
        if self.file_name == "SOCHEONGCHO":
            db_insert_value_list.append(None)
        return tuple(db_insert_value_list)

    def check_null(self, value_list):
        result_list = list()
        for value in value_list:
            if value == "-":
                result_list.append(None)
            else:
                result_list.append(round(float(value), 2))
        return result_list


class HfObject(ObsObject):
    def __init__(self, folder_path, file_name, obs_date):
        self.obs_date = obs_date
        self.time_delta = datetime.timedelta(hours=1)
        self.obs_datetime = self._str_to_datetime(obs_date)
        self.station_name = folder_path.split('/')[-1]
        self.file_name = file_name
        self.obs_post_name = get_station_post_id(file_name)
        self.file_path = self.get_file_path(folder_path)

    def read_obs_data(self):
        if os.path.isfile(self.file_path):
            read_obs_data_row = ParsingData.read_tuv(self.file_path)
            self.get_parsing_tuv(read_obs_data_row)
            return True
        return False

    def make_idx_arr(self, grid_info, flag):
        grid_space = grid_info['grid_space']
        if flag == 'x':
            grid_x_min = grid_info['x_min']
            grid_x_max = grid_info['x_max']
            grid_x_origin = grid_info['x_origin']
            grid_x_diff = grid_info['x_diff']

            grid_x_size = int((grid_x_max - grid_x_min) / grid_space)
            idx_x_list = list()
            x_idx = grid_x_min
            for i in range(grid_x_size + 1):
                idx_x_list.append(x_idx)
                x_idx += grid_space

            idx_x_arr = np.array(idx_x_list)
            self.idx_x_arr = np.round(idx_x_arr, 2)

            lon = grid_x_origin
            lon_arr = [lon]
            for i in range(1, self.idx_x_arr.shape[0]):
                lon += grid_x_diff
                lon_arr.append(lon)
            self.lon_arr = np.array(lon_arr)

        elif flag == 'y':
            grid_y_min = grid_info['y_min']
            grid_y_max = grid_info['y_max']
            grid_y_origin = grid_info['y_origin']
            grid_y_diff = grid_info['y_diff']

            grid_y_size = int((grid_y_max - grid_y_min) / grid_space)
            idx_y_list = list()
            y_idx = grid_y_min
            for i in range(grid_y_size + 1):
                idx_y_list.append(y_idx)
                y_idx += grid_space

            idx_y_arr = np.array(idx_y_list)
            self.idx_y_arr = np.round(idx_y_arr, 2)

            lat = grid_y_origin
            lat_arr = [lat]
            for i in range(1, self.idx_y_arr.shape[0]):
                lat -= grid_y_diff
                lat_arr.append(lat)
            self.lat_arr = np.array(lat_arr)

    def get_parsing_tuv(self, obs_data):
        get_grid_info_sql = f"select * from hfradar_grid_info where obs_post_id='{self.file_name}';"
        grid_info = pd.DataFrame.to_dict(DBInsertModule.read_query(get_grid_info_sql), orient='index')[0]

        self.make_idx_arr(grid_info, 'x')
        self.make_idx_arr(grid_info, 'y')
        x_size = self.idx_x_arr.shape[0]
        y_size = self.idx_y_arr.shape[0]

        self.u_arr = np.zeros(shape=(y_size,x_size), dtype=np.float64)
        self.v_arr = np.zeros(shape=(y_size,x_size), dtype=np.float64)
        self.range_arr = np.zeros(shape=(y_size,x_size), dtype=np.float64)
        self.bearing_arr = np.zeros(shape=(y_size,x_size), dtype=np.float64)
        self.velocity_arr = np.zeros(shape=(y_size,x_size), dtype=np.float64)
        self.direction_arr = np.zeros(shape=(y_size,x_size), dtype=np.float64)

        idx_x_arr = list()
        idx_y_arr = list()
        lon_arr = list()
        lat_arr = list()

        for data in obs_data:
            x_dist = float(data[8])
            y_dist = float(data[9])
            x_idx = np.where(self.idx_x_arr == x_dist)
            y_idx = np.where(self.idx_y_arr == y_dist)

            self.u_arr[y_idx,x_idx] = float(data[2])
            self.v_arr[y_idx,x_idx] = float(data[3])
            self.range_arr[y_idx,x_idx] = float(data[10])
            self.bearing_arr[y_idx,x_idx] = float(data[11])
            self.velocity_arr[y_idx,x_idx] = float(data[12])
            self.direction_arr[y_idx,x_idx] = float(data[13])

    def make_lonlat_array(self, space):
        y_dist = (self.lat_arr[-1,0] - self.lat_arr[0,0]) / (self.idx_y_arr.shape[0]-1)
        x_dist = (self.lon_arr[0,-1] - self.lon_arr[0,0]) / (self.idx_x_arr.shape[0]-1)
        for y in range(1, self.idx_y_arr.shape[0]):
            self.lat_arr[y,:] = self.lat_arr[y-1,0] + y_dist
        for x in range(1, self.idx_x_arr.shape[0]):
            self.lon_arr[:,x] = self.lon_arr[0,x-1] + x_dist

    def get_file_path(self, folder_path):
        file_date = self.obs_datetime.strftime('%Y_%m_%d_%H%M')
        return f"{folder_path}/TOTL_{self.file_name}_{file_date}.tuv"


def main(obs_date, station, data_name):
    station_path = get_station_folder_path(station, data_name)
    if station == 'hf':
        obs_object = HfObject(station_path, data_name, obs_date)
    else:
        obs_object = ObsObject(station_path, data_name, obs_date)
    if obs_object.read_obs_data():
        obs_db_object = DBInsertModule.ReadObsInsertDB(obs_object)
        obs_db_object.obs_db_insert()


if __name__ == "__main__":
    obs_date = sys.argv[1]
    station = sys.argv[2]
    data_name = sys.argv[3]
    main(station, obs_date, data_name)
