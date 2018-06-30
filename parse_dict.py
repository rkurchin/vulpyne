import json
import pandas as pd
from copy import deepcopy
from fuzzywuzzy import fuzz
import numpy as np
from functions import *

def parse_dict(**argv):
    # read in the big dictionary and beautify the Dataframe a bit
    dct = json.load(open('./dictionary_compact.json','r'))
    dct = pd.DataFrame.from_dict(dct,orient='index')
    dct.columns = ['definition']
    dct = dct.rename_axis('word')

    # define some stuff
    match_strs = ['pertaining to', 'characteristic of']
    extra_strs = ['related to','resembling', 'like', 'designating', 'containing', 'derived from', 'discovered by', 'obtained from', 'according to', 'conveying', 'induced by', 'used by', 'observed at', 'involving', 'characterized by', 'denoting', 'containing', 'possessed by', 'produced by', 'employed in', 'suitable for', 'derived from', 'composed of', 'concerned in', 'named from', 'in the region of', 'formed by', 'received during', 'secreting', 'attending with', 'producing', 'issued by', 'covered with', 'in conformity with', 'illustrating', 'characteristic of', 'made at', 'connected with', 'formed in', 'produced from', 'in the style of', 'including', 'affected by', 'uttered in', 'exhibiting the phenomena of', 'having the characteristics of', 'consisting of', 'affecting', 'denoting', 'engaging in', 'containing', 'conforming to', 'adapted to', 'confined in', 'befitting']
    articles = ['a ', 'an ', 'the ']
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

    verbose = argv.setdefault('verbose',False)
    subset_length = argv.setdefault('subset_length',len(subset))
    subset = subset.iloc[:subset_length]
    to_print = argv.setdefault('to_print',True)
    to_print = argv['to_print']

    # now parse!
    target_list_1 = []
    target_list_2 = []
    target_list = []
    trivialities_1 = []
    trivialities_2 = []
    trivialities = []
    nontrivial = []
    for entry in subset.iterrows():
        word = entry[0]
        defn = entry[1]['definition']
        if(verbose):
            print('****************************')
            print(word,defn)
            print('-----')

        # find last instance of one of match_strs in def
        start_ind_1 = skip_to_ind(defn,match_strs,verbose,last=False)
        subset_1 = defn[start_ind_1:]
        report_out('Clipped from last instance of one of %s'%match_strs,defn,verbose)

        target_1 = clean_entry(subset_1,extra_strs,articles,punc_list,punc_no_commas,verbose)
        target_list_1.append(target_1)

        # compare that content to word
        triviality_1 = max([fuzz.ratio(word,target_1),fuzz.partial_ratio(word,target_1),fuzz.partial_ratio(target_1,word)])
        trivialities_1.append(triviality_1)

        start_ind_2 = skip_to_ind(defn[start_ind_1:],match_strs,verbose,last=False)

        if start_ind_2 == 0:
            target_2 = ''
            triviality_2 = 100
        else:
            subset_2 = defn[start_ind_2+start_ind_1:]
            report_out('$$$$$$analyzing the second target!',subset_2,verbose)
            target_2 = clean_entry(subset_2,extra_strs,articles,punc_list,punc_no_commas,verbose)
            # compare that content to word
            triviality_2 = max([fuzz.ratio(word,target_2),fuzz.partial_ratio(word,target_2),fuzz.partial_ratio(target_2,word)])

        target_list_2.append(target_2)
        trivialities_2.append(triviality_2)

        if triviality_2 > triviality_1:
            triviality = triviality_1
            target = target_1
        else:
            triviality = triviality_2
            target = target_2

        target_list.append(target)
        trivialities.append(triviality)
        if triviality < 57:
            nontrivial.append(True)
        else:
            nontrivial.append(False)

    subset['target 1'] = target_list_1
    subset['target 2'] = target_list_2
    subset['target'] = target_list
    subset['triviality_1'] = trivialities_1
    subset['triviality_2'] = trivialities_2
    subset['triviality'] = trivialities
    subset['nontrivial'] = nontrivial

    ind_arr = subset['nontrivial']==True
    nontrivial_list = subset[ind_arr]
    if to_print:
        print(nontrivial_list[['target','triviality']].tail(60))
        subset[['target 1','target 2','target','triviality_1','triviality_2','triviality']].to_csv('vulpyne.csv')
        print('%d total entries found, of which %d are nontrivial.'%(len(subset),len(nontrivial_list)))
    nontrivial_list[['target 1','target 2','target','triviality_1','triviality_2','triviality']].to_csv('vulpyne_nontrivial.csv')

    return subset
