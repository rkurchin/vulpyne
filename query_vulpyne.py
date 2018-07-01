from parse_dict import parse_dict
import sys

subset = parse_dict(to_print=False)
query = sys.argv[1]

ind_arr=subset['target'].str.contains(query)
print(subset[ind_arr][['target','triviality']])
