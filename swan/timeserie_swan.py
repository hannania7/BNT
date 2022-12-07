#!/usr/bin/python3.6

import os
from sys import argv
import sys
import netCDF4
import numpy as np
from datetime import datetime, timedelta
from time import time
import json


def find_thenearest_grd_pts(lat_array,lon_array,latitude,longitude):
    lon = lon_array[:,:] - float(longitude)
    lat = lat_array[:,:] - float(latitude)
    diff = (lon * lon) + (lat * lat)
    j_indices, i_indices = np.where(diff==diff.min())
    j = j_indices[0]
    i = i_indices[0]
    return j, i


def timeserie_swan(filepath,varname,latitude,longitude,starttime,endtime):

    # output 폴더가 없으면 생성
    if not os.path.exists('/DATA/PYTHON+NCL/output/swan/timeserie/json'):
        os.makedirs('/DATA/PYTHON+NCL/output/swan/timeserie/json')
    if not os.path.exists('/DATA/PYTHON+NCL/output/swan/timeserie/txt'):
        os.makedirs('/DATA/PYTHON+NCL/output/swan/timeserie/txt') 
    
    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    yyyymmddhh = filename_without_ext.split('_')[-1]
    startdate = datetime.strptime(yyyymmddhh,"%Y%m%d%H")

    if os.path.exists(filepath): # if file exists

        nc2read = netCDF4.Dataset(filepath)
        src_lat = nc2read.variables['lat'][:,:]
        src_lon = nc2read.variables['lon'][:,:]
            
        j, i = find_thenearest_grd_pts(src_lat[:,:],src_lon[:,:],latitude,longitude)

        if varname =='Hsig':
            varname2 = "Hs"
            var_bin = nc2read.variables[varname2][int(starttime):int(endtime),j,i]   
        elif varname =='Rpeak':
            varname2 = "Tm"
            var_bin = nc2read.variables[varname2][int(starttime):int(endtime),j,i]   
        elif varname =='Wdir':
            varname2 = "wdir"
            var_bin = nc2read.variables[varname2][int(starttime):int(endtime),j,i]   
        else:
            print("The variable name is incorrect! Program halted")
            sys.exit()

        var_bin = var_bin.tolist()
        
        [t] = np.shape(var_bin)
        time = []
        for m in range(t):
            m = float(m)
            hours = timedelta(hours=m)
            temporary = startdate + hours
            temporary = temporary.strftime("%Y%m%d%H")
            time.append(temporary)
        
        data = [{"time" : time, varname : var_bin} for time, var_bin in zip(time, var_bin)]
        with open('/DATA/PYTHON+NCL/output/swan/timeserie/json/timeserie_swan_%s_%s_%s,%s_%s,%s.json' % \
                  (yyyymmddhh,varname,latitude,longitude,starttime,endtime), "w") as fj:
            json.dump(data,fj)

        with open('/DATA/PYTHON+NCL/output/swan/timeserie/txt/timeserie_swan_%s_%s_%s,%s_%s,%s.txt' % \
                  (yyyymmddhh,varname,latitude,longitude,starttime,endtime), "w") as ft:
            ft.write("%s\t%s\n" % ("datetime", varname))
            for k in range(len(time)):
                ft.write("%s\t%.7f" % (time[k], var_bin[k]))
                ft.write("\n")

    else: # if file doesn't exist
        data = {}
        with open('/DATA/PYTHON+NCL/output/swan/timeserie/json/timeserie_swan_%s_%s_%s,%s_%s,%s.json' % \
                  (yyyymmddhh,varname,latitude,longitude,starttime,endtime), "w") as fj:
            json.dump(data,fj)
        with open('/DATA/PYTHON+NCL/output/swan/timeserie/txt/timeserie_swan_%s_%s_%s,%s_%s,%s.txt' % \
                  (yyyymmddhh,varname,latitude,longitude,starttime,endtime), "w") as ft:
            ft.write("")
    return


if __name__ == "__main__":
    
    timeserie_swan(argv[1], argv[2], argv[3], argv[4], argv[5], argv[6])

