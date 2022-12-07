#!/bin/bash

filepath=$1
varname=$2
s_rho=$3

eval python /DATA/PYTHON/source/mohid/concat_mohid.py $filepath $varname $s_rho
eval python /DATA/PYTHON/source/mohid/concat_minmax_mohid.py $filepath $varname $s_rho