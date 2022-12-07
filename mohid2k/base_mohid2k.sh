#!/bin/bash

filepath=$1
varname=$2
timestep=$3
s_rho=$4

eval python /DATA/PYTHON/source/mohid2k/base_mohid2k.py $filepath $varname $timestep $s_rho
eval python /DATA/PYTHON/source/mohid2k/base_minmax_mohid2k.py $filepath $varname $timestep $s_rho

# sh /DATA/PYTHON/source/mohid2k/base_mohid2k.sh /DATA/PYTHON/source/mohid2k/OUTPUT/L2_Vis_2022110412.nc sali 8 39
