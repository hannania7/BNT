#!/bin/sh

filepath=$1
varname=$2
latstart=$3
lonstart=$4
latend=$5
lonend=$6
cflevels=$7
time=$8

eval python /DATA/PYTHON/source/mohid/vslice_mohid.py $1 $2 $3 $4 $5 $6 $7 $8

# python /DATA/PYTHON/source/mohid/vslice_mohid.py /DATA/opendap/application/MOHID_113/Mohid_vis/L4_Vis_2020040112.nc u 37.7161 125.6726 37.8040 126.3207 -1,1,0.2 3