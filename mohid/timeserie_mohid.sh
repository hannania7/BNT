#!/bin/sh

filepath=$1
varname=$2
latitude=$3
longitude=$4
starttime=$5
endtime=$6
s_rho=$7

eval python /DATA/PYTHON/source/mohid/timeserie_mohid.py $1 $2 $3 $4 $5 $6 $7

# sh /DATA/PYTHON/source/mohid/timeserie_mohid.sh /DATA/opendap/application/MOHID_113/Mohid_vis/L4_Vis_2020040112.nc sali 36 124 0 8 39