#!/bin/bash

today=`date +%Y%m%d`
time2=`date +%H`

# gk2a
/usr/bin/python3.6 /DATA/NAVY/source/weather_png.py 251 $today $time2 >> /DATA/NAVY/source/ColMain.log