# -*- coding: utf-8 -*-

import os
from sys import argv
import sys
import netCDF4
import numpy as np
from datetime import datetime, timedelta
import json

def minmax(filepath,varname,s_rho='99'):
    nc= netCDF4.Dataset(filepath, mode ='r')
    
    if varname == "temp":       
        vout = nc.variables[varname][:,int(s_rho),:,:]
    elif varname == "sali":
        vout = nc.variables['salt'][:,int(s_rho),:,:]
    elif varname == "elev":
        vout = nc.variables[varname][:,:,:]        
    else:
        sys.exit()

    vout=np.ma.masked_where(vout<=-99.9,vout)
    vout.set_fill_value=1.0E37

    filename_with_ext = os.path.basename(filepath)
    filename_without_ext, file_ext = os.path.splitext(filename_with_ext)
    yyyymmdd12 = filename_without_ext[-10:]
    
    path1 = os.path.split(filepath)
    path2 = os.path.split(path1[0])
    foldername = path2[1]

    data = [{"data":varname,"min": float(np.ma.min(vout[:,:,:])),"max":float(np.ma.max(vout[:,:,:]))}]
    
    if varname == 'elev':
        with open('/DATA/PYTHON/output/mohid2k/concat_%s_%s_%s_00_minmax.json' % \
                  (foldername.lower(),yyyymmdd12,varname), "w") as f:
            json.dump(data,f)
    else:   
        with open('/DATA/PYTHON/output/mohid2k/concat_%s_%s_%s_%02d_minmax.json' % \
                  (foldername.lower(),yyyymmdd12,varname,int(s_rho)), "w") as f:
            json.dump(data,f)

    return

if __name__ == "__main__":
    minmax(*argv[1:])
