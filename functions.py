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
