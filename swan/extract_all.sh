#!/bin/bash

filepath=$1
varname=$2
time=$3

eval python /DATA/PYTHON+NCL/source/swan/extract_all.py $filepath $varname $time

# sh /DATA/PYTHON+NCL/source/swan/extract_all.sh /DATA/opendap/simulation/wave/SWAN/L4_WA_2022062712.nc Hsig 3
