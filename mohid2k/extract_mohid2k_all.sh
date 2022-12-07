#!/bin/bash

filepath=$1
varname=$2
s_rho=$3
time=$4

eval python /DATA/PYTHON/source/mohid2k/extract_mohid2k_all.py $filepath $varname $s_rho $time

# sh /DATA/PYTHON/source/mohid2k/extract_mohid2k_all.sh /DATA/PYTHON/source/mohid2k/OUTPUT/L2_Vis_2022110412.nc sali 39 8