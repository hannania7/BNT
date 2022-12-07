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


def timeserie_swan(filepath,latitude,longitude,starttime,endtime):

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

        Hsig = nc2read.variables['Hs'][int(starttime):int(endtime),j,i]   
        Rpeak = nc2read.variables['Tm'][int(starttime):int(endtime),j,i]   
        Wdir = nc2read.variables['wdir'][int(starttime):int(endtime),j,i]   

        Hsig = np.nan_to_num(Hsig, copy=False)
        Rpeak = np.nan_to_num(Rpeak, copy=False)
        Wdir = np.nan_to_num(Wdir, copy=False)

        Hsig_bin = Hsig.tolist()
        Rpeak_bin = Rpeak.tolist()
        Wdir_bin = Wdir.tolist()
        
        [t] = np.shape(Hsig_bin)
        time = []
        for m in range(t):
            m = float(m)
            hours = timedelta(hours=m)
            temporary = startdate + hours
            temporary = temporary.strftime("%Y%m%d%H")
            time.append(temporary)
        
        data = [{"time" : time, "Hsig" : Hsig_bin, "Rpeak" : Rpeak_bin, "Wdir" : Wdir_bin} for time, Hsig_bin, Rpeak_bin, Wdir_bin in zip(time, Hsig_bin, Rpeak_bin, Wdir_bin)]
        with open('/DATA/PYTHON+NCL/output/swan/timeserie/json/timeserie_swan_%s_%s,%s_%s,%s.json' % \
                  (yyyymmddhh,latitude,longitude,starttime,endtime), "w") as fj:
            json.dump(data,fj)

        with open('/DATA/PYTHON+NCL/output/swan/timeserie/txt/timeserie_swan_%s_%s,%s_%s,%s.txt' % \
                  (yyyymmddhh,latitude,longitude,starttime,endtime), "w") as ft:
            ft.write("%s\t%s\t%s\t%s\n" % ("datetime", "Hsig", "Rpeak", "Wdir"))
            for k in range(len(time)):
                ft.write("%s\t%.2f\t%.2f\t%.2f" % (time[k], Hsig_bin[k], Rpeak_bin[k], Wdir_bin[k]))
                ft.write("\n")

    else: # if file doesn't exist
        data = {}
        with open('/DATA/PYTHON+NCL/output/swan/timeserie/json/timeserie_swan_%s_%s,%s_%s,%s.json' % \
                  (yyyymmddhh,latitude,longitude,starttime,endtime), "w") as fj:
            json.dump(data,fj)
        with open('/DATA/PYTHON+NCL/output/swan/timeserie/txt/timeserie_swan_%s_%s,%s_%s,%s.txt' % \
                  (yyyymmddhh,latitude,longitude,starttime,endtime), "w") as ft:
            ft.write("")
    return


if __name__ == "__main__":
    
    timeserie_swan(argv[1], argv[2], argv[3], argv[4], argv[5])

