# -*- coding: utf-8 -*-

import os
import psycopg2
import psycopg2.extras as extras
import netCDF4
import numpy as np
import datetime
import pandas as pd
import ParsingData

FILL_VALUE = None

PROPERTY_PATH = '/DATA/NAVY/source/property.in'
PROPERTY = ParsingData.read_property(PROPERTY_PATH)

def connect():
    connection = psycopg2.connect(database=PROPERTY['DATABASE'],
                                  host=PROPERTY['DB_HOST'],
                                  port=PROPERTY['DB_PORT'],
                                  user=PROPERTY['DB_USER'],
                                  password=PROPERTY['DB_PW'])
    connection.autocommit = True
    return connection


def read_query(sql):
    connection = connect()
    result = pd.read_sql_query(sql, con=connection)
    return result


class PreParsingData:

    def get_model_date(self, data_path):
        model_date = data_path.split('/')[-2]
        model_time = int(data_path.split('_regrid')[0][-4:])
        self.model_time = model_time

        year = int(model_date[:4])
        month = int(model_date[4:6])
        day = int(model_date[6:8])

        self.create_time = datetime.datetime(year, month, day, 9)


    def set_pred_time(self, model, file_idx):
        delta_time = datetime.timedelta(hours=int(file_idx))
        self.pred_time = self.create_time + delta_time

    def model_dataset_insert(self, dataset_sql):
        dataset_tuple = self.get_dataset_param_tuple_list()
        print(dataset_sql, dataset_tuple)
        with connect() as connection:
            with connection.cursor() as cursor:
                extras.execute_values(cursor, dataset_sql, dataset_tuple)
            cursor.close()
        connection.close()

    def get_dataset_param_tuple_list(self):
        param_list = list()

        dataset_tuple = self.get_dataset_param_tuple()
        param_list.append(dataset_tuple)

        return param_list

    def get_dataset_param_tuple(self):
        receive_time = datetime.datetime.now()
        result_sql_param = tuple((self.st_id, self.create_time, self.pred_time, receive_time))
        return result_sql_param

    def get_data_param_tuple_list(self):

        param_list = list()
        assert self.parsing_flag, 'You should first do parsing_pickle_data'

        y = len(self.lat)
        x = len(self.lon)

        for y_index in range(y-1, -1, -1):
            for x_index in range(x):
                point_tuple = self.get_data_param_tuple(self.st_id, y_index, x_index)
                param_list.append(point_tuple)
        return param_list

    def model_data_insert(self, data_sql):
        data_tuple = self.get_data_param_tuple_list()
        with connect() as connection:
            with connection.cursor() as cursor:
                extras.execute_values(cursor, data_sql, data_tuple)
            cursor.close()
        connection.close()

    def make_mndarray2ndarray(self, array_p) -> np.ndarray:
        array_p.set_fill_value(FILL_VALUE)
        array_p = array_p.filled()
        return array_p

    def calculate_speed_direction(self):
        speed_array = np.zeros((len(self.lat), len(self.lon)))
        direction_array = np.zeros((len(self.lat), len(self.lon)))
        for lat_idx in range(len(self.lat)):
            for lon_idx in range(len(self.lon)):
                if self.u[lat_idx, lon_idx] >= 10000:
                    speed_array[lat_idx, lon_idx] = FILL_VALUE
                    direction_array[lat_idx, lon_idx] = FILL_VALUE
                else:
                    point_u = self.u[lat_idx, lon_idx]
                    point_v = self.v[lat_idx, lon_idx]
                    if point_u != 0:
                        point_speed = self.__calculate_speed(point_u, point_v)
                        point_direction = self.__calculate_direction(point_u, point_v)

                        speed_array[lat_idx, lon_idx] = point_speed
                        direction_array[lat_idx, lon_idx] = point_direction
        return speed_array, direction_array

    def __calculate_speed(self, u_val, v_val) -> np.ndarray:
        point_speed = np.sqrt((u_val ** 2) + (v_val ** 2))
        return point_speed

    def __calculate_direction(self, u_val, v_val) -> np.ndarray:
        direction_rad = np.arctan2(v_val, u_val)
        direction_deg = np.rad2deg(direction_rad) * -1
        point_direction = direction_deg + 90
        if point_direction >= 360:
            point_direction -= 360
        if point_direction < 0:
            point_direction += 360
        return point_direction


