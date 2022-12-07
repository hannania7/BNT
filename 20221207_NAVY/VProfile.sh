#!/bin/bash

file_name=$1
model=$2
date=$3
varname=$4
lonlat_array=$5
xrange=$6
time=$7
vprofile_path=$8

/usr/bin/python3.6 /DATA/NAVY/source/VProfile.py $file_name $model $date $varname $lonlat_array $xrange $time $vprofile_path
# python /DATA/NAVY/source/VProfile.py pred_vprofile_yes3k_20201231_10_u_[-1,1,0.25]_20220106150113 yes3k 201231 u [[123.595826,33.45034],[123.595826,33.45034],[124.000372,33.295814],[124.095766,33.000318],[124.30018,32.295532]] [-1,1,0.25] 10 /DATA/NAVY/output/yes3k
