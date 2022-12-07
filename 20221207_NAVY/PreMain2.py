#-*- coding:utf-8 -*-

"""
해군 통합해양정보체계
예측자료를 파싱하여 전처리하는 모듈
Mohid300m, Yes3k, WRF dm2, WW3
2021.08.27 이민지 작성
"""

import os
import sys
import subprocess
import datetime
import numpy as np
import DBInsertModule 
import ParsingData
import ColManual    
import CalModelSpeed 
import netCDF4   
# from datetime import datetime
import pandas as pd
import pyproj    
import MakeFilePath2
import psycopg2

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


def run_model_regrid(input_file_path:str, weight_file_path, ncl_path, date) -> str:
    ext = os.path.splitext(input_file_path)[-1]
    if ext == '.nc':
        output_file_path = MakeFilePath2.get_regrid_path(input_file_path)
        if os.path.isfile(output_file_path):
            os.remove(output_file_path)
        subprocess.run( F'ncl ipath=\\"{input_file_path}\\" opath=\\"{output_file_path}\\" '
                        + F'wpath=\\"{weight_file_path}\\" '
                        + ncl_path
                        ,shell=True)
        return output_file_path


def model_db_insert(file_path, model, model_date, data_name):
    if model == 'sf':
        model_object = DBInsertModule.ReadSfInsertDB(file_path)
        input_column = '(obs_post_id, create_time, pred_time, seafog_master)'
        model_object.parsing_value_data()
        data_sql = f"insert into ai_pre_seafog {input_column} values %s"
        model_object.model_data_insert(data_sql)

    elif model == 'SATELLITE':
        input_column = '(codename, obs_time, create_time, file_path)'
        sat_data = DBInsertModule.satellite_db_data(file_path, model_date)
        data_sql = f"insert into satellite_information {input_column} values %s"
        DBInsertModule.satellite_db_insert(data_sql, sat_data)

    else:
        model = model.lower()
        data_name = data_name.lower()
        table_date = model_date.strftime('%Y%m%d')
        flag = False
        if model == 'mohid300':
            for time_val in range(24,72):
                model_object = DBInsertModule.ReadMohid300mInsertDB(file_path, time_val)
                model_object.parsing_value_data(time_val)
                if check_dbinsert('MODEL_MOHID300_DATASET', model_object):
                    DBInsertModule.get_st_id(model_object, model)
                    dataset_sql = f"INSERT INTO MODEL_MOHID300_DATASET_{table_date} (st_id, create_time, pred_time, receive_time) VALUES %s"
                    model_object.model_dataset_insert(dataset_sql)
                    data_sql = f"INSERT INTO MODEL_MOHID300_DATA_{table_date} (st_id, latitude, longitude, cspeed, cdir, u, v, salt, wtemp, idx_x, idx_y) VALUES %s"
                    model_object.model_data_insert(data_sql)
        else:
            # 3일
            if (data_name == 'yes3k' and model == 'yes3k') or (model == 'wrfdm1') or (model == 'wrfdm2') or (model == 'ww3'):
                for time_val in range(72):
                    if model == 'yes3k':
                        model_object = DBInsertModule.ReadYes3kInsertDB(file_path)
                        input_column = "(st_id, latitude, longitude, u, v, wtemp, salt, cspeed, cdir, idx_x, idx_y)"
                    elif model == 'ww3':
                        model_object = DBInsertModule.ReadWw3InsertDB(file_path)
                        input_column = '(st_id, latitude, longitude, wave_height, wave_period, wave_dir, idx_x, idx_y)'
                    elif model == 'wrfdm1':
                        model_object = DBInsertModule.ReadWrfInsertDB(file_path)
                        input_column = '(st_id, latitude, longitude, wspeed, wdir, u, v, atemp, apress, swrad, idx_x, idx_y)'
                    elif model == 'wrfdm2':
                        model_object = DBInsertModule.ReadWrfInsertDB(file_path)
                        input_column = '(st_id, latitude, longitude, wspeed, wdir, u, v, atemp, apress, swrad, idx_x, idx_y)'

                    model_object.parsing_value_data(time_val)
                    if check_dbinsert(f'model_{model}_dataset', model_object):
                        flag = True
                        DBInsertModule.get_st_id(model_object, model)
                        dataset_sql = f"insert into model_{model}_dataset_{table_date} (st_id, create_time, pred_time, receive_time) values %s"
                        model_object.model_dataset_insert(dataset_sql)
                        data_sql = f"insert into model_{model}_data_{table_date} {input_column} values %s"
                        model_object.model_data_insert(data_sql)
                # 2022.6.22 원태찬 DB update하기 위해 추가하는 중, UNIQUE 제약 조건(중복 값 없애기) 때문에 UPDATE가 되지 않음
                    # else:
                    #     flag = True
                    #     st_id = DBInsertModule.get_st_id(model_object, model)
                    #     st_id_up = st_id - time_val
                    #     dataset_sql = f"update model_{model}_dataset_{table_date} set (st_id, create_time, pred_time, receive_time) = %s where st_id = {st_id_up}"
                    #     model_date = file_path.split('/')[-2]
                    #     print(model_date)
                    #     year = int(model_date[:4])
                    #     month = int(model_date[4:6])
                    #     day = int(model_date[6:8])

                    #     create_time = datetime.datetime(year, month, day, 9)
                    #     delta_time = datetime.timedelta(hours=int(time_val))
                    #     pred_time = create_time + delta_time
                    #     receive_time = datetime.datetime.now

                    #     with connect() as connection:
                    #             with connection.cursor() as cursor:
                    #                     cursor.execute(dataset_sql, (st_id_up, create_time, pred_time, receive_time))
                    #             cursor.close()
                    #     connection.close()                
                    #     data_sql = f"update model_{model}_data_{table_date} set {input_column} = %s where st_id = {st_id_up}"
                    #     model_object.model_data_insert(data_sql)
            # 8일
            elif (data_name == 'yes3k_8D' and model == 'yes3k_8D') or (model == 'wrfdm1_8D'):
                for time_val in range(72):
                    if model == 'yes3k_8D':
                        model = 'yes3k'
                        model_object = DBInsertModule.ReadYes3kInsertDB(file_path)
                        input_column = "(st_id, latitude, longitude, u, v, wtemp, salt, cspeed, cdir, idx_x, idx_y)"
                    elif model == 'wrfdm1_8D':
                        model_object = DBInsertModule.ReadWrfInsertDB(file_path)
                        input_column = '(st_id, latitude, longitude, wspeed, wdir, u, v, atemp, apress, swrad, idx_x, idx_y)'

                    model_object.parsing_value_data(time_val)
                    if check_dbinsert(f'model_{model}_dataset', model_object):
                        flag = True
                        DBInsertModule.get_st_id(model_object, model)
                        dataset_sql = f"insert into model_{model}_8D_dataset_{table_date} (st_id, create_time, pred_time, receive_time) values %s"
                        model_object.model_dataset_insert(dataset_sql)
                        data_sql = f"insert into model_{model}_8D_data_{table_date} {input_column} values %s"
                        model_object.model_data_insert(data_sql)
 
            # if flag and model == 'yes3k' or (model == 'wrfdm1'):
            #     CalModelSpeed.main(model.upper(), table_date)