class ReadMohid300mInsertDB(PreParsingData):

    def __init__(self, filepath, time_val):
        self.ncd = netCDF4.Dataset(filepath, mode='r')
        self.lat = self.ncd.variables['lat'][:]
        self.lon = self.ncd.variables['lon'][:]
        self.model_time = time_val
        self.st_id = ''
        self.parsing_flag = False
        self.get_mohid_date(filepath)

    def get_mohid_date(self, filepath):
        model_name = filepath.split('/')[-1]
        self.model_date = model_name.split('.')[0].split('_')[-1]

        year = int(self.model_date[:4])
        month = int(self.model_date[4:6])
        day = int(self.model_date[6:8])
        hour = int(self.model_date[8:])

        self.create_time = datetime.datetime(year, month, day, 21)

    def parsing_value_data(self, file_idx):
        self.set_pred_time("MOHID300M", file_idx)
        self.parsing_flag = True

        self.land_point = self.ncd.variables['null'][self.model_time]

        self.u = self.ncd.variables['u'][self.model_time]
        self.v = self.ncd.variables['v'][self.model_time]
        self.temp = self.ncd.variables['temp'][self.model_time]
        self.salt = self.ncd.variables['sali'][self.model_time]

        self.speed, self.direction = self.calculate_speed_direction()

    def get_data_param_tuple(self, st_id, lat_index, lon_index):

        assert self.parsing_flag, 'You should first do parsing_pickle_data'

        lat = round(float(self.lat[lat_index]), 5)
        lon = round(float(self.lon[lon_index]), 5)
        u = round(float(self.u[lat_index, lon_index]), 3)
        v = round(float(self.v[lat_index, lon_index]), 3)
        temp = round(float(self.temp[lat_index, lon_index]), 3)
        salt = round(float(self.salt[lat_index, lon_index]), 3)
        speed = round(float(self.speed[lat_index, lon_index]), 3)
        direction = round(float(self.direction[lat_index, lon_index]), 3)
        land_point = round(float(self.land_point[lat_index, lon_index]), 3)

        if not land_point:
            u = FILL_VALUE
            v = FILL_VALUE
            temp = FILL_VALUE
            salt = FILL_VALUE
            speed = FILL_VALUE
            direction = FILL_VALUE

        result_sql_param = tuple((st_id, lat, lon, speed, direction, u, v, salt, temp, lon_index, lat_index))
        return result_sql_param


class ReadYes3kInsertDB(PreParsingData):

    def __init__(self, filepath):
        self.ncd = netCDF4.Dataset(filepath, mode='r')
        self.lat = self.ncd.variables['lat'][:]
        self.lon = self.ncd.variables['lon'][:]
        self.st_id = ''
        self.parsing_flag = False
        self.get_model_date(filepath)

    def parsing_value_data(self, file_idx):
        self.set_pred_time('YES3K', file_idx)
        self.parsing_flag = True

        u_array = self.ncd.variables['u'][file_idx, :, :]
        v_array = self.ncd.variables['v'][file_idx, :, :]
        temp_array = self.ncd.variables['temp'][file_idx, :, :]
        salt_array = self.ncd.variables['salt'][file_idx, :, :]

        self.u = self.make_mndarray2ndarray(u_array)
        self.v = self.make_mndarray2ndarray(v_array)
        self.temp = self.make_mndarray2ndarray(temp_array)
        self.salt = self.make_mndarray2ndarray(salt_array)
        self.speed, self.direction = self.calculate_speed_direction()
        self.ncd.close()

    def get_data_param_tuple(self, st_id, lat_index, lon_index):

        assert self.parsing_flag, 'You should first do parsing_pickle_data'

        lat = round(float(self.lat[lat_index]), 5)
        lon = round(float(self.lon[lon_index]), 5)
        u = round(float(self.u[lat_index, lon_index]), 2)
        v = round(float(self.v[lat_index, lon_index]), 2)
        speed = round(float(self.speed[lat_index, lon_index]), 3)
        direction = round(float(self.direction[lat_index, lon_index]), 3)
        temp = round(float(self.temp[lat_index, lon_index]), 3)
        salt = round(float(self.salt[lat_index, lon_index]), 3)

        if u > 1000:
            u = FILL_VALUE
            v = FILL_VALUE
            speed = FILL_VALUE
            direction = FILL_VALUE
            temp = FILL_VALUE
            salt = FILL_VALUE

        result_sql_param = tuple((st_id, lat, lon, u, v, temp, salt, speed, direction, lon_index, lat_index))
        return result_sql_param


