from functions import *
from parse_dict import *
import sys

if len(sys.argv)>1:
    num = int(sys.argv[1])
    if len(sys.argv)>2:
        nontrivial = bool(sys.argv[2])
    else:
        nontrivial = True
else:
    num = 1

dct = parse_dict(to_print=False,verbose=False)

if nontrivial:
    ind_arr = dct['nontrivial']==True
    dct = dct[ind_arr]

print(dct.sample(num)[['target','triviality']])