def check_dbinsert(table_name, model_object):
    create_time = model_object.create_time
    pred_time = model_object.pred_time
    time_sql = f"select * from {table_name} where create_time='{create_time}' and pred_time='{pred_time}'"
    result = DBInsertModule.read_query(time_sql)
    if len(result):
        return False
    return True


def get_data_time(file_path):
    file_name = file_path.split("/")[-1].split(".")[0]
    data_time = file_name.split("_")[1][:8]
    return data_time


def make_output_folder_path(output_path, data_time):
    folder_path = output_path + data_time
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    return folder_path


def make_nc_time_path(output_folder_path, time_val):
    data_time = output_folder_path[-8:]
    model_name = output_folder_path.split("/")[-2]
    time_str = "%04d" %time_val
    return f"{output_folder_path}/base_{model_name}_{data_time}_{time_str}.nc"


def u2rho(u):
    dims = u.shape
    dimY = dims[-2]
    dimX = dims[-1]
    ur = np.zeros([dims[0], dimY, dimX + 1], dtype=float)
    ur[:, :, 1:dimX] = 0.5 * (u[:, :, :dimX - 1] + u[:, :, 1:dimX])
    ur[:, :, 0] = ur[:, :, 1]
    ur[:, :, dimX] = ur[:, :, dimX - 1]
    return ur


