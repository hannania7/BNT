import datetime
import os
import subprocess
import ParsingData
import DBInsertModule

PROPERTY_PATH = '/DATA/NAVY/source/property.in'
PROPERTY = ParsingData.read_property(PROPERTY_PATH)

def get_log_path(column_row, date):
    log_folder_path = PROPERTY['LOG_FOLDER_PATH']
    data_cate1 = column_row.get('data_cate1')
    data_cate2 = column_row.get('data_cate2')
    data_name = column_row.get('data_name')
    file_name = data_cate1

    if data_name == 'RGB':
        file_name = data_name
    if data_cate1 == 'pred' and data_cate2 == 'sf':
        file_name = 'pred_sf_station'
    if not os.path.isdir(f'{log_folder_path}/{date}'):
        subprocess.run(f'mkdir {log_folder_path}/{date}', shell=True)
    log_file_path = f'{log_folder_path}/{date}/{file_name}.log'
    return log_file_path


def get_sar_scp_log_path(date):
    log_folder_path = PROPERTY['LOG_FOLDER_PATH']
    date_str = date.strftime('%Y%m%d')
    if not os.path.isdir(f'{log_folder_path}/{date_str}'):
        subprocess.run(f'mkdir {log_folder_path}/{date_str}', shell=True)
    log_file_path = f'{log_folder_path}/{date_str}/sar_scp.log'
    return log_file_path


def get_server_remove_log_path(date):
    log_folder_path = PROPERTY['LOG_FOLDER_PATH']
    date_str = date.strftime('%Y%m%d')
    if not os.path.isdir(f'{log_folder_path}/{date_str}'):
        subprocess.run(f'mkdir {log_folder_path}/{date_str}', shell=True)
    log_file_path = f'{log_folder_path}/{date_str}/server_remove.log'
    return log_file_path

def get_obs_remote_path(column_row, col_datetime):
    server_folder_path = PROPERTY['REMOTE_PATH']
    data_cate2 = column_row.get('data_cate2')
    data_name = column_row.get('data_name').upper()
    date = col_datetime.strftime("%Y%m%d")
    if data_name == 'IPPADO':
        data_name = 'PTDJ'
    if data_cate2 == 'hf':
        file_date = col_datetime.strftime("%Y_%m_%d")
        obs_time = col_datetime.strftime('%H00')
        remote_file_path = f"{server_folder_path}/TOTL_{data_name}_{file_date}_{obs_time}.tuv"
    else:
        remote_file_path = f"{server_folder_path}/{data_name}{date}.dat"
    return remote_file_path


def get_obs_save_file_path(column_row, col_datetime, save_folder_path):
    data_cate2 = column_row.get('data_cate2')
    data_name = column_row.get('data_name').upper()
    date = col_datetime.strftime("%Y%m%d")
    if data_name == 'IPPADO':
        data_name = 'PTDJ'
    if data_cate2 == 'hf':
        file_date = col_datetime.strftime("%Y_%m_%d")
        obs_time = col_datetime.strftime('%H00')
        save_file_path = f"{save_folder_path}/TOTL_{data_name}_{file_date}_{obs_time}.tuv"
    else:
        save_file_path = f"{save_folder_path}/{data_name}{date}.dat"
    return save_file_path


def get_pred_save_dir_path(column_row, date):
    data_path = column_row.get('data_path')
    model_date = date.strftime('%Y%m%d')
    dir_path = f"{data_path}/{model_date}"
    return dir_path

def get_middle_yebo_remote_path(date, code):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    model_date = date.strftime("%Y%m%d%H%M")
    remote_file_path = f"{remote_dir_path}/FCT_WO6_{code}_{model_date}.csv"
    return remote_file_path    

def get_middle_yebo_save_file_path(column_row, date, code):
    data_path = get_pred_save_dir_path(column_row, date)
    model_date = date.strftime("%Y%m%d%H%M")
    save_file_path = f"{data_path}/FCT_WO6_{code}_{model_date}.csv"
    return save_file_path

