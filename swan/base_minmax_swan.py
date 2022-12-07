#!/usr/bin/python3.6

import os
from sys import argv
import sys
import netCDF4
import numpy as np
from datetime import datetime, timedelta
import json

def minmax(filepath,varname,timestep):  
    nc= netCDF4.Dataset(filepath, mode ='r')
    
    if varname == "Hsig":       
        varname2 = "Hs"
        vout = nc.variables[varname2][int(timestep),:,:]
    elif varname == "Rpeak":
        varname2 = "Tm"  
        vout = nc.variables[varname2][int(timestep),:,:]     
    elif varname == "Wdir":
        varname2 = "wdir"    
        vout = nc.variables[varname2][int(timestep),:,:]    
    else:
        print('The input variable, %s does not exist' % varname)
        sys.exit()

    vout[np.isnan(vout)] = 1.0E37
    vout[vout<-999] = 1.0E37
    vout = np.ma.masked_where(vout==1.0E37, vout)

    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    yyyymmdd = filename_without_ext[-10:]
    
    modelname = 'swan'
        
    data = [{"data":varname2,"min": float(np.ma.min(vout[:,:])),"max":float(np.ma.max(vout[:,:]))}]
        
    with open('/DATA/PYTHON+NCL/output/swan/base_%s_%s+%04d_%s_minmax.json' % \
              (modelname,yyyymmdd,int(timestep),varname), "w") as f:
        json.dump(data,f)

    return

if __name__ == "__main__":
    minmax(argv[1], argv[2], argv[3])
