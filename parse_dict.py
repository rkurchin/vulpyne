import json
import pandas as pd

# read in the big dictionary and beautify the Dataframe a bit
dct = json.load(open('dictionary_compact.json','r'))
dct = pd.DataFrame.from_dict(dct,orient='index')
dct.columns=['definition']
dct=dct.rename_axis('word')

# set up list of phrases to match and a regex query
match_strs = ['pertaining to','resembling','related to']
regex_str = '('
for phr in match_strs:
    regex_str = regex_str + phr + '|'
regex_str = regex_str[:-1]+')'

# query the dictionary and make a subset
ind_arr = dct['definition'].str.contains(regex_str,regex=True)
subset = dct[ind_arr]

# now to remove the "nontrivial" ones

print(subset.head())
