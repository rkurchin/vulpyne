import json
import pandas as pd
from copy import deepcopy
from fuzzywuzzy import fuzz

# read in the big dictionary and beautify the Dataframe a bit
dct = json.load(open('./dictionary_compact.json','r'))
dct = pd.DataFrame.from_dict(dct,orient='index')
dct.columns=['definition']
dct=dct.rename_axis('word')

# set up list of phrases to match and a regex query
match_strs = ['pertaining to','related to']
regex_str = '('
for phr in match_strs:
    regex_str = regex_str + phr + '|'
regex_str = regex_str[:-1]+')'

# query the dictionary and make a subset
ind_arr = dct['definition'].str.contains(regex_str,regex=True)
subset = deepcopy(dct[ind_arr])

# remove "trivial" entries
content_list = []
trivialities = []
for entry in subset.iterrows():
    word = entry[0]
    defn = entry[1]['definition']

    # find last instance of one of match_strs in def
    substr_indices = {substr:-1 for substr in match_strs}
    for substr in match_strs:
        substr_indices[substr] = defn.find(substr)
        if substr_indices[substr]>=0:
            substr_indices[substr] = substr_indices[substr] + len(substr) + 1
    start_ind = max(substr_indices.values())

    # get content of definition from last instance to next period
    defn = defn[start_ind:]
    punc_index = len(defn)
    for punc in [',',' (',',',';','.',';',',']:
        ind = defn.find(punc)
        if ind >= 0 and ind<punc_index: punc_index = ind
    content = defn[:punc_index]
    content_list.append(content)

    # compare that content to word
    triviality = fuzz.ratio(word,content)
    trivialities.append(triviality)

subset['target'] = content_list
subset['triviality'] = trivialities
print(subset[['target','triviality']].head(20))
