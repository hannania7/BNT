#!/bin/bash

no=$1
date=$2
time2=$3

/usr/bin/python3.6 /DATA/NAVY/source/weather_png.py $no $date $time2 >> /DATA/NAVY/source/ColMain.log

# /usr/bin/python3.6 /DATA/NAVY/source/weather_png_v2.py 250 20221129 09