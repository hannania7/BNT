#!/bin/bash

export NCARG_ROOT=/usr/local/ncl-6.5.0
export PATH=$NCARG_ROOT/bin:$PATH
ncl /DATA/PYTHON+NCL/source/weight_gen/wrf_da/wrf_da_wrfdm1_wgt_gen.ncl