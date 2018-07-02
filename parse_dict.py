from functions import *
import sys

if len(sys.argv)>1:
    verbose = bool(sys.argv[1])
else:
    verbose = False

if len(sys.argv)>2:
    start_ind = sys.argv[2]
else:
    start_ind = 0

if len(sys.argv)>3:
    end_ind = sys.argv[3]
else:
    end_ind = start_ind + 10

dct = parse_dict(verbose=verbose,index_bounds=[start_ind,end_ind],to_print=True)
