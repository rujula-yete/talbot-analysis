import numpy as np
import pandas as pd
from scipy.spatial import KDTree
import os
import glob

datadir = 'talbot_starfinder_full_results/'
files = os.listdir(datadir)

# my pair finding function

def match(set1, set2, distance_bound=np.inf):
    kdtree = KDTree(set2)
    distances, indices = kdtree.query(set1, k=1, distance_upper_bound = distance_bound)
    
    # trying to filter out repeats

    # initializing an array for keeping track of which spots2 indices are used
    used = np.array([])

    # initializing an array with the dimensions we want
    pairs = np.array([[-1,-1,-1]])

    for set1_index, set2_index in enumerate(indices): # iterating through the paired indices
        if set2_index not in used:
            if distances[set1_index] == np.inf:
                continue
            pairs = np.append(pairs, np.array([[set1_index, set2_index, distances[set1_index]]]), axis=0)
            used = np.append(used, set2_index)
            # need to turn dataframes into arrays to add actual x, y, flux values
        else:
            current_distance = distances[set1_index]
            # finding previously listed distance
            match = np.where(pairs[:,1]==set2_index)[0][0] # finding where the existing 2nd element matches the current 2nd index
            existing_distance = pairs[match][2] # extracting the corresponding distance
        
            if current_distance < existing_distance:
                pairs[match] = np.array([set1_index, set2_index, distances[set1_index]])
                
    pairs = np.delete(pairs, 0, axis=0)
    
    return pairs

#files.remove('.ipynb_checkpoints')

# renaming so the numbers stay in order

three_digit_exps = glob.glob('talbot_starfinder_full_results/aperture_ch1_E???.csv')

for file in three_digit_exps:
    parts = file.split('E')
    os.rename(file, parts[0]+'E0'+parts[1])

files_array = np.array(files).reshape((70,70))

# defining the first exposure for later
first_exp = pd.read_csv(datadir+files_array[0,0]).to_numpy() # making it a 2d numpy array
first_exp_positions = first_exp[:,2:4] # corresponding to the x and y centroid columns

# (1)
prev_exp = first_exp
# (2)
prev_exp_positions = first_exp_positions

# (3)
for column_index in range(70):
        
    for row_index in range(70):
        new_exp = pd.read_csv(datadir+files_array[column_index, row_index]).to_numpy()
        # (4)
        new_exp_positions = new_exp[:,2:4]

        # (5)
        bounded_position_match = match(prev_exp_positions, new_exp_positions, distance_bound=3)

        # (6)
        prev_indices = bounded_position_match[:,0].astype(int) # isolating the indices corresponding to pairs
        new_indices = bounded_position_match[:,1].astype(int)

        prev_exp_ordered = prev_exp[prev_indices,:] # ordering and filtering at the same time
        new_exp_ordered = new_exp[new_indices,:]

        # (7)
        combined = np.dstack([prev_exp_ordered, new_exp_ordered])

        # (8)
        prev_exp = combined
        # (9)
        prev_exp_positions = prev_exp[:,2:4,-1] # extracting positions from the most recent exposure

        print(files_array[column_index, row_index], prev_exp.shape)

    # resetting previous exposure positions to 1st in the sequence of 70

    # (10)
    prev_exp_positions = prev_exp[:,2:4,70*column_index+1] # (-1 for the index number, +1 bc first exp got repeated)

# (11)
np.save('starfinder_datacube.npy', prev_exp)