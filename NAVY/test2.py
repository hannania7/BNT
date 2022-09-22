import netCDF4
# from datetime import datetime
import pandas as pd
import numpy as np
import pyproj
import MakeFilePath
import ParsingData
import subprocess

nc = netCDF4.Dataset('/DATA/recv/2021/pred/YES3K/20220221/YES3K_2022022100.nc')
nc2 = netCDF4.Dataset('/DATA/recv/2021/pred/YES3K/20220221/YES3K_2022022100_2.nc')	
nc3 = netCDF4.Dataset('/DATA/recv/2021/pred/YES3K/20220221/YES3K_2022022100_regrid.nc')
nc4 = netCDF4.Dataset('/DATA/recv/2021/pred/YES3K/20220221/YES3K_2022022100_2_regrid.nc')	

temp_nc = nc.variables['temp'][:][0][0][0]
temp_nc2 = nc2.variables['temp'][:][0][0][0]
temp_regrid = nc3.variables['temp'][:][0][0][0]
temp_regrid2 = nc4.variables['temp'][:][0][0][0]

print(temp_nc)
print(temp_nc2)
print(temp_regrid)
print(temp_regrid2)