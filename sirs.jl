# Load standard packages
using Revise
using Glob
using Plots
using FITSIO
using LaTeXStrings
using JLD
using StatsBase
using LinearAlgebra

# Load my packages
using SIRS

ddir = "Talbot_Darks";  # Data are here
rdir = "talbot_sirs_results"; # Results go here

files = glob("ch1_E00*.fits", ddir) # making a list of all the dark files

sc = SIRSCore("h4rg", 32, 7, 5.e-6, 101)

clear!(sc)
for file in files
    
    # Show some status
    println("Processing file: ", file)
   
    # Work with ADAPT format files.
    # Don't worry about DCL format for now. - fixed in next part
    f = FITS(file, "r")
    D = Float64.(dropdims(read(f[2]), dims=4))


    # rujula - crop off the reference output - dimensions should be (4096, 4096, 101)
    D = D[begin:4096, begin:end, begin:end]

    
    close(f)

    println(typeof(D))
    
    # Coadd
    coadd!(sc, D)

end

solve!(sc);

output_filename = rdir * "/talbot_sirs_result.jld"
SIRS.save(sc, output_filename)