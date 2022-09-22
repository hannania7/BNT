#!/bin/bash

echo `date` >> /DATA/NAVY/source/ColMain.log
/usr/bin/python3.6 /DATA/NAVY/source/ColMain.py >> /DATA/NAVY/source/ColMain.log
