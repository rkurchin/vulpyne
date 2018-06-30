import json
import pandas as pd

dct = json.load(open('dictionary_compact.json','r'))
dct = pd.DataFrame.from_dict(dct,orient='index')
