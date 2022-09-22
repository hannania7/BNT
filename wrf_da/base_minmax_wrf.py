#!/usr/bin/python3.6

# time 한 지점 2022.7.1 원태찬 구분하기 위해 주석달음(apress, atemp구함)

import os
from sys import argv
import sys
import netCDF4
import numpy as np
import datetime
import json
from datetime import timedelta
import datetime

def minmax(filepath,varname,timestep):  
    nc= netCDF4.Dataset(filepath, mode ='r')
    r_time = nc.variables["ocean_time"][:]
    
    sepa_filepath = os.path.basename(filepath).split('_')[1]
    vout_append = list()   
    if varname == "Pair":
        vout_result = nc.variables[varname][:]
    elif varname == "Tair":
        vout_result = nc.variables[varname][int(timestep),:,:]      
    else:
        sys.exit()

    find_date = os.path.basename(filepath)
    date = find_date.split('_')[1].split('.')[0]
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    print(f"hours since {year}-{month}-{day} {timestep}:00:00")
    # datum = datetime(1968,5,23,0,0,0)
    # hour_date = datetime.datetime.strptime(hour, "%H")
    # new_date = hour_date + timedelta(hours = int(timestep))
    # new_datum = new_date.strftime("%H")

    
    # new_datum_str = 'hours since %s' % new_datum.strftime("%Y-%m-%d %H:%M:%S")

    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    wrfdm = filename_without_ext.split('_')[0]
    # yyyymmddhh = new_datum.strftime("%Y%m%d%H")

    path = os.path.split(filepath)
    modelname = os.path.basename(path[0])
    
    filename_with_ext = os.path.basename(filepath)
    d_type = filename_with_ext.split('_')[0]
    if d_type == 'wrfdm1':
        wrfdm = 'wrfdm1'
    elif d_type == 'wrfdm2':
        wrfdm = 'wrfdm2' 

    data = [{"data":varname,"min": float(np.ma.min(vout_result[:,:])),"max":float(np.ma.max(vout_result[:,:]))}]
        
    with open('/DATA/PYTHON+NCL/output/wrf_da/base_%s_%s_%s+%04d_%s_minmax.json' % \
              ("wrf_da", wrfdm, date,int(timestep),varname), "w") as f:
        json.dump(data,f)

    return

if __name__ == "__main__":
    minmax(argv[1], argv[2], argv[3])
