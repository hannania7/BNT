#!/bin/bash

column_no=$1
col_date=$2
col_time=$3



/usr/bin/python3.6 /DATA/NAVY/source/ColManual2.py $column_no $col_date $col_time >> /DATA/NAVY/source/ColMain.log


#/usr/bin/python3.6 /DATA/NAVY/source/ColManual.py 1 20210602 1
#/usr/bin/python3.6 /DATA/NAVY/source/ColManual.py 4 20210602 13
#/usr/bin/python3.6 /DATA/NAVY/source/ColManual.py 102 20210602 1
#/usr/bin/python3.6 /DATA/NAVY/source/ColManual.py 103 20210602 14
