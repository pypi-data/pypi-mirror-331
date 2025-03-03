from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt

from medapy import ms_pandas
from medapy import MeasurementCollection, ContactPair, DefinitionsLoader, SweepDirection
from medapy.utils import misc
from medapy.analysis import electron_transport
# from medapy.mplenv.cmaps import cm_vaporwave

# Data directories initialization
path_data = Path(r'~\Desktop\ESA01_Exf16_5e\cleaned').expanduser()
path_prepared = path_data.parent / 'prepared'
path_output = path_data.parent / 'processed'
path_pics = path_data.parent / 'pictures'

# Create new dolders
path_prepared.mkdir(exist_ok=True)
path_output.mkdir(exist_ok=True)
path_pics.mkdir(exist_ok=True)

# Sample geometric configuration (in m)
length = 1e-6
width = 2.8e-6
t = 60e-9

# Default parameter definitions
parameters = DefinitionsLoader().get_all()

# Map units written not as in pint
unit_dict = dict(Ohms='ohm')

# For this experiment the magnitoresistance and Hall were measured seprately
# with different cuurent, frequency and aquisition time

# Rxx: I1-5(0.5uA), V6-7
pair_xx_polar = ContactPair(1, 5, 'I', 0.5e-6)
pair_xx_main = ContactPair(6, 7, 'V')

# Rxx: I1-5(1uA), V3-7
pair_xy_polar = ContactPair(1, 5, 'I', 1e-6)
pair_xy_main = ContactPair(3, 7, 'V')

xx_cont_str = f'{pair_xx_main.first_contact}-{pair_xx_main.second_contact}'
xy_cont_str = f'{pair_xy_main.first_contact}-{pair_xy_main.second_contact}'
xx_r_colname = 'Resistance Ch2'
xy_r_colname = 'Resistance Ch1'

# Read files to collection
collection = MeasurementCollection(path_data, parameters)

# Use only main measurement pair (3-7) and OOP orientation
files_oop = collection.filter(contacts=[pair_xx_main, pair_xy_main], position=0)

# Sort files by temperature value
files_oop = files_oop.sort('temperature')

# Defined parameters for preparation

field_lim = 13.98 # T
field_step = 0.02 # T
field_range = misc.symmetric_range(field_lim, field_step)
# dh step is bigger than Rxx distribution peak because of large steps for Rxy

window_width = 11
polyorder = 2

def savgol(x):
    return savgol_filter(x, window_length=window_width, polyorder=polyorder)
# Data at T=40 K is more noisy; use separate function
def savgol_40(x):
    return savgol_filter(x, window_length=31, polyorder=polyorder)


f = files_oop.filter(contacts=pair_xx_polar)[0]    
temp = f.state_of('temperature').value
fld = f.state_of('magnetic_field')

if temp == 40.0:
    file_xy = files_oop.filter(contacts=pair_xy_polar, temperature=temp)
else:
    file_xy = files_oop.filter(contacts=pair_xy_polar, temperature=temp,
                                sweep_direction=fld.sweep_direction)
assert len(file_xy) == 1

data_xx = pd.read_csv(f.path)
data_xx.ms.init_msheet(translations=unit_dict, patch_rename=True)
data_xx.etr.ensure_increasing(inplace=True)
data_xx.ms.add_labels({xx_r_colname: 'Rxx'})
data_xx.ms.rename(columns={xx_r_colname: f'Resistance_{xx_cont_str}'})
data_xx.ms['Field'] = data_xx.ms['Field'] / 10_000
data_xx.ms.set_unit('Field', 'T')

data_xy = pd.read_csv(file_xy[0].path)
data_xy.ms.init_msheet(translations=unit_dict, patch_rename=True)
data_xy.etr.ensure_increasing(inplace=True)
data_xy.ms.add_labels({xy_r_colname: 'Rxy'})
data_xy.ms.rename(columns={xy_r_colname: f'Resistance_{xy_cont_str}'})
data_xy.ms['Field'] = data_xy.ms['Field'] / 10_000
data_xy.ms.set_unit('Field', 'T')

if temp == 40.0:
    data_xx.etr.interpolate(field_range, smooth=savgol_40, inplace=True)
    data_xy.etr.interpolate(field_range, smooth=savgol_40, inplace=True)
else:
    data_xx.etr.interpolate(field_range, smooth=savgol, inplace=True)
    data_xy.etr.interpolate(field_range, smooth=savgol, inplace=True)

# print(data_xx.ms)
# print(data_xy.ms)
data = data_xx.ms.concat(data_xy)
print(data.ms)