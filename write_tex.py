from parse_dict import *
import pandas as pd

dct = parse_dict(to_print=False,verbose=False)
flag_list = [f[6:-4] for f in glob('flags/*.txt')]

with open('vulpyne.tex','w') as f:
    for entry in dct.iterrows():
        word = entry[0]
        target = entry[1]['target']
        flags_here = []
        for fl in flag_list:
            if target[fl]==True:
                flags_here = fl
        if flags_here == []:
            st = 'Something with the noun (%s) and the adjective (%s) that you will cook up!'%(target,word)
        elif len(flags_here)==1:
            st = 'Something with the noun (%s) and the adjective (%s) that you will cook up, which also mentions that this word is flagged with %s!'%(target,word,flags_here[0])
        else:
            print('We need a way to handle multiple flags now!')
        f.write(st)