def v2rho(v):
    dims = v.shape
    dimY = dims[-2]
    dimX = dims[-1]
    vr = np.empty([dims[0], dimY + 1, dimX])
    vr[:, 1:dimY, :] = 0.5 * (v[:, :dimY - 1, :] + v[:, 1:dimY, :])
    vr[:, 0, :] = vr[:, 1, :]
    vr[:, dimY, :] = vr[:, dimY - 1, :]
    return vr


def mask2ndarray(vin):
    vin.set_fill_value(0)
    vout = vin.filled()
    return vout


def get_wrf_end_date(start_date):
    start_datetime = datetime.datetime.strptime(start_date, '%Y%m%d')
    end_datetime = start_datetime + datetime.timedelta(days=2)
    return end_datetime.strftime("%Y%m%d")


def get_model_pred_time(column_row, col_datetime):
    if column_row.get('data_cate2') == 'MOHID300M':
        pred_time = '21:00'
    elif column_row.get('data_cate2') == 'SATELLITE':
        pred_time = col_datetime.strftime("%H:15")
    elif column_row.get('data_cate2') == 'sf':
        pred_time = col_datetime.strftime("%H") + ":00"
    else:
        pred_time = '09:00'
    return pred_time


def scp_sar(file_path, input_dir, date):
    sar_ip = PROPERTY["SAR"]
    sar_pw = PROPERTY["SAR_PW"]
    sar_path = PROPERTY["SAR_PATH"] + input_dir
    subprocess.run(f'sshpass -p {sar_pw} scp -P 22 -r {file_path} {sar_ip}:"{sar_path}"', shell=True)
    server_scp_path = MakeFilePath2.get_sar_scp_log_path(date)
    scp_log = ColManual.get_scp_log(file_path, sar_path)
    ColManual.write_log(server_scp_path, scp_log)

def scp_sar_8D(file_path, file_out, input_dir, date):
    sar_ip = PROPERTY["SAR"]
    sar_pw = PROPERTY["SAR_PW"]
    sar_path = PROPERTY["SAR_PATH"] + input_dir + '/' + file_out
    subprocess.run(f'sshpass -p {sar_pw} scp -P 22 -r {file_path} {sar_ip}:"{sar_path}"', shell=True)
    server_scp_path = MakeFilePath2.get_sar_scp_log_path(date)
    scp_log = ColManual.get_scp_log(file_path, sar_path)
    ColManual.write_log(server_scp_path, scp_log)

