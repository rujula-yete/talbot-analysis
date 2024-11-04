import numpy as np
from astropy.io import fits
import pandas as pd
import matplotlib.pyplot as plt
import os

datadir = 'talbot_darks_sirs_corrected/'
files_list = os.listdir(datadir)

data = fits.getdata(datadir+files_list[0])[1]

darks_list = []
for index in range(len(files_list)):
    data = fits.getdata(datadir+files_list[index])[1]
    darks_list.append(data)

darks_array = np.dstack(darks_list)
medians_array = np.median(darks_array, axis=2)
fits.writeto('talbot_darks_medians.fits', data=medians_array)