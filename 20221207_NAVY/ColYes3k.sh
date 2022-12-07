#!/bin/bash

export NCARG_ROOT=/usr/local/ncl-6.6.2
export PATH=$NCARG_ROOT/bin:$PATH

today=`date +%Y%m%d`

# /usr/bin/python3.6 /DATA/NAVY/source/ColManual.py 103 $today 9 >> /DATA/NAVY/source/ColMain.log

# /usr/bin/python3.6 /DATA/NAVY/source/ColManual.py 244 $today 9 >> /DATA/NAVY/source/ColMain.log

/usr/bin/python3.6 /DATA/NAVY/source/ColManual.py 103 20220608 9 >> /DATA/NAVY/source/ColMain.log

/usr/bin/python3.6 /DATA/NAVY/source/ColManual.py 244 20221116 9 >> /DATA/NAVY/source/ColMain.log