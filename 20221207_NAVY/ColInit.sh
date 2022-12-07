#!/bin/bash

column_no=$1
col_date=$2
col_time=$3

/usr/bin/python3.6 /DATA/NAVY/source/ColInit2.py $column_no $col_date $col_time >> /DATA/NAVY/source/ColMain.log