#!/bin/bash

filepath=$1
timestep=$2
s_rho=$3

eval python /DATA/PYTHON/source/mohid/base_uv_mohid.py $filepath $timestep $s_rho