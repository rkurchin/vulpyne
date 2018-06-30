from parse_dict import *
import pandas as pd

dct = parse_dict(to_print=False,verbose=False)

with open('vulpyne.tex','w') as f:
    for entry in dct.iterrows():
        word = entry[0]
        target = entry[1]['target']
        f.write('Something with the noun (%s) and the adjective (%s) that you will cook up!'%(target,word))
