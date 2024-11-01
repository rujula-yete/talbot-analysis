# talbot-analysis File Organization

#### General Process Outline:
1. __Reference Correction__ - reference correction using the Simple Improved Reference Subtraction (SIRS) algorithm
2. __Background Correction__ - subtracting darks from data files
3. __Spot Detection__ - using source extractor to detect spots and measure their properties
4. __Matching__ - using nearest neighbors to match spots across exposures
5. __Analysis__ - plotting results

These steps were done on the `/explore/nobackup/projects/romanst/H4RG/Talbot/20240606072156_LargeScan_480nm_23dB/` dataset, which contains 4900 exposures of spots with the 480nm laser.

### Reference Correction

I ran the SIRS code entirely in Julia scripts which can be run directly from the terminal. SIRS uses dark exposures to find the optimal parameters for reference correction, then applies them to the data files of choice. In addition to installing Julia and the libraries in the script, the github package for SIRS must also be downloaded and installed on Adapt/Prism in order to use this code. I used the original code from github, but made the following modifications:

- changed file paths
- adapted for DCL format data by cropping off the extra reference output in each file (4096 x 4224 --> 4096 x 4096)
- changed values specific to the number of up-the-ramp samples
- automated the process to run on all files in a directory

The dark exposures were taken from this directory: `/explore/nobackup/projects/romanst/H4RG/Talbot/20240605053628_PreDarks/`

The files to be run are:
1. `sirs.jl`
2. `automated_sirs_correction.jl`
3. `automated_sirs_darks_correction.jl`

#### sirs.jl

This script calculates weights from a set of darks. Line 14 is the directory with the darks, Line 15 is the output directory, Line 17 is the list of files, and Line 48 is the output file name (there is only 1 resulting file). The last argument in Line 19 should the the number of up-the-ramp samples in the dark exposures (in this case, 101), and Line 34 is where I adjust for the DCL data format. This can take a while to run (about half an hour). My resulting weights file is `talbot_sirs_results/talbot_sirs_result.jld`

#### automated_sirs_correction.jl

This script uses the weights calculated in the previous file to correct the spot files. Line 16 is the directory with the files with spots, Line 31 is the weights file, and Line 49 has the output directory and file names. The first argument in Line 42 is the number of up-the-ramp samples in the spot exposures (in this case, 3), and Line 25 is where I adjust for the DCL data format. This can take several hours to run. The resulting 4900 corrected files are in `talbot_sirs_corrected2/`

#### automated_sirs_darks_correction.jl

This script does the same thing as the one above, but corrects the dark files. It uses the same weights file, and the resulting 5 corrected files are in `talbot_darks_sirs_corrected/`

One thing to note is that SIRS corrections results in no brightness having a flux of 0 while brighter pixels have negative flux (more brightness = more negative). In the next steps, I multiplied the resulting data by -1 to put the brightness on a positive scale.

### Background Correction

First, I found the median value of each pixel from all 5 corrected dark files. This code is in `darks_median.ipynb`, with the result as `talbot_darks_medians.fits`

Then, I subtracted the median dark image from each of the reference corrected spot images. This code is in `automated_background_correction.ipynb`, with the resulting 4900 files in `talbot_background_corrected/`

### Spot Detection

`automated_aperture.ipynb` - the full automated process for spot detection with DAO Starfinder. Most of this code is adapted from Neil's original code. The resulting 4900 csv files are in `talbot_starfinder_full_results/`, with individual demonstrations/explanations of the code in `aperture.ipynb`.

### Matching

I used the KDTree nearest neighbors algorithm from scipy to conduct pairwise matching of spots across exposures. `automated_starfinder_full_matching.ipynb` - the full automated matching of the tables from DAO Starfinder, follows the same process as the previous matching code. The resulting final array is `starfinder_datacube.npy`.