def change_coordinate(path, data_row, date, model, data_name):
    # 2022.6.21 원태찬 좌표변환 때문에 추가함
    if (data_name == 'YES3K' and model == 'YES3K') or (data_name == 'YES3K_8D' and model == 'YES3K'):
        ncp = netCDF4.Dataset(path, 'r')
        lon_rho = ncp.variables['lon_rho'][:]
        lat_rho = ncp.variables['lat_rho'][:]
        r_ocean_time = ncp.variables['ocean_time'][:]
        r_u = ncp.variables['u'][:]
        r_v = ncp.variables['v'][:]
        r_temp = ncp.variables['temp'][:]
        r_zeta = ncp.variables['zeta'][:]
        r_mask_rho = ncp.variables['mask_rho'][:]
        r_salt = ncp.variables['salt'][:]
        if (data_name == 'YES3K_8D' and model == 'YES3K'):
            r_angle = ncp.variables['angle'][:]
        c = lon_rho.flatten()
        d = lat_rho.flatten()
        df = pd.DataFrame(zip(c,d), columns = ['lon_rho', 'lat_rho'])
        coord = np.array(df)
        p1_type = "epsg:4326"
        p2_type = "epsg:3857"
        p1 = pyproj.Proj(init=p1_type)
        p2 = pyproj.Proj(init=p2_type)
        fx, fy = pyproj.transform(p1, p2, coord[:, 0], coord[:, 1])
        result = np.dstack([fx, fy])[0]

        lon_rho = result[:, 0]
        lat_rho = result[:, 1]

        r_lon_rho = lon_rho.reshape(642,610)
        r_lat_rho = lat_rho.reshape(642,610)

        eta_rho = ncp.dimensions['eta_rho']
        xi_rho = ncp.dimensions['xi_rho']
        # 3일
        if (data_name == 'YES3K' and model == 'YES3K'):
            change_file_path = MakeFilePath2.change_coordinate_path(data_row, date, model)
        # 8일
        elif (data_name == 'YES3K_8D' and model == 'YES3K'):
            change_file_path = MakeFilePath2.change_coordinate_path_8D(data_row, date, model)
        w_ncp = netCDF4.Dataset(change_file_path, 'w')
        w_ncp.createDimension('ocean_time', r_ocean_time.shape[0])
        w_ncp.createDimension('eta_rho', size=eta_rho.size)
        w_ncp.createDimension('xi_rho', size=xi_rho.size)

        lon_rho = w_ncp.createVariable('lon_rho', 'd', ('eta_rho','xi_rho'))
        lat_rho = w_ncp.createVariable('lat_rho', 'd', ('eta_rho','xi_rho'))
        ocean_time = w_ncp.createVariable('ocean_time', 'd', ('ocean_time'))
        u = w_ncp.createVariable('u', 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=9.96921E36)
        v = w_ncp.createVariable('v', 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=9.96921E36)
        temp = w_ncp.createVariable('temp', 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=0)
        salt = w_ncp.createVariable('salt', 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=0)
        zeta = w_ncp.createVariable('zeta', 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=0)
        if (data_name == 'YES3K_8D' and model == 'YES3K'):
            angle = w_ncp.createVariable('angle', 'd', ('eta_rho', 'xi_rho'))


        mask_rho = w_ncp.createVariable('mask_rho', 'd', ('eta_rho', 'xi_rho'))

        lat_rho[:] = r_lat_rho
        lon_rho[:] = r_lon_rho
        ocean_time[:] = r_ocean_time
        u[:] = r_u
        v[:] = r_v
        temp[:] = r_temp
        salt[:] = r_salt
        zeta[:] = r_zeta
        if (data_name == 'YES3K_8D' and model == 'YES3K'):
            angle[:] = r_angle
        mask_rho[:] = r_mask_rho

        ocean_time.units = "seconds since 1968-05-23 00:00:00 GMT"
        ocean_time.long_name = "time since initialization"
        ocean_time.field = "time, scalar, series"
        ocean_time.calendar = "gregorian"

        lat_rho.long_name = "latitude"
        lat_rho.units = "degrees_north"

        lon_rho.long_name = "longitude"
        lon_rho.units = "degrees_east"

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

        salt.long_name = "salinity"
        salt.units = "psu"
        salt.time = "ocean_time"
        salt.field = "salinity, scalar, series"
        salt.remap = "remapped via ESMF_regrid_with_weights: Bilinear"
        
        if (data_name == 'YES3K_8D' and model == 'YES3K'):
            angle.long_name = "angle between XI-axis and EAST"
            angle.units = "radians"
            angle.coordinates = "lon_rho lat_rho"
            angle.field = "angle, scalar"

        mask_rho.long_name = "mask on RHO-points"
        mask_rho.flag_values = 0.0, 1.0
        mask_rho.flag_meanings = "land water"
        mask_rho.coordinates = "lon_rho lat_rho"
        w_ncp.close()
        
    elif (model == 'WRFDM1') or (model == 'WRFDM1_8D') or (model == 'WRFDM2') or (model == 'WRFDM2_8D'):
        ncp = netCDF4.Dataset(path, 'r')
        lon_rho = ncp.variables['lon_rho'][:]
        lat_rho = ncp.variables['lat_rho'][:]
        r_ocean_time = ncp.variables['ocean_time'][:]
        r_Uwind = ncp.variables['Uwind'][:]
        r_Vwind = ncp.variables['Vwind'][:]
        r_Swrad = ncp.variables['Swrad'][:]
        r_Tair = ncp.variables['Tair'][:]
        r_Pair = ncp.variables['Pair'][:]
        c = lon_rho.flatten()
        d = lat_rho.flatten()
        df = pd.DataFrame(zip(c,d), columns = ['lon_rho', 'lat_rho'])
        coord = np.array(df)
        p1_type = "epsg:4326"
        p2_type = "epsg:3857"
        p1 = pyproj.Proj(init=p1_type)
        p2 = pyproj.Proj(init=p2_type)
        fx, fy = pyproj.transform(p1, p2, coord[:, 0], coord[:, 1])
        result = np.dstack([fx, fy])[0]

        lon_rho = result[:, 0]
        lat_rho = result[:, 1]
        if model == 'WRFDM1' or model == 'WRFDM1_8D':
            r_lon_rho = lon_rho.reshape(217,183)
            r_lat_rho = lat_rho.reshape(217,183)
        elif model == 'WRFDM2' or model == 'WRFDM2_8D':
            r_lon_rho = lon_rho.reshape(270,270)
            r_lat_rho = lat_rho.reshape(270,270)

        eta_rho = ncp.dimensions['eta_rho']
        xi_rho = ncp.dimensions['xi_rho']

        # 3일
        if (model == 'WRFDM1') or (model == 'WRFDM2'):
            change_file_path = MakeFilePath2.change_coordinate_path(data_row, date, model)
        # 8일
        elif (model == 'WRFDM1_8D') or (model == 'WRFDM2_8D'):
            change_file_path = MakeFilePath2.change_coordinate_path_8D(data_row, date, model)
        w_ncp = netCDF4.Dataset(change_file_path, 'w')
        w_ncp.createDimension('ocean_time', r_ocean_time.shape[0])
        w_ncp.createDimension('eta_rho', size=eta_rho.size)
        w_ncp.createDimension('xi_rho', size=xi_rho.size)

        lon_rho = w_ncp.createVariable('lon_rho', 'd', ('eta_rho','xi_rho'))
        lat_rho = w_ncp.createVariable('lat_rho', 'd', ('eta_rho','xi_rho'))
        ocean_time = w_ncp.createVariable('ocean_time', 'd', ('ocean_time'))
        Uwind = w_ncp.createVariable('Uwind', 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=9.96921E36)
        Vwind = w_ncp.createVariable('Vwind', 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=9.96921E36)
        Swrad = w_ncp.createVariable('Swrad', 'd', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=0)
        Tair = w_ncp.createVariable('Tair', 'd', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=0)
        Pair = w_ncp.createVariable('Pair', 'd', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=0)

        lat_rho[:] = r_lat_rho
        lon_rho[:] = r_lon_rho
        ocean_time[:] = r_ocean_time
        Uwind[:] = r_Uwind
        Vwind[:] = r_Vwind
        Swrad[:] = r_Swrad
        Tair[:] = r_Tair
        Pair[:] = r_Pair

        ocean_time.units = "seconds since 1968-05-23 00:00:00 GMT"
        ocean_time.long_name = "time since initialization"
        ocean_time.calendar = "gregorian"
        ocean_time.field = "time, scalar, series"

        lat_rho.long_name = "latitude of RHO-points"
        lat_rho.units = "degree_north"
        lat_rho.standard_name = "latitude"
        lat_rho.field = "lat_rho, scalar"

        lon_rho.long_name = "longitude of RHO-points"
        lon_rho.units = "degree_east"
        lon_rho.standard_name = "longitude"
        lon_rho.field = "lon_rho, scalar"

        Uwind.long_name = "WRF (10m) u winds [m/s]"
        Uwind.units = "meter second-1"
        Uwind.time = "ocean_time"

        Vwind.long_name = "WRF (10m) v winds [m/s]"
        Vwind.units = "meter second-1"
        Vwind.time = "ocean_time"

        Swrad.long_name = "solar shortwave radiation flux"
        Swrad.units = "Watts meter-2"
        Swrad.positive = "downward flux, heating"
        Swrad.negative = "upward flux, cooling"
        Swrad.time = "ocean_time"

        Tair.long_name = "2 metre temperature"
        Tair.units = "Celsius"
        Tair.time = "ocean_time"

        Pair.long_name = "sea level air presure"
        Pair.units = "bar"
        Pair.time = "ocean_time"
        w_ncp.close()
    return change_file_path

