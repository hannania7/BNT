#!/bin/bash

filepath=$1
varname=$2
s_rho=$3

eval python /DATA/PYTHON/source/mohid2k/concat_mohid2k.py $filepath $varname $s_rho
eval python /DATA/PYTHON/source/mohid2k/concat_minmax_mohid2k.py $filepath $varname $s_rho

# sh /DATA/PYTHON/source/mohid2k/concat_wgts_mohid2k.sh /DATA/PYTHON/source/mohid2k/OUTPUT/L2_Vis_2022110412.nc sali 39