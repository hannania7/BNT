# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
import datetime
import subprocess

import DBInsertModule
import ObsMain
import MakeFilePath2
import ParsingData
import PreMain2
PROPERTY_PATH = '/DATA/NAVY/source/property.in'
PROPERTY = ParsingData.read_property(PROPERTY_PATH)

def write_log(log_path, log):
    if not os.path.isfile(log_path):
        log_file = open(log_path, 'w')
        log_file.close()
    with open(log_path, 'a', encoding='utf-8') as log_file:   
        log_file.write(log)


def get_log(column_row, obs_time, pred_time, start_time, end_time, col_stat):
    log_list = list()
    no = column_row.get('no')
    data_cate1 = column_row.get('data_cate1')
    data_cate2 = column_row.get('data_cate2')
    data_name = column_row.get('data_name')

    log_list.extend(['데이터 번호 :', str(no), ','])
    log_list.extend(['데이터 카테고리 :', data_cate2, ','])
    log_list.extend(['데이터 이름 :', data_name, ','])

    if data_cate1 == 'obs':
        log_list.extend(['관측시간 :', obs_time, ','])
        log_list.extend(['수집시간 :', start_time.strftime('%Y/%m/%d %H:%M'), ','])
    else:
        log_list.extend(['예측시간 :', pred_time, ','])
        log_list.extend(['수집시간 :', start_time.strftime('%Y/%m/%d %H:%M'), ','])
        log_list.extend(['DB insert 소요 시간 :', str(end_time - start_time), ','])

    if col_stat == '0':
        log_list.extend(['수집안됨',])
    elif col_stat == '1':
        log_list.extend(['수집됨', ])

    
    log_list.extend(['\n'])
    log = ' '.join(log_list)
    return log


