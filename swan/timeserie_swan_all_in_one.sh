#!/bin/sh

filepath=$1
latitude=$2
longitude=$3
starttime=$4
endtiem=$5

eval python /DATA/PYTHON+NCL/source/swan/timeserie_swan_all_in_one.py $1 $2 $3 $4 $5