#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  3 12:29:39 2021

@author: alfonso
"""
from resources import _load_dictionary
import numpy as np
import random
import itertools
import warnings
import pandas as pd    

def _emotion_distribution(wordlist, emotion_lexicon = None, normalize_strategy = 'none', emotions = [], language = 'english'):
    """
    Count emotions in given wordlist.

    Required arguments:
    ----------
    *wordlist*:
        A list of words. 
        
    *emotion_lexicon*:
        A lexicon with every word-emotion association. By default, the NRCLexicon will be loaded.
        
    *normalize_strategy*:
        A string, whether to normalize emotion scores over the number of words. Accepted values are:
            'none': no normalization at all
            'text_lenght': normalize emotion counts over the total text length
            'emotion_words': normalize emotion counts over the number of words associated to an emotion
            
    *emotions*:
        A list of emotions, depending on the model required. Default is Pluthick's wheel of emotions model.
        
    *language*:
        Language of the text. Full support is offered for the languages supported by Spacy: 
            Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
            Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
        Limited support for other languages is available.
        
    Returns:
    ----------
    *emo_distr*:
        A list of lists. Each entry is a list of emotions associated to a word in wordlist.
    """
    
    if not emotion_lexicon:
        emotion_lexicon = _load_dictionary(language)
        emotion_lexicon = emotion_lexicon.groupby('word')['emotion'].apply(list).to_dict()
        
    if not emotions:
        emotions = ['anger', 'trust', 'surprise', 'disgust', 'joy', 'sadness', 'fear', 'anticipation']
        
        
    emo_distr = [emotion_lexicon[word] for word in wordlist if word in emotion_lexicon.keys()]
    
    return emo_distr
    
def _emotion_words(wordlist, emotion_lexicon = None, normalize_strategy = 'none', emotions = [], language = 'english'):
    """
    Count emotions in given wordlist. Returns the words most associated to emotions.

    Required arguments:
    ----------
    *wordlist*:
        A list of words. 
        
    *emotion_lexicon*:
        A lexicon with every word-emotion association. By default, the NRCLexicon will be loaded.
        
    *normalize_strategy*:
        A string, whether to normalize emotion scores over the number of words. Accepted values are:
            'none': no normalization at all
            'text_lenght': normalize emotion counts over the total text length
            'emotion_words': normalize emotion counts over the number of words associated to an emotion
            
    *emotions*:
        A list of emotions, depending on the model required. Default is Pluthick's wheel of emotions model.
        
    *language*:
        Language of the text. Full support is offered for the languages supported by Spacy: 
            Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
            Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
        Limited support for other languages is available.
        
    Returns:
    ----------
    *emo_words:
        A dictionary. For each emotion, a tuple (word, n_occurrences). Max 10 words per emotion.
    """
    
    emotion_lexicon = _load_dictionary(language)
        
    if not emotions:
        emotions = ['anger', 'trust', 'surprise', 'disgust', 'joy', 'sadness', 'fear', 'anticipation']
    
    worddf = pd.Series(wordlist).value_counts()
    worddf = pd.DataFrame({'word': worddf.index, 'count': worddf.values})
    
    worddf = pd.merge(worddf, emotion_lexicon, on = 'word').sort_values('count', ascending = False).reset_index()
    
    emo_words = {emo: worddf.loc[worddf['emotion'] == emo, ].head(10) for emo in emotions}
    
    return emo_words

    



def _samples(baseline_distr, sample_size, emotions = [], n_samples = 300, epsilon = 0.0):
    """
    Get mean and std of emotions distribution in randomized samples of words-related emotions taken from the baseline.

    Required arguments:
    ----------
    *baseline_distr*:
        Distribution of emotions in the baseline. 
        
    *sample_size*:
        An integer. How big the random samples are supposed to be.
        
    *emotions*:
        List of emotions.
        
    *n_samples*:
        An integer, how many samples to take from the baseline.
    
    Returns:
    ----------
    
    *wordlist*:
        A list of words. Words preceded by negations have been eliminated.    
    """
    
    emo_sample_tot = {emo: [] for emo in emotions}
    
    for k in range(n_samples):
        
        Lrandom = random.choices(baseline_distr, k = sample_size)
            
        # chain emotions
        randemo = list(itertools.chain(*Lrandom))
        randemo = {emo: randemo.count(emo) for emo in set(randemo)}
        
        # Update results
        emo_sample_tot = {k: emo_sample_tot.get(k) + [randemo.get(k, 0)] for k in set(emo_sample_tot)}
        
                
    # Get mean and std for each emotion
    emo_sample_tot = {k: {'mean': np.mean(val), 'std': np.std(val)} for k, val in emo_sample_tot.items()}
    if any([emo_sample_tot[k]['std'] == 0 for k in emo_sample_tot.keys()]):
        
        if epsilon > 0:        
            raise ValueError("There are too few emotions in input text. When sampling a list of words from a baseline, some emotions don't appear at all. The resulting z-score would result in a division by zero, and it would be not meaningful. Please input a larger text. You can also provide epsilon > 0, avoiding the DivisionByZero error.")
        else:
            for k in emo_sample_tot.keys():
                if emo_sample_tot[k]['std'] == 0:
                    emo_sample_tot[k]['std'] = epsilon
            
            warnings.warn("The emotion distribution of the samples of the baseline had some 0s. In order to avoid a division by zero, an epsilon = 0.1 has been forced as denominator when computing z-scores. Resampling is strongly suggested.")
    
    return emo_sample_tot