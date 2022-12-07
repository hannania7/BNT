#!/bin/bash

filepath=$1
varname=$2
timestep=$3

eval python /DATA/PYTHON+NCL/source/swan/base_swan.py $filepath $varname $timestep
eval python /DATA/PYTHON+NCL/source/swan/base_minmax_swan.py $filepath $varname $timestep

export NCARG_ROOT=/usr/local/ncl-6.6.2
export PATH=$NCARG_ROOT/bin:$PATH
if [ $varname == "Hsig" ]; then
	 ncl fpath=\"$1\" variable=\"Hsig\" nt=\"$3\" /DATA/PYTHON+NCL/source/swan/base_wgt_swan.ncl
fi
if [ $varname == "Rpeak" ]; then
	 ncl fpath=\"$1\" variable=\"Rpeak\" nt=\"$3\" /DATA/PYTHON+NCL/source/swan/base_wgt_swan.ncl
fi
if [ $varname == "Wdir" ]; then
	 ncl fpath=\"$1\" variable=\"Wdir\" nt=\"$3\" /DATA/PYTHON+NCL/source/swan/base_wgt_swan.ncl
fi



# sh base_wgt_swan.sh /DATA/opendap/simulation/wave/swan/L4_WA_2022062712.nc wdir 1