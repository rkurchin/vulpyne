import json
import pandas as pd
from copy import deepcopy
from fuzzywuzzy import fuzz
import sys
import numpy as np
from functions import *

# read in the big dictionary and beautify the Dataframe a bit
dct = json.load(open('./dictionary_compact.json','r'))
dct = pd.DataFrame.from_dict(dct,orient='index')
dct.columns=['definition']
dct=dct.rename_axis('word')

# define some stuff
match_strs = ['pertaining to','related to']
extra_strs = ['resembling', 'like', 'designating', 'containing', 'derived from']
punc_list = [',',' (',',',';','.',';',',']
punc_no_commas = [' (',';','.',';']

# set up a regex query
regex_str = '('
for phr in match_strs:
    regex_str = regex_str + phr + '|'
regex_str = regex_str[:-1]+')'

# query the dictionary and make a subset
ind_arr = dct['definition'].str.contains(regex_str,regex=True)
subset = deepcopy(dct[ind_arr])

# verbosity, subset
if len(sys.argv)>1:
    verbose = bool(sys.argv[1])
    subset_length = int(sys.argv[2])
else:
    verbose = False
    subset_length = len(subset)
print(verbose)
subset = subset.iloc[:subset_length]

# now parse!
target_list_1 = []
target_list_2 = []
trivialities = []
for entry in subset.iterrows():
    word = entry[0]
    defn = entry[1]['definition']
    if(verbose):
        print('*****************')
        print(word,defn)
        print('-----')

    # find last instance of one of match_strs in def
    start_ind = skip_to_ind(defn,match_strs,verbose,last=True)
    defn = defn[start_ind:]
    report_out('Clipped from last instance of one of %s'%match_strs,defn,verbose)

    # get content of definition from last instance to next "firm" punctuation
    punc_index = len(defn)
    for punc in punc_no_commas:
        ind = defn.find(punc)
        if ind >= 1 and ind<punc_index: punc_index = ind
    defn = defn[:punc_index]
    report_out('Clipped to first instance of one of %s'%punc_no_commas,defn,verbose)

    # check for any of extra_strs to skip past
    new_start_ind = skip_to_ind(defn,extra_strs,verbose,last=False)
    if new_start_ind >= 0:
        defn = defn[new_start_ind:]
    report_out('Clipped from first instance of one of %s'%extra_strs,defn,verbose)

    # clear out leading or trailing punctuation or spaces
    defn = strip_punc(defn,punc_list)
    report_out('Stripping leading/trailing punctuation',defn,verbose)

    # get content of definition from last instance to next "firm" punctuation
    punc_index = len(defn)
    for punc in punc_list:
        ind = defn.find(punc)
        if ind >= 1 and ind<punc_index: punc_index = ind
    defn = defn[:punc_index]
    report_out('Clipped to first instance of one of %s'%punc_list,defn,verbose)

    # clear out leading or trailing punctuation or spaces
    defn = strip_punc(defn,punc_list)
    report_out('Stripping leading/trailing punctuation again',defn,verbose)

    target_list_1.append(defn)

    # compare that content to word
    triviality = fuzz.ratio(word,defn)
    trivialities.append(triviality)

#print(len(content_list),len(trivialities))

subset['target 1'] = target_list_1
subset['triviality'] = trivialities
print(subset[['target','triviality']].head(100))
