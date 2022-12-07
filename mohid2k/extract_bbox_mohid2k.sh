#!/bin/bash

filepath=$1
varname=$2
s_rho=$3
latmin=$4
lonmin=$5
latmax=$6
lonmax=$7
time=$8

eval python /DATA/PYTHON/source/mohid2k/extract_bbox_mohid2k.py $filepath $varname $s_rho $latmin $lonmin $latmax $lonmax $time

# sh /DATA/PYTHON/source/mohid2k/extract_bbox_mohid2k.sh /DATA/PYTHON/source/mohid2k/OUTPUT/L2_Vis_2022110412.nc sali 39 30 123 32 125 8