def get_remove_log(server_path, save_path):
    log_list = list()
    log_list.extend(['대내연동서버 파일 경로 :', server_path, ','])
    log_list.extend(['저장 파일 경로 :', save_path])
    log_list.extend(['실행 시간 :', datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%s')])
    log_list.extend(['\n'])
    log = ' '.join(log_list)
    return log


def get_scp_log(server_path, save_path):
    log_list = list()
    log_list.extend(['전송되는 파일 경로 :', server_path, ','])
    log_list.extend(['해수유동서버 저장 파일 경로 :', save_path])
    log_list.extend(['실행 시간 :', datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%s')])
    log_list.extend(['\n'])
    log = ' '.join(log_list)
    return log

def check_obs_file(column_row, file_path, obs_date, time):
    data_cate2 = column_row.get('data_cate2')
    if data_cate2 == 'hf':
        if os.path.isfile(file_path):
            return '1'
        else:
            return '0'
    no = column_row.get('no')
    file_date = file_path.split('/')[-1].split('.')[0]
    data_date = ''
    for string in file_date:
        if 48 <=ord(string) <= 57:
            data_date += string

    get_col_cycle_sql = f'select * from public.mng_data_col_setting where no={no};'

    col_data_time = datetime.datetime.strptime(obs_date, "%Y%m%d")
    col_data_time = col_data_time.replace(hour=int(time))
    col_data_time_str = col_data_time.strftime('%Y/%m/%d %H:%M:%S')
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='cp949') as obs_file:
            file_rows = obs_file.readlines()
            for file_row in file_rows:
                file_time = file_row.split(',')[0]
                if col_data_time_str == file_time:
                    return '1'
    return '0'
def check_file_size_list(no, file_path, date):
    get_file_size_sql = f'select * from public.mng_data_col_head where no={no};'
    data_row = DBInsertModule.read_query(get_file_size_sql)
    if data_row.get('data_cate2')[0] == 'sf':
        check_sf_file(file_path, date)

    head_file_size = data_row['file_size'][0]
    if os.path.isfile(file_path):
        opendap_file_size = str(os.path.getsize(file_path))
    else:
        return '2'
    return '1' if head_file_size <= opendap_file_size else '2'

def check_file_size(no, file_path, date):
    get_file_size_sql = f'select * from public.mng_data_col_head where no={no};'
    data_row = DBInsertModule.read_query(get_file_size_sql)
    if data_row.get('data_cate2')[0] == 'sf':
        check_sf_file(file_path, date)

    head_file_size = data_row['file_size'][0]
    if os.path.isfile(file_path):
        opendap_file_size = str(os.path.getsize(file_path))
    else:
        return '0'
    return '1' if head_file_size <= opendap_file_size else '0'

def check_sf_file(file_path, date):
    # date -= datetime.timedelta(hours=1)
    if os.path.isfile(file_path):
        data = ParsingData.read_csv(file_path)
        data_date = data[0][1]
        date_str = date.strftime('%Y-%m-%d %H:%M:00')
        if not data_date == date_str:
            os.remove(file_path)

def sshpass_obs(column_row, col_datetime):
    server = PROPERTY['SERVER']
    server_pw = PROPERTY['SERVER_PW']
    date = col_datetime.strftime("%Y%m%d")
    obs_time = col_datetime.strftime('%H')
    server_file_path = MakeFilePath2.get_obs_remote_path(column_row, col_datetime)
    save_dir_path = column_row.get('data_path')

    if not os.path.isdir(save_dir_path):
        subprocess.run(f'mkdir -p {save_dir_path}', shell=True)

    # 파일 가져오기
    subprocess.run(f'sshpass -p {server_pw} scp -P 22 -o "StrictHostKeyChecking=no" -r {server}:{server_file_path} {save_dir_path}', shell=True)
    save_file_path = MakeFilePath2.get_obs_save_file_path(column_row, col_datetime, save_dir_path)

    # 점검하기(관측자료는 파일 열고 해당 시간 데이터가 없으면 anal_stat 0으로)
    anal_stat = check_obs_file(column_row, save_file_path, date, obs_time)

    # log 테이블에 로그 남기기(점검 완료 후)
    if save_file_path:
        col_stat = '1' if os.path.isfile(save_file_path) and anal_stat == '1' else '0'
    else:
        col_stat = '0'

    if col_stat == '1':
        subprocess.run(f'sshpass -p {server_pw} ssh -o "StrictHostKeyChecking=no" {server} rm -f {server_file_path}', shell=True)
        server_remove_path = MakeFilePath2.get_server_remove_log_path(col_datetime)
        remove_log = get_remove_log(server_file_path, save_file_path)
        write_log(server_remove_path, remove_log)
    return col_stat

def	sshpass_pred(column_row, date):
    server_pw = PROPERTY['SERVER_PW']
    server = PROPERTY['SERVER']
    data_cate2 = column_row.get('data_cate2')
    data_name = column_row.get('data_name')
    save_dir_path = MakeFilePath2.get_pred_save_dir_path(column_row, date)

    server_file_path = None
    save_file_path = None
    if data_cate2 == 'MOHID300M':
                    if data_name == 'MOHID300M':
                                    server_file_path = MakeFilePath2.get_mohid300_remote_path(date)
                                    save_file_path = MakeFilePath2.get_mohid300_save_file_path(column_row, date)
                    elif data_name == 'TCSMap':
                                    server_file_path = MakeFilePath2.get_mohid_tcs_remote_path(date)
                                    save_file_path = MakeFilePath2.get_mohid_tcs_save_file_path(column_row, date)
    # 3일
    elif data_cate2 == "YES3K" and data_name == 'YES3K':
                                    server_file_path = MakeFilePath2.get_yes3k_remote_path(date)
                                    save_file_path = MakeFilePath2.get_yes3k_save_file_path(column_row, date)

    elif data_cate2 == "WRF" and (data_name == 'DM1' or data_name == 'DM2'):
                                    server_file_path = MakeFilePath2.get_wrf_remote_path(date, data_name.lower())
                                    save_file_path = MakeFilePath2.get_wrf_save_file_path(column_row, date)

    elif data_cate2 == "WW3":
                                    server_file_path = MakeFilePath2.get_ww3_remote_path(date)
                                    save_file_path = MakeFilePath2.get_ww3_save_file_path(column_row, date)
    
    # 7일				
    elif data_cate2 == "YES3K_7D" and data_name == 'YES3K_7D': 
                                    server_file_path = MakeFilePath2.make_yes3k_remote_path_7D(date)
                                    save_file_path = MakeFilePath2.make_yes3k_save_file_path_7D(column_row, date)

    elif data_cate2 == "WRF_7D" and data_name == 'DM1_7D': 
        server_file_path = MakeFilePath2.make_wrf_remote_path_7D(date, data_name.lower())
        save_file_path = MakeFilePath2.make_wrf_save_file_path_7D(column_row, date) 
        
    elif data_cate2 == "WRF_7D_2" and data_name == 'DM2_7D': 
        server_file_path = MakeFilePath2.make_wrf_remote_path_7D(date, data_name.lower())
        save_file_path = MakeFilePath2.make_wrf_save_file_path_7D(column_row, date) 

    elif data_cate2 == 'SATELLITE':
        if data_name == "RGB":
            server_file_path = MakeFilePath2.get_rgb_remote_path(date)
            save_file_path = MakeFilePath2.get_rgb_save_file_path(column_row, date)

        elif data_name == "DETECT":
                    pass

    elif data_cate2 == 'sf':
                    server_file_path = MakeFilePath2.get_sf_remote_path(column_row, date)
                    save_file_path = MakeFilePath2.get_sf_save_file_path(column_row, date)

    elif data_cate2 == "MID":
                    server_file_path = MakeFilePath2.get_mid_remote_path(date)
                    save_file_path = MakeFilePath2.get_mid_save_path(column_row, date)

    if not os.path.isdir(save_dir_path):
                    subprocess.run(f'mkdir -p {save_dir_path}', shell=True)

    subpro_check = list(subprocess.getstatusoutput(f'sh /DATA/NAVY/source/status_test.sh {server_file_path} {server} {server_pw}'))
    print(subpro_check)
    # 대내연동수신서버에 파일이 있을 경우
    if subpro_check[1] == 'File exists':
                    subprocess.run(f'sshpass -p {server_pw} scp -P 22 -o "StrictHostKeyChecking=no" -r {server}:{server_file_path} {save_dir_path}', shell=True)
                    
    # 대내연동수신서버에 파일이 없을 경우
    elif subpro_check[1] == 'File does not exist':
                    pass

    if data_cate2 == 'SATELLITE':
        for i in range(12):
            file_num = "%03d" % i
            if data_name == "RGB":
                            tile_file_path = MakeFilePath2.get_rgb_tile_file_path(column_row, date, file_num)
            elif data_name == "DETECT":
                            tile_file_path = None
            if tile_file_path:
                            subprocess.run(f'sshpass -p {server_pw} scp -P 22 -o "StrictHostKeyChecking=no" -r {server}:{tile_file_path} {save_dir_path}',
                                                                            shell=True)
        # 파일 점검하기(mng_data_col_head 테이블에서 file_size 비교)
        # 파일 사이즈가 맞으면 anal_stat = 1
    if save_file_path:
        anal_stat = check_file_size_list(column_row.get('no'), save_file_path, date)

    if save_file_path:
        col_stat = '1' if os.path.isfile(save_file_path) and anal_stat == '1' else '3'
    else:
        col_stat = '3'
    return col_stat, server_file_path, save_file_path, subpro_check

def sshpass_anal(column_row, date):
    server_pw = PROPERTY['SERVER_PW']
    server = PROPERTY['SERVER']
    data_cate2 = column_row.get('data_cate2')
    data_name = column_row.get('data_name')
    if data_cate2 == 'MOHID300M':
        save_dir_path = MakeFilePath2.get_anal_vis_save_dir_path(column_row, date)
        server_file_path = MakeFilePath2.get_anal_vis_remote_file_path(column_row, date)
        save_file_path = MakeFilePath2.get_anal_vis_save_file_path(column_row, date)

    elif data_cate2 == "YES3K":
        save_dir_path = MakeFilePath2.get_anal_yes3k_save_dir_path(column_row, date)
        server_file_path = MakeFilePath2.get_anal_yes3k_remote_file_path(column_row)
        save_file_path = MakeFilePath2.get_anal_yes3k_save_file_path(column_row, date)
    else:
        save_dir_path = column_row.get('data_path')

    if not os.path.isdir(save_dir_path):
        subprocess.run(f'mkdir -p {save_dir_path}', shell=True)

    # 파일 가져오기
    if data_cate2 == 'MOHID300M' or data_cate2 == 'YES3K':
        subprocess.run(f'sshpass -p {server_pw} scp -P 22 -o "StrictHostKeyChecking=no" -r {server}:{server_file_path} {save_dir_path}', shell=True)

        # 파일 점검하기(mng_data_col_head 테이블에서 file_size 비교)
        # 파일 사이즈가 맞으면 anal_stat = 1
        anal_stat = check_file_size(column_row.get('no'), save_file_path, date)

        # log 테이블에 로그 남기기(점검 완료 후)
        col_stat = '1' if os.path.isfile(save_file_path) and anal_stat == '1' else '0'
    else:
        col_stat = '0'

    if col_stat == '1':
        subprocess.run(f'sshpass -p {server_pw} ssh -o "StrictHostKeyChecking=no" {server} rm -f {server_file_path}', shell=True)
        server_remove_path = MakeFilePath2.get_server_remove_log_path(date)
        remove_log = get_remove_log(server_file_path, save_file_path)
        write_log(server_remove_path, remove_log)
    return col_stat


def get_log_sql(data_no, col_date, obs_time, pred_time):
    log_sql = f"select * from mng_data_col_log where no={data_no} and " \
                  f"data_date='{col_date}' and obs_time='{obs_time}' and pred_time='{pred_time}'"
    return log_sql

def manual_col_main(data_no, col_date, col_time):
    now_date = datetime.datetime.now()
    now_time = now_date.strftime("%H")
    compare_date = col_date + now_time
    arrange_time = col_date + '23'
    now_datetime = datetime.datetime.strptime(compare_date, "%Y%m%d%H")
    trans_date = datetime.datetime.strptime(arrange_time, "%Y%m%d%H")
    date = col_date + col_time
    col_datetime = datetime.datetime.strptime(date, "%Y%m%d%H")
    process_start_time = datetime.datetime.now()
    get_col_head_row_sql = f"select * from mng_data_col_head where no={data_no}"
    col_head_row = pd.DataFrame.to_dict(DBInsertModule.read_query(get_col_head_row_sql), orient='index')[0]

    data_cate1 = col_head_row.get('data_cate1')
    if data_cate1 == 'sea':
        sys.exit()
    if data_cate1 == 'obs':
        obs_time = col_datetime.strftime("%H") + ":00"
        pred_time = "00:00"
    elif data_cate1 == 'pred' or data_cate1 == 'anal':
        obs_time = "00:00"
        pred_time = PreMain2.get_model_pred_time(col_head_row, col_datetime)

    log_sql = get_log_sql(data_no, col_date, obs_time, pred_time)
    col_log_row = DBInsertModule.read_query(log_sql)

    if len(col_log_row) > 0:
        # 로그가 있어도 일단 수집,
        col_cnt = str(int(col_log_row.get('col_cnt')) + 1)
        if data_cate1 == 'obs':
            col_stat = sshpass_obs(col_head_row, col_datetime)
        elif data_cate1 == 'pred':
            col_stat, server_file_path, save_file_path, subpro_check = sshpass_pred(col_head_row, col_datetime)
        elif data_cate1 == 'anal':
            col_stat = sshpass_anal(col_head_row, col_datetime)
    
        if data_cate1 == 'pred':
            # 지연 -> 성공
            if col_stat == '1' and subpro_check[1] == 'File exists':
                sql_set = f"col_stat='{col_stat}', col_cnt='{col_cnt}', reg_date='{now_date}'"
                sql_where = log_sql.split('where')[1]
                DBInsertModule.log_db_update(sql_set, sql_where)
            # 성공 -> 지연
            elif col_stat == '1':
                sql_set = f"col_cnt='{col_cnt}'"
                sql_where = log_sql.split('where')[1]
                DBInsertModule.log_db_update(sql_set, sql_where)
            # 지연 -> 지연                  
            elif col_stat == '3':
                sql_set = f"col_stat='{col_stat}', col_cnt='{col_cnt}'"
                sql_where = log_sql.split('where')[1]
                DBInsertModule.log_db_update(sql_set, sql_where)  

        elif (data_cate1 == 'obs' or data_cate1 == 'anal') and col_stat == '1':
            sql_set = f"col_stat='{col_stat}', col_cnt='{col_cnt}', reg_date='{now_date}'"
            sql_where = log_sql.split('where')[1]
            DBInsertModule.log_db_update(sql_set, sql_where)


    else:
        # 로그 없음, 처음 수집
        # 수집, 로그 남기기
        col_stat = '2'
        col_cnt = '1'
        if data_cate1 == 'obs':
            col_stat = sshpass_obs(col_head_row, col_datetime)
        elif data_cate1 == 'pred':
            col_stat, server_file_path, save_file_path, subpro_check = sshpass_pred(col_head_row, col_datetime)
        elif data_cate1 == 'anal':
            col_stat = sshpass_anal(col_head_row, col_datetime)
        
        if data_cate1 == 'pred':
            # 성공
            if col_stat == '1' and subpro_check[1] == 'File exists':
                sql_set = f"obs_time='{obs_time}', pred_time='{pred_time}', col_stat='{col_stat}', col_cnt='{col_cnt}', reg_date='{now_date}'"
                sql_where = log_sql.split('where')[1]
                DBInsertModule.log_db_update(sql_set, sql_where)
            # 지연
            else:
                sql_set = f"obs_time='{obs_time}', pred_time='{pred_time}', col_stat='{col_stat}', col_cnt='{col_cnt}'"
                sql_where = log_sql.split('where')[1]
                DBInsertModule.log_db_update(sql_set, sql_where)

        elif (data_cate1 == 'obs' or data_cate1 == 'anal') and col_stat == '1':
            log_data = tuple((data_no, col_date, obs_time, pred_time, col_stat, col_cnt, now_date))
            DBInsertModule.log_db_insert(log_data)
        
    server_pw = PROPERTY['SERVER_PW']
    server = PROPERTY['SERVER']
    if col_stat == '1':
        if data_cate1 == 'obs':
            station = col_head_row.get('data_cate2')
            data_name = col_head_row.get('data_name')
            obs_date = col_datetime.strftime("%Y%m%d%H:00")
            ObsMain.main(obs_date, station, data_name)
        # 예측자료와 대내연동수신서버에 파일이 있으면,
        elif data_cate1 == 'pred' and subpro_check[1] == 'File exists':
            PreMain2.main(col_head_row, col_datetime) 
            subprocess.run(f'sshpass -p {server_pw} ssh -o "StrictHostKeyChecking=no" {server} rm -f {server_file_path}', shell=True)
            server_remove_path = MakeFilePath2.get_server_remove_log_path(col_datetime) 
            remove_log = get_remove_log(server_file_path, save_file_path)
            write_log(server_remove_path, remove_log)

    process_end_time = datetime.datetime.now()

    log_path = MakeFilePath2.get_log_path(col_head_row, col_date)
    log = get_log(col_head_row, obs_time, pred_time, process_start_time, process_end_time, col_stat)
    write_log(log_path, log)
    
if __name__ == "__main__":
    data_no = sys.argv[1]
    col_date = sys.argv[2]
    col_time = sys.argv[3]
    # for i in range(224, 242):
    #manual_col_main(66, '20210602','23')
    manual_col_main(data_no, col_date, col_time)