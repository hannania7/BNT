#!/bin/bash

filepath=$1
height=$2
time=$3

eval python /DATA/PYTHON/source/mohid2k/hslice_mohid2k_uv.py $filepath $height $time
# sh /DATA/PYTHON/source/mohid2k/hslice_mohid2k_uv.sh /DATA/opendap/application/MOHID_113/Mohid_vis/L4_Vis_2020040112.nc 50 1

