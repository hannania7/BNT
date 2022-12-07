#!/bin/sh

filepath=$1
varname=$2
latitude=$3
longitude=$4
xrange=$5
timestep=$6

eval python /DATA/PYTHON/source/mohid/vprofile_mohid.py $1 $2 $3 $4 $5 $6

# sh /DATA/PYTHON/source/mohid/vprofile_mohid.sh /DATA/opendap/application/MOHID_113/Mohid_vis/L4_Vis_2020040112.nc temp 33.6291504 127.9248047 [10,34,4] 1
# sh /DATA/PYTHON/source/mohid/vprofile_mohid.sh /DATA/opendap/application/MOHID_113/Mohid_vis/L4_Vis_2020040112.nc sali 33.6291504 127.9248047 [10,34,4] 1
# sh /DATA/PYTHON/source/mohid/vprofile_mohid.sh /DATA/opendap/application/MOHID_113/Mohid_vis/L4_Vis_2020040112.nc u 36.7602539 125.8703613 [-1,1,0.2] 1
# sh /DATA/PYTHON/source/mohid/vprofile_mohid.sh /DATA/opendap/application/MOHID_113/Mohid_vis/L4_Vis_2020040112.nc v 36.7602539 125.8703613 [-1,1,0.2] 1