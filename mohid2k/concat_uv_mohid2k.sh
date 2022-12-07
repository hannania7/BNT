#!/bin/bash

filepath=$1
s_rho=$2

eval python /DATA/PYTHON/source/mohid2k/concat_uv_mohid2k.py $filepath $s_rho

# sh /DATA/PYTHON/source/mohid2k/concat_uv_wgts_mohid2k.sh /DATA/PYTHON/source/mohid2k/OUTPUT/L2_Vis_2022110412.nc 39