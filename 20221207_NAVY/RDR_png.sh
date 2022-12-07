#!/bin/bash

today=`date +%Y%m%d`
time2=`date +%H`

# RDR
/usr/bin/python3.6 /DATA/NAVY/source/weather_png.py 250 $today $time2 >> /DATA/NAVY/source/ColMain.log