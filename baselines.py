"""
@author: alfonso.semeraro@unito.it

Baselines are in the format [emo_combinations, weights] where

emo_combinations = [['joy'], ['joy', 'trust'], ['joy', 'trust', 'fear'] ...]
weights = [123521, 1242, 212, ...]

"""

import textloader as _load_object
from collections import Counter
import pickle

def _make_baseline(baseline = None, tagger = None, language = 'english', 
                   emojis_dict = {}, idiomatic_tokens = {},
                   emotion_lexicon = None,):
           
    if baseline:
        # extract all words from the input baseline
        wordlist = _load_object(baseline = baseline, 
                               language = language,
                               tagger = tagger,
                               emojis_dict = emojis_dict, 
                               convert_emojis = convert_emojis,
                               idiomatic_tokens = idiomatic_tokens)
        
        
                           
        
        # check into the lexicon the emotions associated
        emotions = [emotion_lexicon[w] for w in wordlist]
        
        if not emotions:
            raise ValueError("Baseline has no emotions. Fallback to the default baseline.")
    else:
        # use the emotion lexicon as baseline
        emotions = list(emotion_lexicon.values())
    
    
    # count
    baseline_distr = dict(Counter(map(tuple, emotions)))
    # two lists: items and weights
    baseline_distr = [[list(k) for k in baseline_distr.keys()], list(baseline_distr.values())]
    
    
    return baseline_distr
        
    
def _load_lookup_table(language = 'english'):
    
    try:
        with open('baseline_tables/{}_baseline.dict'.format(language), 'rb') as rb:
            lookup = pickle.load(rb)
    except:
        lookup = {}
        
    return lookup