def get_short_yebo_remote_path(date, code):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    model_date = date.strftime("%Y%m%d%H%M")
    remote_file_path = f"{remote_dir_path}/FCT_DO3_{code}_{model_date}.csv"
    return remote_file_path  

def get_short_yebo_save_file_path(column_row, date, code):
    data_path = get_pred_save_dir_path(column_row, date)
    model_date = date.strftime("%Y%m%d%H%M")
    save_file_path = f"{data_path}/FCT_DO3_{code}_{model_date}.csv"
    return save_file_path

def get_RWW3_yebo_remote_path(date, code):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    model_date = date.strftime("%Y%m%d")
    remote_file_path = f"{remote_dir_path}/rww3_wavhgt_daas.{model_date}{code}"
    return remote_file_path  

def get_RWW3_yebo_save_file_path(column_row, date, code):
    data_path = get_pred_save_dir_path(column_row, date)
    model_date = date.strftime("%Y%m%d")
    save_file_path = f"{data_path}/rww3_wavhgt_daas.{model_date}{code}"
    return save_file_path  

def get_mohid300_remote_path(date):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    date = date - datetime.timedelta(days=1)
    model_date = date.strftime("%Y%m%d12")
    remote_file_path = f"{remote_dir_path}/L4_OC_{model_date}.nc"
    return remote_file_path


def get_mohid300_save_file_path(column_row, date):
    data_path = get_pred_save_dir_path(column_row, date)
    date = date - datetime.timedelta(days=1)
    model_date = date.strftime("%Y%m%d12")
    save_file_path = f"{data_path}/L4_OC_{model_date}.nc"
    return save_file_path


def get_mohid_tcs_remote_path(date):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    date = date - datetime.timedelta(days=1)
    model_date = date.strftime("%Y%m%d12")
    remote_file_path = f"{remote_dir_path}/L4_OC_{model_date}_TCSMap_format.nc"
    return remote_file_path


def get_mohid_tcs_save_file_path(column_row, date):
    data_path = get_pred_save_dir_path(column_row, date)
    date = date - datetime.timedelta(days=1)
    model_date = date.strftime("%Y%m%d12")
    save_file_path = f"{data_path}/L4_OC_{model_date}_TCSMap_format.nc"
    return save_file_path


def get_yes3k_remote_path(date):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    model_date = date.strftime("%Y%m%d00")
    remote_file_path = f"{remote_dir_path}/YES3K_{model_date}.nc"
    return remote_file_path


def get_yes3k_save_file_path(column_row, date):
    data_path = get_pred_save_dir_path(column_row, date)
    model_date = date.strftime("%Y%m%d00")
    save_file_path = f"{data_path}/YES3K_{model_date}.nc"
    return save_file_path

# ColManual 7일 예측자료
def make_yes3k_remote_path_7D(date):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    model_date = date.strftime("%Y%m%d00")
    remote_file_path = f"{remote_dir_path}/YES3K_{model_date}_7D.nc"
    return remote_file_path


def make_yes3k_save_file_path_7D(column_row, date):
    data_path = get_pred_save_dir_path(column_row, date)
    model_date = date.strftime("%Y%m%d00")
    save_file_path = f"{data_path}/YES3K_{model_date}_7D.nc"
    return save_file_path

# 2022.6.22 원태찬 좌표계 적용 때문에 추가(3일)
def change_coordinate_path(column_row, date, model):
    if model == 'YES3K':
        data_path = get_pred_save_dir_path(column_row, date)
        model_date = date.strftime("%Y%m%d00")
        save_file_path = f"{data_path}/{model}_{model_date}_2.nc"
    elif model == 'WRFDM1' or model == 'WRFDM2':
        data_name = column_row.get('data_name').lower()
        data_path = get_pred_save_dir_path(column_row, date)
        start_date = date.strftime("%Y%m%d")
        end_date = (date + datetime.timedelta(days=2)).strftime("%Y%m%d")
        save_file_path = f"{data_path}/wrf{data_name}_{start_date}_{end_date}_2.nc"
    return save_file_path