class ReadWrfInsertDB(PreParsingData):

    def __init__(self, filepath):
        self.ncd = netCDF4.Dataset(filepath, mode='r')
        self.lat = self.ncd.variables['lat'][:]
        self.lon = self.ncd.variables['lon'][:]
        self.st_id = ''
        self.parsing_flag = False
        self.get_model_date(filepath)

    def parsing_value_data(self, file_idx):
        self.set_pred_time("WRFDM1", file_idx)
        self.parsing_flag = True

        u_array = self.ncd.variables['Uwind'][file_idx, :, :]
        v_array = self.ncd.variables['Vwind'][file_idx, :, :]
        tair_array = self.ncd.variables['Tair'][file_idx, :, :]
        pair_array = self.ncd.variables['Pair'][file_idx, :, :]
        swrad_array = self.ncd.variables['Swrad'][file_idx, :, :]

        self.u = self.make_mndarray2ndarray(u_array)
        self.v = self.make_mndarray2ndarray(v_array)
        self.tair = self.make_mndarray2ndarray(tair_array)
        self.pair = self.make_mndarray2ndarray(pair_array)
        self.swrad = self.make_mndarray2ndarray(swrad_array)
        self.speed, self.direction = self.calculate_speed_direction()
        self.ncd.close()

    def get_data_param_tuple(self, st_id, lat_index, lon_index):

        assert self.parsing_flag, 'You should first do parsing_pickle_data'

        lat = round(float(self.lat[lat_index]), 5)
        lon = round(float(self.lon[lon_index]), 5)
        u = round(float(self.u[lat_index, lon_index]), 3)
        v = round(float(self.v[lat_index, lon_index]), 3)
        speed = round(float(self.speed[lat_index, lon_index]), 3)
        direction = round(float(self.direction[lat_index, lon_index]), 3)
        atemp = round(float(self.tair[lat_index, lon_index]), 3)
        apress = round(float(self.pair[lat_index, lon_index]), 3)
        swrad = round(float(self.swrad[lat_index, lon_index]), 3)

        if u > 1000:
            u = FILL_VALUE
            v = FILL_VALUE
            speed = FILL_VALUE
            direction = FILL_VALUE
            atemp = FILL_VALUE
            apress = FILL_VALUE
            swrad = FILL_VALUE

        result_sql_param = tuple((st_id, lat, lon, speed, direction, u, v, atemp, apress, swrad, lon_index, lat_index))
        return result_sql_param


class ReadWw3InsertDB(PreParsingData):

    def __init__(self, filepath):
        self.ncd = netCDF4.Dataset(filepath, mode='r')
        self.lat = self.ncd.variables['lat'][:]
        self.lon = self.ncd.variables['lon'][:]
        self.st_id = ''
        self.parsing_flag = False
        self.get_model_date(filepath)

    def parsing_value_data(self, file_idx):
        self.set_pred_time("WW3", file_idx)
        self.parsing_flag = True

        hsig_array = self.ncd.variables['Hsig'][file_idx, :, :]
        rpeak_array = self.ncd.variables['Rpeak'][file_idx, :, :]
        wdir_array = self.ncd.variables['Wdir'][file_idx, :, :]

        self.hsig = self.make_mndarray2ndarray(hsig_array)
        self.rpeak = self.make_mndarray2ndarray(rpeak_array)
        self.wdir = self.make_mndarray2ndarray(wdir_array)
        self.ncd.close()

    def get_data_param_tuple(self, st_id, lat_index, lon_index):

        assert self.parsing_flag, 'You should first do parsing_pickle_data'

        lat = round(float(self.lat[lat_index]), 5)
        lon = round(float(self.lon[lon_index]), 5)
        hsig = round(float(self.hsig[lat_index, lon_index]), 2)
        rpeak = round(float(self.rpeak[lat_index, lon_index]), 2)
        wdir = round(float(self.wdir[lat_index, lon_index]), 3)

        if hsig > 1000:
            hsig = FILL_VALUE
            rpeak = FILL_VALUE
            wdir = FILL_VALUE

        result_sql_param = tuple((st_id, lat, lon, hsig, rpeak, wdir, lon_index, lat_index))
        return result_sql_param


