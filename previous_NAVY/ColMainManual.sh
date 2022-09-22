#!/bin/bash

col_date=$1
col_time=$2

/usr/bin/python3.6 /DATA/PYTHON/source/ColMainManual.py $col_date $col_time >> /DATA/PYTHON/source/ColMain.log
