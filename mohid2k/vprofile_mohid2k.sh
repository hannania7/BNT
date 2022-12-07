#!/bin/sh

filepath=$1
varname=$2
latitude=$3
longitude=$4
xrange=$5
timestep=$6

eval python /DATA/PYTHON/source/mohid2k/vprofile_mohid2k.py $1 $2 $3 $4 $5 $6

# sh /DATA/PYTHON/source/mohid2k/vprofile_mohid2k.sh /DATA/opendap/application/MOHID_113/Mohid_2k/L2_Vis_2022110412.nc sali 36 124 [5,6,7] 8