# 2022.6.22 원태찬 7일치 예측자료 추가
def change_coordinate_path_7D(column_row, date, model):
    if model == 'YES3K':
        data_path = get_pred_save_dir_path(column_row, date)
        model_date = date.strftime("%Y%m%d00")
        save_file_path = f"{data_path}/{model}_{model_date}_7D_2.nc"
    elif model == 'WRFDM1_7D' or model == 'WRFDM2_7D':
        data_name = column_row.get('data_name').lower()
        if data_name == 'dm1_7d':
            data = 'dm1'
        elif data_name == 'dm2_7d':
            data = 'dm2'        
        data_path = get_pred_save_dir_path(column_row, date)
        start_date = date.strftime("%Y%m%d")
        end_date = (date + datetime.timedelta(days=6)).strftime("%Y%m%d")
        save_file_path = f"{data_path}/wrf{data}_{start_date}_{end_date}_7D_2.nc"
    return save_file_path


# 2022.6.22 원태찬 좌표계 적용 때문에 수정
def get_yes3k_regrid_file_path(column_row, date):
    data_path = get_pred_save_dir_path(column_row, date)
    model_date = date.strftime("%Y%m%d00") 
    save_file_path = f"{data_path}/YES3K_{model_date}_2_regrid.nc"
    return save_file_path

# 2022.7.8 원태찬 7일치 예측자료 추가
def get_yes3k_regrid_file_7D_path(column_row, date):
    data_path = get_pred_save_dir_path(column_row, date)
    model_date = date.strftime("%Y%m%d00")
    save_file_path = f"{data_path}/YES3K_{model_date}_7D_2_regrid.nc"
    return save_file_path


def get_wrf_remote_path(date, data_name):
    if data_name == 'dm1' or data_name == 'dm2':
        remote_dir_path = PROPERTY['REMOTE_PATH']
        start_date = date.strftime("%Y%m%d")
        end_date = (date + datetime.timedelta(days=2)).strftime("%Y%m%d")
        dir_date = date.strftime("%Y%m%d")
        remote_file_path = f"{remote_dir_path}/wrf{data_name}_{start_date}_{end_date}.nc"
    elif data_name == 'dm1_7d' or data_name == 'dm2_7d':
        if data_name == 'dm1_7d':
            data = 'dm1'
        elif data_name == 'dm2_7d':
            data = 'dm2'
        remote_dir_path = PROPERTY['REMOTE_PATH']
        start_date = date.strftime("%Y%m%d")
        end_date = (date + datetime.timedelta(days=6)).strftime("%Y%m%d")
        dir_date = date.strftime("%Y%m%d")
        remote_file_path = f"{remote_dir_path}/wrf{data}_{start_date}_{end_date}.nc"
    return remote_file_path


def get_wrf_save_file_path(column_row, date):
    data_name = column_row.get('data_name').lower()
    if data_name == 'dm1' or data_name == 'dm2':
        data_path = get_pred_save_dir_path(column_row, date)
        start_date = date.strftime("%Y%m%d")
        end_date = (date + datetime.timedelta(days=2)).strftime("%Y%m%d")
        save_file_path = f"{data_path}/wrf{data_name}_{start_date}_{end_date}.nc" 
    elif data_name == 'dm1_7d' or data_name == 'dm2_7d':
        if data_name == 'dm1_7d':
            data = 'dm1'
        elif data_name == 'dm2_7d':
            data = 'dm2'  
        data_path = get_pred_save_dir_path(column_row, date)
        start_date = date.strftime("%Y%m%d")
        end_date = (date + datetime.timedelta(days=6)).strftime("%Y%m%d")
        save_file_path = f"{data_path}/wrf{data}_{start_date}_{end_date}.nc" 
    return save_file_path 

# ColManual 7일치 예측자료 추가
def make_wrf_save_file_path_7D(column_row, date):
    data_name = column_row.get('data_name').lower()
    if data_name == 'dm1_7d':
        data = 'dm1'
    elif data_name == 'dm2_7d':
        data = 'dm2'
    data_path = get_pred_save_dir_path(column_row, date)
    start_date = date.strftime("%Y%m%d")
    end_date = (date + datetime.timedelta(days=6)).strftime("%Y%m%d")
    save_file_path = f"{data_path}/wrf{data}_{start_date}_{end_date}.nc"
    return save_file_path

