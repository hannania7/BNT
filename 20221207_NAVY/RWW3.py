import pandas as pd
import numpy as np
import psycopg2
import ParsingData
import psycopg2.extras as extras
import datetime
import os
import DBInsertModule
import MakeFilePath2
import subprocess

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

def get_log_sql(data_no, col_date, obs_time, pred_time):
    log_sql = f"select * from mng_data_col_log where no={data_no} and " \
                  f"data_date='{col_date}' and obs_time='{obs_time}' and pred_time='{pred_time}'"
    return log_sql

def	sshpass_fore(column_row, date, code):
    server_pw = PROPERTY['SERVER_PW']
    server = PROPERTY['SERVER']
    data_cate2 = column_row.get('data_cate2')
    data_name = column_row.get('data_name')
    date_before = date.strftime('%Y%m%d')
    date_str = datetime.datetime.strptime(date_before, "%Y%m%d")
    save_dir_path = MakeFilePath2.get_pred_save_dir_path(column_row, date_str)

    if not os.path.isdir(save_dir_path):
            subprocess.run(f'mkdir -p {save_dir_path}', shell=True)
    
    server_file_path = None
    save_file_path = None 

    if data_cate2 == "RWW3" and data_name == 'yebo':   
            server_file_path = MakeFilePath2.get_RWW3_yebo_remote_path(date, code) 
            save_file_path = MakeFilePath2.get_RWW3_yebo_save_file_path(column_row, date, code) 
    print(server_file_path)
    print(save_file_path)
    subpro_check = list(subprocess.getstatusoutput(f'sh /DATA/NAVY/source/status_test.sh {server_file_path} {server} {server_pw}'))
    # 대내연동수신서버에 파일이 있을 경우
    if subpro_check[1] == 'File exists':
            subprocess.run(f'sshpass -p {server_pw} scp -P 22 -o "StrictHostKeyChecking=no" -r {server}:{server_file_path} {save_dir_path}', shell=True)
    # 대내연동수신서버에 파일이 없을 경우
    elif subpro_check[1] == 'File does not exist':
            pass
    print(subpro_check[1])

    # 파일 점검하기(mng_data_col_head 테이블에서 file_size 비교)
    # 파일 사이즈가 맞으면 anal_stat = 1

    if save_file_path:
            anal_stat = check_file_size(column_row.get('no'), save_file_path, date)

    if save_file_path:
            col_stat = '1' if os.path.isfile(save_file_path) and anal_stat == '1' else '0'
    else:
            col_stat = '0'
    subprocess.run(f'sshpass -p {server_pw} ssh -o "StrictHostKeyChecking=no" {server} rm -f {server_file_path}', shell=True)
    server_remove_path = MakeFilePath2.get_server_remove_log_path(col_datetime) 
    remove_log = get_remove_log(server_file_path, save_file_path)
    write_log(server_remove_path, remove_log)
    return col_stat, server_file_path, save_file_path, subpro_check

def check_file_size(no, file_path, date):
    get_file_size_sql = f'select * from public.mng_data_col_head where no={no};'
    data_row = DBInsertModule.read_query(get_file_size_sql)
    head_file_size = int(data_row['file_size'][0])
    if os.path.isfile(file_path):
        opendap_file_size = int(os.path.getsize(file_path))
    else:
        return '0'
    return '1' if head_file_size <= opendap_file_size else '0'

