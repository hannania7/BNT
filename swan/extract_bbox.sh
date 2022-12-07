#!/bin/bash

filepath=$1
varname=$2
time=$3
latmin=$4
lonmin=$5
latmax=$6
lonmax=$7

eval python /DATA/PYTHON+NCL/source/swan/extract_bbox.py $filepath $varname $time $latmin $lonmin $latmax $lonmax

# sh /DATA/PYTHON+NCL/source/swan/extract_bbox.sh /DATA/opendap/simulation/wave/SWAN/L4_WA_2022062712.nc Hsig 3 27.3005 126.6504 34.8162 131.4404