def make_wrf_remote_path_7D(date, data_name):
		if data_name == 'dm1_7d':
				data = 'dm1'
		elif data_name == 'dm2_7d':
				data = 'dm2'
		remote_dir_path = PROPERTY['REMOTE_PATH']
		start_date = date.strftime("%Y%m%d")
		end_date = (date + datetime.timedelta(days=6)).strftime("%Y%m%d")
		dir_date = date.strftime("%Y%m%d")
		remote_file_path = f"{remote_dir_path}/wrf{data}_{start_date}_{end_date}.nc"
		return remote_file_path

# 2022.6.22 원태찬 좌표계 적용 때문에 수정
def get_wrf_regrid_file_path(column_row, date):
    data_name = column_row.get('data_name').lower()
    data_path = get_pred_save_dir_path(column_row, date)
    start_date = date.strftime("%Y%m%d")
    end_date = (date + datetime.timedelta(days=2)).strftime("%Y%m%d")
    save_file_path = f"{data_path}/wrf{data_name}_{start_date}_{end_date}_2_regrid.nc"
    return save_file_path

# 2022.6.22 원태찬 7일치 예측자료 추가
def get_wrf_regrid_file_7D_path(column_row, date):
    data_name = column_row.get('data_name').lower()
    if data_name == 'dm1_7d':
        data = 'dm1'
    elif data_name == 'dm2_7d':
        data = 'dm2'
    data_path = get_pred_save_dir_path(column_row, date)
    start_date = date.strftime("%Y%m%d")
    end_date = (date + datetime.timedelta(days=6)).strftime("%Y%m%d")
    save_file_path = f"{data_path}/wrf{data}_{start_date}_{end_date}_7D_2_regrid.nc"
    return save_file_path


def get_ww3_remote_path(date):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    model_date = date.strftime("%Y%m%d00")
    remote_file_path = f"{remote_dir_path}/WW3_{model_date}.nc"
    return remote_file_path


def get_ww3_save_file_path(column_row, date):
    data_path = get_pred_save_dir_path(column_row, date)
    model_date = date.strftime("%Y%m%d00")
    save_file_path = f"{data_path}/WW3_{model_date}.nc"
    return save_file_path


def get_regrid_path(input_file_path):
    file_dir = '/'.join(input_file_path.split('/')[:-1])
    file_name = os.path.basename(input_file_path).split('.')[0]
    output_file_path = f"{file_dir}/{file_name}_regrid.nc"
    return output_file_path


def get_rgb_remote_path(date):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    model_datetime = date + datetime.timedelta(hours=-9)
    model_date = model_datetime.strftime('%Y%m%d_%H1530')
    remote_file_path = f"{remote_dir_path}/GK2_GOCI2_L1B_{model_date}_LA.jpg"
    return remote_file_path


def get_rgb_save_file_path(column_row, date):
    data_path = get_pred_save_dir_path(column_row, date)
    sat_date = date + datetime.timedelta(hours=-9)
    rgb_file_time_str = sat_date.strftime('%Y%m%d_%H1530')
    save_file_path = f'{data_path}/GK2_GOCI2_L1B_{rgb_file_time_str}_LA.jpg'
    return save_file_path


def get_rgb_tile_file_path(column_row, date, file_num):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    sat_date = date + datetime.timedelta(hours=-9)
    rgb_file_time_str = sat_date.strftime('%Y%m%d_%H1530')
    file_path = f'{remote_dir_path}/GK2_GOCI2_L1B_{rgb_file_time_str}_LA_S{file_num}.jpg'
    return file_path


def get_save_rgb_tile_path(column_row, date, file_num):
    save_dir_path = column_row.get('data_path')
    sat_date = date + datetime.timedelta(hours=-9)
    rgb_file_time_str = sat_date.strftime('%Y%m%d_%H1530')
    file_path = f'{save_dir_path}/GK2_GOCI2_L1B_{rgb_file_time_str}_LA_S{file_num}.jpg'
    return file_path


