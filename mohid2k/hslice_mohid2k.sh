#!/bin/bash

filepath=$1
varname=$2
height=$3
time=$4

eval python /DATA/PYTHON/source/mohid2k/hslice_mohid2k.py $filepath $varname $height $time
# sh /DATA/PYTHON/source/mohid/hslice_mohid2k.sh /DATA/opendap/application/MOHID_113/Mohid_vis/L4_Vis_2020040112.nc sali 20 3

