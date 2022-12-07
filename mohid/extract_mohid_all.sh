#!/bin/bash

filepath=$1
varname=$2
s_rho=$3
time=$4

eval python /DATA/PYTHON/source/mohid/extract_mohid_all.py $filepath $varname $s_rho $time