def get_detect_remote_path():
    pass


def get_detect_save_file_path():
    pass


def get_mid_remote_path(date):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    model_date = (date - datetime.timedelta(days=1)).strftime("%Y%m%d12")
    remote_file_path = f"{remote_dir_path}/MID_KIOPS_OUV_{model_date}_72t.nc"
    return remote_file_path


def get_mid_save_path(column_row, date):
    data_path = get_pred_save_dir_path(column_row, date)
    model_date = (date - datetime.timedelta(days=1)).strftime("%Y%m%d12")
    save_file_path = f"{data_path}/MID_KIOPS_OUV_{model_date}_72t.nc"
    return save_file_path


def get_sf_remote_path(column_row, date):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    sf_date = date - datetime.timedelta(minutes=5)
    sf_file_time_str = sf_date.strftime("%H%M")
    data_name = column_row.get('data_name')
    sf_data_name = get_sf_name(data_name)
    remote_file_path = f'{remote_dir_path}/{sf_data_name}_result{sf_file_time_str}.csv'
    return remote_file_path


def get_sf_save_file_path(column_row, date):
    data_path = get_pred_save_dir_path(column_row, date)
    sf_date = date - datetime.timedelta(minutes=5)
    sf_file_time_str = sf_date.strftime("%H%M")
    data_name = column_row.get('data_name')
    sf_data_name = get_sf_name(data_name)
    save_file_path = f'{data_path}/{sf_data_name}_result{sf_file_time_str}.csv'
    return save_file_path


def get_anal_yes3k_save_dir_path(column_row, date):
    data_path = column_row.get('data_path')
    model_date = date.strftime('%Y%m%d00')
    dir_path = f"{data_path}/{model_date}"
    return dir_path


def get_anal_vis_save_dir_path(column_row, date):
    data_path = column_row.get('data_path')
    model_date = date.strftime('%Y%m%d')
    dir_path = f"{data_path}/{model_date}"
    return dir_path


def get_anal_yes3k_remote_file_path(column_row):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    data_name = column_row.get('data_name')
    remote_file_path = f"{remote_dir_path}/{data_name}.nc"
    return remote_file_path


def get_anal_vis_remote_file_path(column_row, date):
    remote_dir_path = PROPERTY['REMOTE_PATH']
    file_date = date.strftime('%Y%m%d')
    data_name = f'L4_OC_{file_date}_nodepth.nc'
    remote_file_path = f"{remote_dir_path}/{data_name}"
    return remote_file_path


def get_anal_yes3k_save_file_path(column_row, date):
    dir_path = get_anal_yes3k_save_dir_path(column_row, date)
    data_name = column_row.get('data_name')
    file_path = f'{dir_path}/{data_name}.nc'
    return file_path


def get_anal_vis_save_file_path(column_row, date):
    dir_path = get_anal_vis_save_dir_path(column_row, date)
    file_date = date.strftime('%Y%m%d')
    data_name = f'L4_OC_{file_date}_nodepth.nc'
    file_path = f'{dir_path}/{data_name}'
    return file_path


def get_yes3k_depth_file_path(date, time):
    time_str = "%04d" %int(time)
    get_folder_path_sql = f"select data_path from public.mng_data_col_head where data_cate1='anal' and data_cate2='YES3K';"
    yes3k_folder_path = DBInsertModule.read_query(get_folder_path_sql)['data_path'][0]
    basename = f'his_yes3km_{time_str}_nodepth'
    filepath = f'{yes3k_folder_path}/{date}/{basename}.nc'
    return filepath


def get_depth_path(model_name):
    depth_path = f"{PROPERTY['DATA_PATH']}/{model_name}_depth_zeta.nc"
    return depth_path


def get_sf_name(data_name):
    sf_name_dict = {
        'SF_0002': 'NBUSAN',
        'SF_0003': 'ICN',
        'SF_0004': 'PTDJ',
        'SF_0005': 'GS',
        'SF_0006': 'DS',
        'SF_0007': 'MP',
        'SF_0008': 'YG',
        'SF_0009': 'HAE'
    }
    return sf_name_dict.get(data_name)