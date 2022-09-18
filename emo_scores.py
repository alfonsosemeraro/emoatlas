"""
@author: alfonso.semeraro@unito.it

"""

import numpy as np
import itertools
import textloader as _txl 
from random import choices
   


def _get_emotions(obj, 
                   emotion_lexicon, 
                   language,
                   normalization_strategy, 
                   tagger,
                   emotions,
                   return_words,
                   emojis_dict,
                   convert_emojis,
                   idiomatic_tokens):
    
        
    wordlist = _txl._load_object(obj = obj,
                           language = language,
                           tagger = tagger,
                           emojis_dict = emojis_dict, 
                           convert_emojis = convert_emojis,
                           idiomatic_tokens = idiomatic_tokens)
        
    # word-emotion pairs
    emowords = [[(w, emo) for emo in emotion_lexicon[w]] for w in wordlist if w in emotion_lexicon]
    emowords = list(itertools.chain(*emowords))
    
    # emotion: count, list of words
    emowords = {emo: list(set([word for word, emotion in emowords if emo == emotion])) for emo in emotions}
    emowords = {emo: {'count': len(emo_words), 'words': emo_words} for emo, emo_words in emowords.items()}
    
    if return_words:
        
        if language != 'english':
            reverse_id_tok = {val: key for key, val in idiomatic_tokens.items()}
            for emo in emowords:
                emowords[emo]['words'] = [reverse_id_tok[w] if w in reverse_id_tok else w for w in emowords[emo]['words']]
        return emowords
    
    else:
        emowords = {emo: emowords[emo]['count'] for emo in emowords}
        
        if normalization_strategy == 'text_length':
            N = len(wordlist)
            emowords = {key: val/N if N else 0 for key, val in emowords.items()}
            
        elif normalization_strategy == 'emotion_words':
            N = sum(emowords.values())
            emowords = {key: val/N if N else 0 for key, val in emowords.items()}
    
    return emowords






def _zscores(obj,
             baseline,
             n_samples,
             emotion_lexicon,
             language,
             tagger,
             emotions,
             lookup,
             emojis_dict,
             convert_emojis,
             idiomatic_tokens):
    
    emotion_words = _get_emotions(obj = obj, emotion_lexicon = emotion_lexicon, language = language, 
                                   normalization_strategy = 'none', tagger = tagger, emotions = emotions,
                                   return_words = True, emojis_dict = emojis_dict, convert_emojis = convert_emojis,
                                   idiomatic_tokens = idiomatic_tokens)
    
    # # text_emo: 'joy': 'L'
    # S = sum([emotion_words[emo]['count'] for emo in emotions])
    # text_emo = {emo: emotion_words[emo]['count']/S if S != 0 else 0 for emo in emotions}
    
    
    # N words to sample
    N = len(set(itertools.chain(*[emotion_words[emo]['words'] for emo in emotions])))
    
    
    # No 1 word sentences
    if N == 1:
        return {emo: 2 if emotion_words[emo]['count'] > 0 else 0 for emo in emotion_words}
    
    # Few emotion words? only count emotions that appear twice
    elif N <= 5:
        return {emo: 2 if emotion_words[emo]['count'] > 1 else 0 for emo in emotion_words}
    
    
    # N is in the lookup table
    if N in lookup:
        zscores = {emo: (emotion_words[emo].get('count', 0) - lookup[N][emo]['mean']) / lookup[N][emo]['std'] if lookup[N][emo]['std'] else 0 for emo in emotions}
        return zscores
    
    
    # otherwise I'll compute it and add it to lookup
    
    # all samples together
    all_samples = {emo: [] for emo in emotions}
    
    for _ in range(n_samples):
        
        # random choice N with prob
        sample = choices(baseline[0], weights = baseline[1], k = N)
        sample = list(itertools.chain(*sample))
        
        # count emotions
        sample = {emo: sample.count(emo) for emo in emotions}
                
        # add to all_samples
        all_samples = {emo: all_samples[emo] + [sample.get(emo, 0)] for emo in emotions}
        
    # All samples: 'joy': 'mean': ... 'std': ...
    # Add all samples to lookup[N]
    all_samples = {emo: {'mean': np.mean(all_samples[emo]), 'std': np.std(all_samples[emo])} for emo in emotions}
    lookup[N] = all_samples
    
    # Get z-scores
    zscores = {emo: (emotion_words[emo].get('count', 0) - all_samples[emo]['mean']) / all_samples[emo]['std'] if all_samples[emo]['std'] else 0 for emo in emotions}

    
    return zscores

 
    