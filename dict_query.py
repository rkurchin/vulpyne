from functions import *
import sys

subset = parse_dict(to_print=False)
query = sys.argv[1]

print(subset.loc[query]['definition'])
