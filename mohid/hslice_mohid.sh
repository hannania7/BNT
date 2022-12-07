#!/bin/bash

filepath=$1
varname=$2
height=$3
time=$4

#eval python /DATA/PYTHON/source/mohid/hslice_mohid.py $filepath $varname $height $time
eval python /DATA/PYTHON/source/mohid/hslice_mohid_test.py $filepath $varname $height $time
# sh /DATA/PYTHON/source/mohid/hslice_mohid.sh /DATA/opendap/application/MOHID_113/Mohid_vis/L4_Vis_2020040112.nc sali 20 3

