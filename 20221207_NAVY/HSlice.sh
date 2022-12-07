#!/bin/bash

file_name=$1
model=$2
date=$3
lonlat_array=$4
varname=$5
height=$6
time=$7
h_slice_path=$8

/usr/bin/python3.6 /DATA/NAVY/source/test/HSlice.py $file_name $model $date $lonlat_array $varname $height $time $h_slice_path
# $file_name = '{type}_hslice_{model}_{date_yymmdd}_{time}_{variable}_{height}_{create time_YYYYMMDDHHmmss}'
#python3.6 /DATA/NAVY/source/HSlice.py pred_hslice_yes3k_201231_10_u_30_20220106113000 yes3k 20201231 123,30,135,39 u 30 10 /DATA/NAVY/output/hslice/yes3k
#python3.6 /DATA/NAVY/source/test/HSlice.py pred_hslice_mohid300m_200401_1_temp_10_20211121151529 mohid300m 20200401 temp 10 1