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
import MakeFilePath
import ColManual
import CalModelSpeed

FILL_VALUE = None
PROPERTY_PATH = '/DATA/NAVY/source/property.in'
PROPERTY = ParsingData.read_property(PROPERTY_PATH)


def run_model_regrid(input_file_path:str, weight_file_path, ncl_path, date) -> str:
    ext = os.path.splitext(input_file_path)[-1]
    if ext == '.nc':
        output_file_path = MakeFilePath.get_regrid_path(input_file_path)
        if os.path.isfile(output_file_path):
            os.remove(output_file_path)
        subprocess.run( F'ncl ipath=\\"{input_file_path}\\" opath=\\"{output_file_path}\\" '
                        + F'wpath=\\"{weight_file_path}\\" '
                        + ncl_path
                        ,shell=True)
    return output_file_path


def model_db_insert(file_path, model, model_date):
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
            if flag and model == 'yes3k' or model == 'wrfdm1':
                CalModelSpeed.main(model.upper(), table_date)


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
    server_scp_path = MakeFilePath.get_sar_scp_log_path(date)
    scp_log = ColManual.get_scp_log(file_path, sar_path)
    ColManual.write_log(server_scp_path, scp_log)


def main(data_row, date):
    model = data_row['data_cate2']
    data_name = data_row['data_name']
    ncl_file_path = f'{PROPERTY["NCL_PATH"]}/regrid_{model.lower()}.ncl'
    weight_file_path = f'{PROPERTY["WEIGHT_PATH"]}/wgt_file_{model.lower()}.nc'

    if model == 'MOHID300M':
        model = 'MOHID300'
        if data_name == 'TCSMap':
            mohid_tcs_file_path = MakeFilePath.get_mohid_tcs_save_file_path(data_row, date)
            if os.path.isfile(mohid_tcs_file_path):
                scp_sar(mohid_tcs_file_path, 'L4_OC', date)

        else:
            mohid300m_file_path = MakeFilePath.get_mohid300_save_file_path(data_row, date)
            if os.path.isfile(mohid300m_file_path):
                model_db_insert(mohid300m_file_path, model, date)

    elif model == 'YES3K':
        yes3k_file_path = MakeFilePath.get_yes3k_save_file_path(data_row, date)
        if os.path.isfile(yes3k_file_path):
            scp_sar(yes3k_file_path, 'YES3K', date)
            yes3k_regrid_path = run_model_regrid(yes3k_file_path, weight_file_path, ncl_file_path, date)
            model_db_insert(yes3k_regrid_path, model, date)

    elif model == 'WW3':
        ww3_file_path = MakeFilePath.get_ww3_save_file_path(data_row, date)
        if os.path.isfile(ww3_file_path):
            ww3_regrid_path = run_model_regrid(ww3_file_path, weight_file_path, ncl_file_path, date)
            model_db_insert(ww3_regrid_path, model, date)

    elif model == 'WRF':
        model = model + data_name
        weight_file_path = f'{PROPERTY["WEIGHT_PATH"]}/wgt_file_{model.lower()}.nc'
        if data_name == 'DM1':
            wrfdm1_file_path = MakeFilePath.get_wrf_save_file_path(data_row, date)
            if os.path.isfile(wrfdm1_file_path):
                scp_sar(wrfdm1_file_path, 'WRF', date)
                wrfdm1_regrid_path = run_model_regrid(wrfdm1_file_path, weight_file_path, ncl_file_path, date)
                model_db_insert(wrfdm1_regrid_path, model, date)
        elif data_name == 'DM2':
            wrfdm2_file_path = MakeFilePath.get_wrf_save_file_path(data_row, date)

    elif model == 'sf':
        input_file_path = MakeFilePath.get_sf_save_file_path(data_row, date)
        if os.path.isfile(input_file_path):
            model_db_insert(input_file_path, model, date)

    elif model == 'SATELLITE':
        input_file_path = MakeFilePath.get_rgb_save_file_path(data_row, date)
        if os.path.isfile(input_file_path):
            model_db_insert(input_file_path, model, date)

    elif model == 'MID':
        input_file_path = MakeFilePath.get_mid_save_path(data_row, date)
        if os.path.isfile(input_file_path):
            scp_sar(input_file_path, 'MID', date)

    else:
        sys.exit()


if __name__ == "__main__":
    data_row = sys.argv[1]
    date = sys.argv[2]
    main(data_row, date)