class ReadSfInsertDB:
    def __init__(self, file_path):
        self.file_path = file_path
        self.parsing_flag = False

    def parsing_value_data(self):
        with open(self.file_path, 'r', encoding='ISO-8859-1') as fp:
            read_sf_data = fp.readlines()[1:]
            pre_data_list = self.get_parsing_csv(read_sf_data)
        self.parsing_flag = True
        self.data_list = pre_data_list
        return pre_data_list

    def get_parsing_csv(self, pre_data):
        db_data_list = list()
        for pre_row_data in pre_data:
            pre_row_list = pre_row_data.split(",")
            pre_row_list[-1] = pre_row_list[-1].split('\n')[0]
            db_data_list.append(pre_row_list)
        return db_data_list

    def get_data_param_tuple_list(self):
        param_list = list()
        assert self.parsing_flag, 'You should first do parsing_pickle_data'

        for param in self.data_list:
            param_tuple = self.get_data_param_tuple(param)
            param_list.append(param_tuple)
        return param_list

    def get_data_param_tuple(self, data_row):
        data_tuple = tuple(data_row)
        return data_tuple

    def model_data_insert(self, data_sql):
        data_tuple = self.get_data_param_tuple_list()
        if self.check_sf_table(data_tuple):
            with connect() as connection:
                with connection.cursor() as cursor:
                    extras.execute_values(cursor, data_sql, data_tuple)
                cursor.close()
            connection.close()

    def check_sf_table(self, data_tuple):
        obs_post_id = data_tuple[0][0]
        create_time = data_tuple[0][1]
        pred_time = data_tuple[0][2]
        check_sql = f"select * from ai_pre_seafog where obs_post_id='{obs_post_id}' and create_time='{create_time}' and " \
                    f"pred_time='{pred_time}';"
        result_query = read_query(check_sql)
        if len(result_query):
            return False
        return True