def get_remove_log(server_path, save_path):
    log_list = list()
    log_list.extend(['대내연동서버 파일 경로 :', server_path, ','])
    log_list.extend(['저장 파일 경로 :', save_path])
    log_list.extend(['실행 시간 :', datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%s')])
    log_list.extend(['\n'])
    log = ' '.join(log_list)
    return log

def write_log(log_path, log):
    if not os.path.isfile(log_path):
        log_file = open(log_path, 'w')
        log_file.close()
    with open(log_path, 'a', encoding='utf-8') as log_file:   
        log_file.write(log)

def check_dbinsert(data_date):
        time_sql = f"select * from model_rww3_data where date='{data_date}'"
        result = DBInsertModule.read_query(time_sql)
        if len(result):
                return False
        return True

flag = '0'
# date 수정
date = '202207140000'

for i in range(0,24):
    now_date = datetime.datetime.now()
    if i < 10:
        i = f'0{i}'
    elif i >= 10:
        i = i
    path_dir = f'/DATA/recv/2021/fore/test/rww3/{i}/'
    file_list = os.listdir(path_dir)
    for i in file_list:
        sepa = i.split('.')[1]
        print(sepa)
        text_test = pd.read_csv(f'{path_dir}/{i}',names = [0], sep = "\t", engine='python', encoding = "cp949")
        # print(text_test)

# 가로로 읽기 유형
# rww3_wavhgt_daas.202207140130, rww3_wavhgt_daas.202207140100

        data_no = 249
        get_col_head_row_sql = f"select * from mng_data_col_head where no={data_no}"
        col_head_row = pd.DataFrame.to_dict(DBInsertModule.read_query(get_col_head_row_sql), orient='index')[0]

        col_datetime = datetime.datetime.strptime(date, "%Y%m%d%H%M")

        # sepa 수정
        # sepa = "/DATA/recv/2021/fore/test/rww3/rww3_wavhgt_daas.202207140330".split('.')[1]
        code = date[8:12]

        col_stat, server_file_path, save_file_path, subpro_check = sshpass_fore(col_head_row, col_datetime, code)
        # text_test 수정
        print(date[0:8])
        text_test = pd.read_csv(f'/DATA/recv/2021/fore/test/rww3/{date[0:8]}/rww3_wavhgt_daas.202207140330',names = [0], sep = "\t", engine='python', encoding = "cp949")
        text_test = text_test[0][1:8000]

        ap2 = list()
        for i in range(1,8000): 
            text_test[i] = text_test[i].split('  ')
            print(text_test[i][1])
            ap = list(filter(None, text_test[i]))
            for j in range(0,19):
                ap[j] = float(ap[j].strip()) / 100
                ap2.append(ap[j]) # wave_height
        print(len(ap2))
        lat = list()
        lon = list()
        st_id = list()
        for i in range(0, 361):
            lat_cal = 50 - ((30/360) * i)
            for j in range(0, 421):
                lat.append(lat_cal)
                lon_cal = 115 + ((35/420) * j)
                lon.append(lon_cal)
        print(len(lat))
        print(len(lon))

        get_st_id_count_sql = f"select count(*) from model_rww3_data"
        row_count = read_query(get_st_id_count_sql)
        if row_count['count'][0] == 0:
            st_id = 1
        else:
            get_st_id_sql = f"select st_id from model_rww3_data ORDER BY st_id DESC LIMIT 1"
            st_id = int(read_query(get_st_id_sql)['st_id'][0] + 1)

        st_id2 = [st_id] * 151981
        data_date = [sepa] * 151981 # date
        ap3 = list()
        ap4 = list()
        ap5 = list()
        ap8 = list()
        for j in range(361, 0, -1):
            ap8 = [j]
            ap6 = ap8 * 421
            ap4.append(ap6)
        idx_y = np.concatenate(ap4).tolist()
        for i in range(1, 422):
            ap5.append(i)
        idx_x = ap5 * 361
        print('c')
        date_time = datetime.datetime.strptime(sepa, '%Y%m%d%H%M')
        print(date_time)
        ap6 = list()
        ap6.append(st_id) # st_id
        ap6.append(date_time) # create_time
        ap6.append(date_time) # pred_time
        ap6.append(now_date) # receive_time

        if check_dbinsert(data_date[0]):
            data_sql = f"insert into model_rww3_dataset (st_id, create_time, pred_time, receive_time) values (%s,%s,%s,%s)"
            with connect() as connection:
                    with connection.cursor() as cursor:
                            cursor.execute(data_sql, tuple(ap6))
                    cursor.close()
            connection.close()


            for pair in zip(st_id2, lat, lon, ap2, idx_x, idx_y, data_date):
                    data_sql = f"insert into model_rww3_data (st_id, latitude, longitude, wave_height, idx_x, idx_y, date) values %s"
                    ap3.append(pair)
                    flag = '1'
            if flag == '1':
                print('b')
                with connect() as connection:
                    with connection.cursor() as cursor:
                        extras.execute_values(cursor, data_sql, ap3)
                    cursor.close()
                connection.close()



            # log테이블 입력
            col_date = date[0:8]
            obs_time_cal = date[8:10]
            obs_time_end = date[10:12]
            if obs_time_cal is not 'null':
                obs_time = f'{obs_time_cal}:{obs_time_end}'
            else:
                obs_time = '-'

            pred_time = '00:00'
            now_date = now_date

            log_sql = get_log_sql(data_no, col_date, obs_time, pred_time)
            col_log_row = DBInsertModule.read_query(log_sql)

            if len(col_log_row) > 0:
                # 로그가 있어도 일단 수집,
                col_cnt = str(int(col_log_row.get('col_cnt')) + 1)
                # 실패 -> 성공
                if col_stat == '1' and subpro_check[1] == 'File exists':
                        sql_set = f"col_stat='{col_stat}', col_cnt='{col_cnt}', reg_date='{now_date}'"
                        sql_where = log_sql.split('where')[1]
                        DBInsertModule.log_db_update(sql_set, sql_where)
                # 성공 -> 실패
                elif col_stat == '1':
                        sql_set = f"col_cnt='{col_cnt}'"
                        sql_where = log_sql.split('where')[1]
                        DBInsertModule.log_db_update(sql_set, sql_where)
                # 실패 -> 실패                  
                elif col_stat == '0':
                        sql_set = f"col_stat='{col_stat}', col_cnt='{col_cnt}', reg_date='{now_date}'"
                        sql_where = log_sql.split('where')[1]
                        DBInsertModule.log_db_update(sql_set, sql_where) 

            else:
                # 로그 없음, 처음 수집
                # 수집, 로그 남기기
                col_cnt = '1'
                # 성공
                if col_stat == '1' and subpro_check[1] == 'File exists':
                    log_data = tuple((data_no, col_date, obs_time, pred_time, col_stat, col_cnt, now_date))
                    DBInsertModule.log_db_insert(log_data)
                # 실패
                else:
                    log_data = tuple((data_no, col_date, obs_time, pred_time, col_stat, col_cnt, now_date))
                    DBInsertModule.log_db_insert(log_data)




# 삭제하기
    # delete = f'{path_dir}/{i}'
    # os.remove(delete)

# 세로로 읽기 유형
        # text_test = pd.read_csv(f'/DATA/recv/2021/fore/test/rww3/{date[0:8]}/rww3_wavhgt_daas.202207140330',names = [0], sep = "\t", engine='python', encoding = "cp949")
        # text_test = text_test[0][1:8000]
        # ap2 = list()
        # for i in range(1,8000):
        #     text_test[i] = text_test[i].split('  ')
        # for j in range(0,19):
        #     for i in range(1,8000): 
        #         ap2.append(text_test[i][j])
        # print(len(ap2))