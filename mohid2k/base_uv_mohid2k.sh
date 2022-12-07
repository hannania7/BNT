#!/bin/bash

filepath=$1
timestep=$2
s_rho=$3

eval python /DATA/PYTHON/source/mohid2k/base_uv_mohid2k.py $filepath $timestep $s_rho

# sh /DATA/PYTHON/source/mohid2k/base_uv_wgts_mohid2k.sh /DATA/PYTHON/source/mohid2k/OUTPUT/L2_Vis_2022110412.nc 8 39