class ReadObsInsertDB():
    def __init__(self, obs_parsing_object):
            self.obs_object = obs_parsing_object
            self.station_name = self.obs_object.station_name
            self.file_name = self.obs_object.file_name

    def obs_db_insert(self):
        if self.station_name == 'hf':
                self.get_hf_st_id()
                dataset_sql = f"INSERT INTO model_hfradar_dataset (st_id, create_time, obs_time, obs_post_id, receive_time) VALUES %s"
                self.hf_dataset_insert(dataset_sql)
                # data_sql = f"INSERT INTO model_hfradar_data (st_id, longitude, latitude, u, v, velocity, direction, x_idx, y_idx, idx_x, idx_y) VALUES %s"
                data_sql = f"INSERT INTO model_hfradar_data (st_id, longitude, latitude, u, v, range, bearing, velocity, direction, idx_x, idx_y) VALUES %s"
                self.hf_data_insert(data_sql)

    def check_obs_time(self, table_name):
            obs_post_id = self.obs_object.obs_data_list[0]
            obs_time = self.obs_object.obs_data_list[1]
            check_sql = f"select * from {table_name} where obs_post_id='{obs_post_id}' and obs_time='{obs_time}';"
            check_result = read_query(check_sql)
            if len(check_result):
                    return False
            return True

    def hf_dataset_insert(self, dataset_sql):
            dataset_tuple = self.get_hf_dataset_tuple_list()
            with connect() as connection:
                    with connection.cursor() as cursor:
                            extras.execute_values(cursor, dataset_sql, dataset_tuple)
                    cursor.close()
            connection.close()

    def get_hf_dataset_tuple_list(self):
            param_list = list()

            dataset_tuple = self.get_hf_dataset_tuple()
            param_list.append(dataset_tuple)

            return param_list

    def get_hf_dataset_tuple(self):
            receive_time = datetime.datetime.now()
            create_time = self.obs_object.obs_datetime
            obs_time = self.obs_object.obs_datetime
            sea_area_code = self.obs_object.obs_post_name
            result_sql_param = tuple((self.st_id, create_time, obs_time, sea_area_code, receive_time))
            return result_sql_param

    def hf_data_insert(self, data_sql):
            data_tuple = self.get_hf_data_tuple_list()
            with connect() as connection:
                    with connection.cursor() as cursor:
                            extras.execute_values(cursor, data_sql, data_tuple)
                    cursor.close()
            connection.close()

    def get_hf_data_tuple_list(self):
            param_list = list()

            y = self.obs_object.lat_arr.shape[0]
            x = self.obs_object.lon_arr.shape[0]
            print(f'y, x shape 정보 : {y} {x}')

            for y_index in range(y - 1, -1, -1):
                    for x_index in range(x):
                            point_tuple = self.get_hf_data_tuple(y_index, x_index)
                            param_list.append(point_tuple)
            print(f'넣을 tuple list 갯수 :{len(param_list)}')
            return param_list

    def get_hf_data_tuple(self, y_index, x_index):
            st_id = self.st_id
            lat_length = self.obs_object.idx_y_arr.shape[0] - 1
            lat = self.obs_object.lat_arr[lat_length-y_index]
            lon = self.obs_object.lon_arr[x_index]
            u = self.obs_object.u_arr[y_index,x_index]
            bearing = self.obs_object.bearing_arr[y_index, x_index]
            if u == 0 and bearing == 0:
                    u = FILL_VALUE
                    v = FILL_VALUE
                    range = FILL_VALUE
                    bearing = FILL_VALUE
                    velocity = FILL_VALUE
                    direction = FILL_VALUE
            else:
                    v = self.obs_object.v_arr[y_index,x_index]
                    range = self.obs_object.range_arr[y_index,x_index]
                    velocity = self.obs_object.velocity_arr[y_index,x_index]
                    direction = self.obs_object.direction_arr[y_index,x_index]
            idx_x = self.obs_object.idx_x_arr[x_index]
            idx_y = self.obs_object.idx_y_arr[y_index]

            result_sql_param = tuple((st_id, lon, lat, u, v, range, bearing, velocity, direction, x_index, y_index))
            return result_sql_param


    def get_hf_st_id(self):
            get_st_id_count_sql = f"select count(*) from model_hfradar_dataset"
            row_count = read_query(get_st_id_count_sql)
            if row_count['count'][0] == 0:
                    st_id = 1
            else:
                    get_st_id_sql = f"select st_id from model_hfradar_dataset ORDER BY st_id DESC LIMIT 1"
                    st_id = read_query(get_st_id_sql)['st_id'][0] + 1
            self.st_id = int(st_id)


def get_st_id(object, model_name):
		get_st_id_count_sql = f"select count(*) from model_{model_name}_dataset"
		row_count = read_query(get_st_id_count_sql)
		if row_count['count'][0] == 0:
				st_id = 1
		else:
				get_st_id_sql = f"select st_id from model_{model_name}_dataset ORDER BY st_id DESC LIMIT 1"
				st_id = read_query(get_st_id_sql)['st_id'][0] + 1
		object.st_id = st_id
		return object


def satellite_db_data(file_path, model_date):
		if 'RGB' in file_path:
				code_name = 'RGB'
		elif 'DETECT' in file_path:
				code_name = 'DETECT'
		obs_time = model_date.replace(minute=15)
		result = tuple((code_name, obs_time, obs_time, file_path))
		return result


def satellite_db_insert(satellite_sql, satellite_data):
		with connect() as connection:
				with connection.cursor() as cursor:
						cursor.execute(satellite_sql, (satellite_data,))
				cursor.close()
		connection.close()


def get_satellite_last_seq():
		get_seq_count_sql = f"select count(*) from satellite_information"
		row_count = read_query(get_seq_count_sql)
		if row_count['count'][0] == 0:
				seq = 1
		else:
				get_seq_sql = f"select seq from satellite_information ORDER BY seq DESC LIMIT 1"
				seq = read_query(get_seq_sql)['seq'][0] + 1


def log_db_insert(log_data):
		log_sql = "insert into mng_data_col_log (no, data_date, obs_time, pred_time, col_stat, col_cnt, reg_date) values %s"
		with connect() as connection:
				with connection.cursor() as cursor:
						cursor.execute(log_sql, (log_data,))
				cursor.close()
		connection.close()


def log_db_update(sql_set, sql_where):
		log_sql = f"update mng_data_col_log set {sql_set} where{sql_where}"
		with connect() as connection:
				with connection.cursor() as cursor:
						cursor.execute(log_sql)
				cursor.close()
		connection.close()
