import numpy as np
from astropy.io import fits
import pandas as pd
import os
from astropy.stats import sigma_clipped_stats
import glob
import photutils

from photutils.aperture import aperture_photometry
from photutils.aperture import CircularAperture, CircularAnnulus
from photutils.detection import DAOStarFinder
from photutils.aperture import ApertureStats
import scipy
from astropy.io import ascii

datadir = 'talbot_background_corrected'

files = os.listdir(datadir)

Aperture_Photometry_Radius = 2 * np.sqrt(2) # radius containing spot, based on max radius needed for 9 pixel box if center is edge of pixel
Annulus_R_in = 3 # inner radius for local background
Annulus_R_out = 3.75 # outer radius for local background
FWHM = 1.3
R_mask = 500

for file in files:
    fname = datadir + '/' + file
    
    img = fits.getdata(fname)
    
    # defining dimensions
    xc = img.shape[0]//2
    yc = img.shape[1]//2
    xindx = np.arange(img.shape[0])-xc
    yindx = np.arange(img.shape[1])-yc
    xindx,yindx = np.meshgrid(xindx,yindx)

    image_mask = np.sqrt(xindx**2+yindx**2) > R_mask
    
    mean_val, median_val, std_val = sigma_clipped_stats(img, mask=image_mask)

    daofind = DAOStarFinder(fwhm=FWHM, threshold=10.*std_val)
    sources = daofind(img, mask=image_mask)
    for col in sources.colnames:  
        sources[col].info.format = '%.2g'  # for consistent table output

    positions = np.transpose((sources['xcentroid'], sources['ycentroid']))
    aperture = CircularAperture(positions, r=Aperture_Photometry_Radius)
    annulus_aperture = CircularAnnulus(positions, r_in=Annulus_R_in, r_out=Annulus_R_out)
    annulus_masks = annulus_aperture.to_mask(method='center')
    
    phot_table = aperture_photometry(img, aperture)
    
    aperstats = ApertureStats(img, annulus_aperture)
    bkg_mean = aperstats.mean
    
    area = aperture.area_overlap(img)
    
    total_bkg = bkg_mean * area

    df = pd.DataFrame(np.transpose(sources))
    df['aperture_sum'] = phot_table['aperture_sum']
    
    subtracted = phot_table['aperture_sum'] - total_bkg
    df['local_background'] = total_bkg
    df['bkg_subtracted_sum'] = subtracted
    
    label = file[21:-5]

    df.to_csv('talbot_starfinder_full_results/aperture_'+label+'.csv')
    print(label, 'processed')
