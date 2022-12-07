import netCDF4
# from datetime import datetime
import pandas as pd
import numpy as np
import pyproj
import MakeFilePath
import ParsingData
import subprocess
import json

with open('/DATA/HResolutionVisual/test/OUTPUT/json/MOHID300M/all/20211129/0021/0/temp.json', 'r') as f:
    json_data = json.load(f)
# 1620x1620 = 2624400
print(len(json_data["array"][:]))