#!/bin/bash
echo $1 
echo $2
echo $3
ncrcat $1 /DATA/PYTHON+NCL/output/wrf_da/$4"_"$5"_"$6"_"$7"_merge".nc
