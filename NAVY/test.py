import netCDF4
# from datetime import datetime
import pandas as pd
import numpy as np
import pyproj
import MakeFilePath
import ParsingData
import subprocess
# import folium
# import geopandas as gpd

PROPERTY_PATH = '/DATA/NAVY/source/property.in'
PROPERTY = ParsingData.read_property(PROPERTY_PATH)

ncp = netCDF4.Dataset('/DATA/recv/2021/pred/YES3K/20220608/YES3K_2022060800.nc', 'r')
lon_rho = ncp.variables['lon_rho'][:]
lat_rho = ncp.variables['lat_rho'][:]
r_ocean_time = ncp.variables['ocean_time'][:]
r_u = ncp.variables['u'][:]
r_v = ncp.variables['v'][:]
r_temp = ncp.variables['temp'][:]
r_salt = ncp.variables['salt'][:]
r_zeta = ncp.variables['zeta'][:]
r_mask_rho = ncp.variables['mask_rho'][:]
c = lon_rho.flatten()
d = lat_rho.flatten()
df = pd.DataFrame(zip(c,d), columns = ['lon_rho', 'lat_rho'])
coord = np.array(df)
p1_type = "epsg:4326"
p2_type = "epsg:3587"
p1 = pyproj.Proj(init=p1_type)
p2 = pyproj.Proj(init=p2_type)
fx, fy = pyproj.transform(p1, p2, coord[:, 0], coord[:, 1])
result = np.dstack([fx, fy])[0]

lon_rho = result[:, 0]
lat_rho = result[:, 1]

r_lon_rho = lon_rho.reshape(642,610)
r_lat_rho = lat_rho.reshape(642,610)

eta_rho = ncp.dimensions['eta_rho']
xi_rho = ncp.dimensions['xi_rho']

w_ncp = netCDF4.Dataset('/DATA/recv/2021/pred/YES3K/20220608/YES3K_2022060800.nc', 'w')

w_ncp.createDimension('ocean_time', r_ocean_time.shape[0])
w_ncp.createDimension('eta_rho', size=eta_rho.size)
w_ncp.createDimension('xi_rho', size=xi_rho.size)

lon_rho = w_ncp.createVariable('lon_rho', 'd', ('eta_rho','xi_rho'))
lat_rho = w_ncp.createVariable('lat_rho', 'd', ('eta_rho','xi_rho'))
ocean_time = w_ncp.createVariable('ocean_time', 'd', ('ocean_time'))
u = w_ncp.createVariable('u', 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=9.96921E36)
v = w_ncp.createVariable('v', 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=9.96921E36)
temp = w_ncp.createVariable('temp', 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=0)
salt = w_ncp.createVariable('salt', 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=0)
zeta = w_ncp.createVariable('zeta', 'f', ('ocean_time', 'eta_rho', 'xi_rho'), fill_value=0)
mask_rho = w_ncp.createVariable('mask_rho', 'd', ('eta_rho', 'xi_rho'))

lat_rho[:] = r_lat_rho
lon_rho[:] = r_lon_rho
ocean_time[:] = r_ocean_time
u[:] = r_u
v[:] = r_v
temp[:] = r_temp
salt[:] = r_salt
zeta[:] = r_zeta
mask_rho[:] = r_mask_rho

ocean_time.units = "seconds since 1968-05-23 00:00:00 GMT"
ocean_time.long_name = "time since initialization"
ocean_time.field = "time, scalar, series"
ocean_time.calendar = "gregorian"

lat_rho.long_name = "latitude"
lat_rho.units = "degrees_north"

lon_rho.long_name = "longitude"
lon_rho.units = "degrees_east"

u.long_name = "sea surface u-momentum component"
u.units = "meter second-1"
u.time = "ocean_time"
u.field = "u-velocity, scalar, series"

v.long_name = "sea surface v-momentum component"
v.units = "meter second-1"
v.time = "ocean_time"
v.field = "v-velocity, scalar, series"

temp.long_name = "potential temperature"
temp.units = "Celsius"
temp.time = "ocean_time"
temp.field = "temperature, scalar, series"

salt.long_name = "salinity"
salt.units = "psu"
salt.time = "ocean_time"
salt.field = "salinity, scalar, series"
salt.remap = "remapped via ESMF_regrid_with_weights: Bilinear"

mask_rho.long_name = "mask on RHO-points"
mask_rho.flag_values = 0.0, 1.0
mask_rho.flag_meanings = "land water"
mask_rho.coordinates = "lon_rho lat_rho"
w_ncp.close()

