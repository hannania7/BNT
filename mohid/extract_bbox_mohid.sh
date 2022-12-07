#!/bin/bash

filepath=$1
varname=$2
s_rho=$3
latmin=$4
lonmin=$5
latmax=$6
lonmax=$7
time=$8

eval python /DATA/PYTHON/source/mohid/extract_bbox_mohid.py $filepath $varname $s_rho $latmin $lonmin $latmax $lonmax $time
