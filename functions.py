from copy import deepcopy
import json
import pandas as pd
from copy import deepcopy
from fuzzywuzzy import fuzz
import numpy as np
from glob import glob

def skip_extra_strs(d,extra_strs,verbose):
    defn = d
    k = 0
    while k < len(extra_strs):
        i = skip_to_ind(defn,['or '],verbose)
        if i <= 4:
            if verbose:
                print('found an or ending at index %d'%i)
            defn = defn[i:]
        j = skip_to_ind(defn,[extra_strs[k]],verbose)
        if j == len(extra_strs[k]):
            if verbose:
                print('found %s'%extra_strs[k])
            defn = defn[j:]
            defn = defn.strip(' ')
            k = 0
        else:
            k = k+1
    return len(d)-len(defn)

def skip_to_ind(defn,substr_list,verbose,last=False):
    substr_indices = {}
    for substr in substr_list:
        ind = defn.find(substr)
        if ind>=0:
            substr_indices[substr] = ind + len(substr)
    if len(substr_indices.values())==0:
        return 0
    if last:
        start_ind = max(substr_indices.values())
    else:
        start_ind = min(substr_indices.values())
    if verbose:
        print(substr_indices,start_ind)
    return start_ind

def strip_punc(defn,punc_list):
    st = defn
    for ch in punc_list + [' ']:
        st = st.strip(ch)
    return st

def report_out(desc, defn, verbose):
    if verbose:
        print(desc)
        print(defn)
        print('----')

def clean_entry(st, extra_strs, articles, punc_list, punc_no_commas, verbose):
    # get content of definition from last instance to next "firm" punctuation
    defn = st
    punc_index = len(defn)
    for punc in punc_no_commas:
        ind = defn.find(punc)
        if ind >= 1 and ind<punc_index: punc_index = ind
    defn = defn[:punc_index]
    report_out('Clipped to first instance of one of %s'%punc_no_commas,defn,verbose)

    # clear out leading or trailing punctuation or spaces
    defn = strip_punc(defn,punc_list)
    report_out('Stripping leading/trailing punctuation',defn,verbose)

    # check for any of extra_strs to skip past
    # should add an option to only search for extra_strs at the beginning (with an "or" maybe)
    #new_start_ind = skip_to_ind(defn,extra_strs,verbose,last=False)
    new_start_ind = skip_extra_strs(defn,extra_strs,verbose)
    if new_start_ind >= 0:
        defn = defn[new_start_ind:]
    report_out('Clipped leading consecutive instances of any of extra_strs.txt',defn,verbose)
    #report_out('Clipped from first instance of one of %s'%extra_strs,defn,verbose)

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

    # remove leading articles
    for art in articles:
        l = len(art)
        if defn[:l] == art:
            defn = defn[l:]
    report_out('Stripping leading articles',defn,verbose)

    return defn

def parse_dict(**argv):
    # read in the big dictionary and beautify the Dataframe a bit
    dct = json.load(open('./data/dictionary_compact.json','r'))
    dct = pd.DataFrame.from_dict(dct,orient='index')
    dct.columns = ['definition']
    dct = dct.rename_axis('word')

    # define some stuff
    match_strs = ['pertaining to', 'characteristic of']
    extra_strs = [l[:-1] for l in open('extra_strs.txt','r').readlines()]
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
    if 'subset_length' in argv.keys():
        subset = subset.iloc[:argv['subset_length']]
    elif 'index_bounds' in argv.keys():
        ib = argv['index_bounds']
        subset = subset.iloc[int(ib[0]):int(ib[1])]

    to_print = argv.setdefault('to_print',True)
    to_print = argv['to_print']

    # prep lists for flags
    flag_words = {}
    flags = {}
    flag_list = [f for f in glob('flags/*.txt')]
    for flag_file in flag_list:
        flags[flag_file[6:-4]] = [False] * len(subset)
        flag_words[flag_file[6:-4]] = [w.split('\n')[0] for w in open(flag_file,'r').readlines()]

    # now parse!
    target_list_1 = []
    target_list_2 = []
    target_list = []
    trivialities_1 = []
    trivialities_2 = []
    trivialities = []
    nontrivial = []

    count = 0
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
        
        for flag,words in flag_words.items():
            if word in words:
                flags[flag][count] = True

        count = count+1

    subset['target 1'] = target_list_1
    subset['target 2'] = target_list_2
    subset['target'] = target_list
    subset['triviality_1'] = trivialities_1
    subset['triviality_2'] = trivialities_2
    subset['triviality'] = trivialities
    subset['nontrivial'] = nontrivial

    for flag,list in flags.items():
        subset[flag] = list

    ind_arr = subset['nontrivial']==True
    nontrivial_list = subset[ind_arr]

    subset=subset.sort_values(by='target')

    if to_print:
        print(nontrivial_list[['target','triviality']+flags.keys()].tail(60))
        print('%d total entries found, of which %d are nontrivial.'%(len(subset),len(nontrivial_list)))

    subset.to_csv('./data/vulpyne.csv')
    nontrivial_list.to_csv('./data/vulpyne_nontrivial.csv')

    return subset
