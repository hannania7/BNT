#!/bin/sh

filepath=$1
varname=$2
latitude=$3
longitude=$4
starttime=$5
endtiem=$6

eval python /DATA/PYTHON+NCL/source/swan/timeserie_swan.py $1 $2 $3 $4 $5 $6


