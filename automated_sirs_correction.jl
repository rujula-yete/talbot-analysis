using SIRS
using FITSIO
using Plots
using JLD
using Revise

# Stage the data to Prism's fast storage
#prism_fast = "/gpfsm/ccds01/nobackup/temp/brausche/"

# SIRS correct this file
#file = prism_fast * "20190914_95k_1p1m0p1_noise_20663_005.fits"


# rujula - automating this with a for loop

data_directory = "/explore/nobackup/projects/romanst/H4RG/Talbot/20240606072156_LargeScan_480nm_23dB/"
files_list = readdir(data_directory)

for file in files_list

    # Get just the data
    f = FITS(data_directory*file, "r")
    D = -Float64.(dropdims(read(f[2]), dims=4)) # Integrate up
    # rujula - crop off the reference output - dimensions should be (4096, 4096, 3)
    D = D[begin:4096, begin:end, begin:end]
    close(f)

    # Get saved SIRSCore for this detector, operating temperature, and bias voltage
    # rujula - changing file name
    #sirs = restore(prism_fast * "2021-05-26T17:58:56_20663_95.0K_1.0V_SIRS.jld");
    sirs = restore("talbot_sirs_results/talbot_sirs_result.jld")

    # SIRS correct the file. This is done in place.
    # Use f_max to zero out high frequencies. This 
    # value generally works OK with Roman Space Telescope
    # IR arrays tested in the DCL
    sirssub!(sirs, D, f_max=740.)

    # Fit 2-parameter straight line.Λta have 60 samples
    # up-the-ramp.
    # rujula - change 60 to 3 since datafiles have 3 samples
    Λ = LegendreMatrices((3,2));

    # Fit it
    myfit = legfit(Λ, D);

    # Save for examination using ds9
    # rujula - rename file
    f = FITS("talbot_sirs_corrected2/sirs_corrected_"*file, "w")
    write(f, myfit)
    close(f)
    println("processed "*file)
end

