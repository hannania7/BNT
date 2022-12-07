#!/bin/sh

filepath=$1
varname=$2
latstart=$3
lonstart=$4
latend=$5
lonend=$6
cflevels=$7
time=$8

eval python /DATA/PYTHON/source/mohid2k/vslice_mohid2k.py $1 $2 $3 $4 $5 $6 $7 $8

# sh /DATA/PYTHON/source/mohid2k/vslice_mohid2k.sh /DATA/PYTHON/source/mohid2k/OUTPUT/L2_Vis_2022110412.nc sali 37 125 39 128 30,50,2 8