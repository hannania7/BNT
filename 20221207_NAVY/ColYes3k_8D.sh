#!/bin/bash

export NCARG_ROOT=/usr/local/ncl-6.6.2
export PATH=$NCARG_ROOT/bin:$PATH

today=`date +%Y%m%d`

/usr/bin/python3.6 /DATA/NAVY/source/ColInit2.py 244 $today 9 >> /DATA/NAVY/source/ColMain.log