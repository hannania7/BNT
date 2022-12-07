#!/bin/bash

filepath=$1
varname=$2

eval python /DATA/PYTHON+NCL/source/swan/concat_swan.py $filepath $varname
eval python /DATA/PYTHON+NCL/source/swan/concat_minmax_swan.py $filepath $varname

export NCARG_ROOT=/usr/local/ncl-6.6.2
export PATH=$NCARG_ROOT/bin:$PATH
if [ $varname == "Hsig" ]; then
	 ncl fpath=\"$1\" variable=\"Hsig\" /DATA/PYTHON+NCL/source/swan/concat_wgt_swan.ncl
fi
if [ $varname == "Rpeak" ]; then
	 ncl fpath=\"$1\" variable=\"Rpeak\" /DATA/PYTHON+NCL/source/swan/concat_wgt_swan.ncl
fi
if [ $varname == "Wdir" ]; then
	 ncl fpath=\"$1\" variable=\"Wdir\" /DATA/PYTHON+NCL/source/swan/concat_wgt_swan.ncl
fi