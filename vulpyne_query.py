from functions import *
import pandas as pd
import sys

subset = parse_dict(to_print=False)
query = sys.argv[1:]

subsets = []
for q in query:
    ind_arr=subset['target'].str.contains(q)
    subsets.append(subset[ind_arr])

print(pd.concat(subsets)[['target','triviality']])
