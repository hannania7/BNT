#!/bin/bash

filepath=$1
count=$2

eval python /DATA/PYTHON+NCL/source/wrf_da/concat_uv_wrf.py $filepath

export NCARG_ROOT=/usr/local/ncl-6.6.2
export PATH=$NCARG_ROOT/bin:$PATH
ncl fpath=\"$1\" /DATA/PYTHON+NCL/source/wrf_da/concat_uv_wgt_wrf.ncl
# sh /DATA/PYTHON+NCL/source/wrf_da/concat_uv_wgt_wrf.sh /DATA/opendap/application/Tidal_atlas/WRF_DA/wrfdm1_20220913_20220916.nc