def main(data_row, date):
        model = data_row['data_cate2']
        data_name = data_row['data_name']
        model2 = ''
        if data_name == 'DM1_8D':
                model2 = 'wrfdm1'
        elif data_name == 'DM2_8D':
                model2 = 'wrfdm2'
        elif data_name == 'YES3K_8D':
                model2 = 'YES3K'

        ncl_file_path = f'{PROPERTY["NCL_PATH"]}/regrid_{model.lower()}.ncl'
        ncl_file_path_8D = f'{PROPERTY["NCL_PATH"]}/regrid_{model2.lower()}_8D.ncl'
        weight_file_path = f'{PROPERTY["WEIGHT_PATH"]}/wgt_file_{model.lower()}.nc'
        weight_file_path_8D = f'{PROPERTY["WEIGHT_PATH"]}/wgt_file_{model2.lower()}.nc'
        print(ncl_file_path)
        print(weight_file_path)
        if model == 'MOHID300M':
            model = 'MOHID300'
            if data_name == 'TCSMap':
                mohid_tcs_file_path = MakeFilePath2.get_mohid_tcs_save_file_path(data_row, date)
                if os.path.isfile(mohid_tcs_file_path):
                    scp_sar(mohid_tcs_file_path, 'L4_OC', date)

            else:
                mohid300m_file_path = MakeFilePath2.get_mohid300_save_file_path(data_row, date)
                if os.path.isfile(mohid300m_file_path):
                    # model_db_insert(mohid300m_file_path, model, date, data_name)
                    pass

        # 8일치
        elif (data_name == 'YES3K_8D') and (model == 'YES3K_8D') or (data_name == 'YES3K') and (model == 'YES3K'):
                    if model == 'YES3K_8D':
                        yes3k_file_path = MakeFilePath2.make_yes3k_save_file_path_8D(data_row, date)
                        base_yes3k_file_path = os.path.basename(yes3k_file_path)
                        if os.path.isfile(yes3k_file_path):  
                            yes3k_file_path_tr = base_yes3k_file_path.replace('_8D','')
                            scp_sar_8D(yes3k_file_path, yes3k_file_path_tr, 'YES3K', date)
                            # yes3k_regrid_path = run_model_regrid(yes3k_file_path, weight_file_path_8D, ncl_file_path_8D, date)
                            # model_db_insert(yes3k_regrid_path, model, date, data_name)
                            # yes3k_file_path_2 = change_coordinate(yes3k_file_path, data_row, date, model, data_name)
                            # yes3k_regrid_path_2 = run_model_regrid(yes3k_file_path_2, weight_file_path_8D, ncl_file_path_8D, date)
                            # table_date = date.strftime('%Y%m%d')
                            # CalModelSpeed.main(model.upper(), table_date, data_name)
                        
                    # 3일치
                    else:
                        yes3k_file_path = MakeFilePath2.get_yes3k_save_file_path(data_row, date)
                        if os.path.isfile(yes3k_file_path):
                                scp_sar(yes3k_file_path, 'YES3K', date)
                        yes3k_regrid_path = run_model_regrid(yes3k_file_path, weight_file_path, ncl_file_path, date)
                        model_db_insert(yes3k_regrid_path, model, date, data_name)
                        yes3k_file_path_2 = change_coordinate(yes3k_file_path, data_row, date, model, data_name)
                        yes3k_regrid_path_2 = run_model_regrid(yes3k_file_path_2, weight_file_path, ncl_file_path, date)
                        table_date = date.strftime('%Y%m%d')
                        CalModelSpeed.main(model.upper(), table_date, data_name)
                        

        elif model == 'WW3':
                ww3_file_path = MakeFilePath2.get_ww3_save_file_path(data_row, date)
                if os.path.isfile(ww3_file_path):
                        ww3_regrid_path = run_model_regrid(ww3_file_path, weight_file_path, ncl_file_path, date)
                        model_db_insert(ww3_regrid_path, model, date, data_name)

        # 8일치
        elif (data_name == 'DM1_8D') and (model == 'WRF_8D') or (data_name == 'DM1') and (model == 'WRF'):
                model = 'WRF' + data_name
                if model == 'WRFDM1_8D':
                    weight_file_path = f'{PROPERTY["WEIGHT_PATH"]}/wgt_file_wrfdm1.nc'
                    if data_name == 'DM1_8D':
                            wrfdm1_file_path = MakeFilePath2.make_wrf_save_file_path_8D(data_row, date)
                            if os.path.isfile(wrfdm1_file_path):
                                    start_date = date.strftime("%Y%m%d")
                                    end_date = (date + datetime.timedelta(days=2)).strftime("%Y%m%d")
                                    base_save_file_path = f"wrfdm1_{start_date}_{end_date}.nc"
                                    scp_sar_8D(wrfdm1_file_path, base_save_file_path, 'WRF', date)
                                    # wrfdm1_regrid_path = run_model_regrid(wrfdm1_file_path, weight_file_path_8D, ncl_file_path_8D, date)
                                    # model_db_insert(wrfdm1_regrid_path, model, date, data_name)
                                    # wrfdm1_file_path_2 = change_coordinate(wrfdm1_file_path, data_row, date, model, data_name)
                                    # wrfdm1_regrid_path_2 = run_model_regrid(wrfdm1_file_path_2, weight_file_path_8D, ncl_file_path_8D, date)
                                    # table_date = date.strftime('%Y%m%d')
                                    # CalModelSpeed.main(model.upper(), table_date, data_name)
                                
        # 3일치
                else:
                    model = 'WRF' + data_name
                    weight_file_path = f'{PROPERTY["WEIGHT_PATH"]}/wgt_file_{model.lower()}.nc'
                    if data_name == 'DM1':
                            wrfdm1_file_path = MakeFilePath2.get_wrf_save_file_path(data_row, date)
                            if os.path.isfile(wrfdm1_file_path):
                                    scp_sar(wrfdm1_file_path, 'WRF', date)
                    model = 'WRF' + 'DM1'
                    weight_file_path = f'{PROPERTY["WEIGHT_PATH"]}/wgt_file_{model.lower()}.nc'
                    wrfdm1_regrid_path = run_model_regrid(wrfdm1_file_path, weight_file_path, ncl_file_path, date)
                    model_db_insert(wrfdm1_regrid_path, model, date, data_name)
                    wrfdm1_file_path_2 = change_coordinate(wrfdm1_file_path, data_row, date, model, data_name)
                    wrfdm1_regrid_path_2 = run_model_regrid(wrfdm1_file_path_2, weight_file_path, ncl_file_path, date)
                    table_date = date.strftime('%Y%m%d')
                    CalModelSpeed.main(model.upper(), table_date, data_name)

        # elif (data_name == 'DM2') and (model == 'WRF'):
        #         model = 'WRF' + data_name
        #         weight_file_path = f'{PROPERTY["WEIGHT_PATH"]}/wgt_file_{model.lower()}.nc'
        #         if data_name == 'DM2':
        #                 wrfdm2_file_path = MakeFilePath2.get_wrf_save_file_path(data_row, date)
        #                 if os.path.isfile(wrfdm2_file_path):
        #                         scp_sar(wrfdm2_file_path, 'WRF', date)
        #                         wrfdm2_regrid_path = run_model_regrid(wrfdm2_file_path, weight_file_path, ncl_file_path, date)
        #                         model_db_insert(wrfdm2_regrid_path, model, date, data_name)
        #                         wrfdm2_file_path_2 = change_coordinate(wrfdm2_file_path, data_row, date, model, data_name)
        #                         wrfdm2_regrid_path_2 = run_model_regrid(wrfdm2_file_path_2, weight_file_path, ncl_file_path, date)
        #                         table_date = date.strftime('%Y%m%d')
        #                         CalModelSpeed.main(model.upper(), table_date, data_name)



        elif (data_name == 'DM2_8D') and (model == 'WRF_8D_2'):
                model = 'WRF' + data_name
                weight_file_path = f'{PROPERTY["WEIGHT_PATH"]}/wgt_file_wrfdm2.nc'
                if data_name == 'DM2_8D':
                        wrfdm2_file_path = MakeFilePath2.make_wrf_save_file_path_8D(data_row, date)
                        if os.path.isfile(wrfdm2_file_path):
                                start_date = date.strftime("%Y%m%d")
                                end_date = (date + datetime.timedelta(days=2)).strftime("%Y%m%d")
                                base_save_file_path = f"wrfdm2_{start_date}_{end_date}.nc"
                                scp_sar_8D(wrfdm2_file_path, base_save_file_path, 'WRF_8D', date)
                                # wrfdm1_regrid_path = run_model_regrid(wrfdm2_file_path, weight_file_path_8D, ncl_file_path_8D, date)
                                # model_db_insert(wrfdm2_regrid_path, model, date, data_name)
                                # wrfdm2_file_path_2 = change_coordinate(wrfdm2_file_path, data_row, date, model, data_name)
                                # wrfdm2_regrid_path_2 = run_model_regrid(wrfdm2_file_path_2, weight_file_path_8D, ncl_file_path_8D, date)
                                # table_date = date.strftime('%Y%m%d')
                                # CalModelSpeed.main(model.upper(), table_date, data_name)

        elif model == 'sf':
                input_file_path = MakeFilePath2.get_sf_save_file_path(data_row, date)
                if os.path.isfile(input_file_path):
                        model_db_insert(input_file_path, model, date, data_name)

        elif model == 'SATELLITE':
                input_file_path = MakeFilePath2.get_rgb_save_file_path(data_row, date)
                if os.path.isfile(input_file_path):
                        model_db_insert(input_file_path, model, date, data_name)

        elif model == 'MID':
                input_file_path = MakeFilePath2.get_mid_save_path(data_row, date)
                if os.path.isfile(input_file_path):
                        scp_sar(input_file_path, 'MID', date)

        else:
                sys.exit()


if __name__ == "__main__":
    data_row = sys.argv[1]
    date = sys.argv[2]
    main(data_row, date)