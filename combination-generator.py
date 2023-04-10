#--------------------------------------------------------------------------
# Overview: This script is used to generate the combinations for sensitivity and verification based analyses
# Last updated on: 12/17/2022
#--------------------------------------------------------------------------

import pickle
import itertools

# # full set of combinations
# intensity = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# comb = [intensity]*4
# combination = [p for p in itertools.product(*comb)]


# for i in range(len(combination)):
#     combination[i] = list(combination[i])

# print(combination)
# with open('./data/combinations.pkl', 'wb') as f: 
#     pickle.dump(combination, f)


# subset of combinations
intensity = [4, 5, 6, 7, 8, 9, 10]

comb = [intensity]*4
combination = [p for p in itertools.product(*comb)]


for i in range(len(combination)):
    combination[i] = list(combination[i])

print(combination)
with open('./data/combinations_subset.pkl', 'wb') as f: 
    pickle.dump(combination, f)



