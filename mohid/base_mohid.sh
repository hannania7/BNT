#!/bin/bash

filepath=$1
varname=$2
timestep=$3
s_rho=$4

eval python /DATA/PYTHON/source/mohid/base_mohid.py $filepath $varname $timestep $s_rho
eval python /DATA/PYTHON/source/mohid/base_minmax_mohid.py $filepath $varname $timestep $s_rho

# python /DATA/PYTHON/source/mohid/base_mohid.py /DATA/opendap/application/MOHID_113/Mohid_vis/L4_Vis_2022043012.nc sali 8 39
