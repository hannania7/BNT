#!/bin/bash

column_no=$1
col_date=$2
col_time=$3

python /DATA/NAVY/source/final_ColManual_7D.py $column_no $col_date $col_time >> /DATA/NAVY/source/ColMain.log