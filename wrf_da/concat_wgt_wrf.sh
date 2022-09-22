#!/bin/bash

filepath=$1
varname=$2

eval python /DATA/PYTHON+NCL/source/wrf_da/concat_wrf.py $filepath $varname
eval python /DATA/PYTHON+NCL/source/wrf_da/concat_minmax_wrf.py $filepath $varname

export NCARG_ROOT=/usr/local/ncl-6.6.2
export PATH=$NCARG_ROOT/bin:$PATH
 ncl fpath=\"$1\" variable=\"$2\" /DATA/PYTHON+NCL/source/wrf_da/concat_wgt_wrf.ncl
# sh /DATA/PYTHON+NCL/source/wrf_da/concat_wgt_wrf.sh /DATA/opendap/application/Tidal_atlas/WRF_DA/wrfdm1_20220913_20220916.nc Pair