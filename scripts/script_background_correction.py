import numpy as np
from astropy.io import fits
import pandas as pd
import os

datadir = 'talbot_sirs_corrected2/'
files = os.listdir(datadir)

median_dark_file = 'talbot_darks_medians.fits'
median_dark = fits.getdata(median_dark_file) * -1

output_dir = 'talbot_background_corrected/'

for file in files:
    name = file[15:]
    img = fits.getdata(datadir+file)[1] * -1
    corrected = img - median_dark

    fits.writeto(output_dir + 'background_corrected_' + name, data=corrected)
    print('processed', name)
