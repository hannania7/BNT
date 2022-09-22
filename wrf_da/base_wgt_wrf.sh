#!/bin/bash

filepath=$1
varname=$2
timestep=$3

eval python /DATA/PYTHON+NCL/source/wrf_da/base_wrf.py $filepath $varname $timestep
eval python /DATA/PYTHON+NCL/source/wrf_da/base_minmax_wrf.py $filepath $varname $timestep

export NCARG_ROOT=/usr/local/ncl-6.6.2
export PATH=$NCARG_ROOT/bin:$PATH
ncl fpath=\"$1\" variable=\"$2\" nt=\"$3\" /DATA/PYTHON+NCL/source/wrf_da/base_wgt_wrf.ncl
# sh /DATA/PYTHON+NCL/source/wrf_da/base_wgt_wrf.sh /DATA/opendap/application/Tidal_atlas/WRF_DA/wrfdm1_20220913_20220916.nc Pair 1
