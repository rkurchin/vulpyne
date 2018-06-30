def skip_to_ind(defn,substr_list,verbose,last=True):
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

    # remove leading articles
    for art in articles:
        l = len(art)
        if defn[:l] == art:
            defn = defn[l:]

    return defn
