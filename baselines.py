#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 15:25:46 2021

@author: alfonso
"""
from resources import _load_dictionary
from collections import namedtuple
import distributions as _dstr
import itertools
import textloader as _txl 



def _baseline_distribution(baseline, emotions = None, emotion_model = 'plutchik', normalization_strategy = 'num_emotions'):
    
    if not emotions and emotion_model == 'plutchik':
        emotions = ['anger', 'trust', 'surprise', 'disgust', 'joy', 'sadness', 'fear', 'anticipation']
    
    emo = list(itertools.chain(*baseline))
    emo_counts = {emotion: emo.count(emotion) for emotion in emotions}
    
    if normalization_strategy not in ['none', 'num_emotions']:
        raise ValueError("'normalization_strategy' must be one of 'none', 'num_emotions'.")
        
    elif normalization_strategy == 'num_emotions':
        emo_counts = {key: val / len(baseline) for key, val in emo_counts.items()}
        
    ecounts = namedtuple('emotion_counts', 'emotions num_emotion_words')
    return ecounts(emo_counts, len(baseline))



def _make_baseline(baseline = None, emotion_lexicon = None, emotions = None, language = 'english', spacy_model = None):
    """
    Get emotion distribution in baseline_wordlist. If empty, use the lexicon as baseline_wordlist.

    Required arguments:
    ----------
    *baseline_wordlist*:
        A list of words. 
        
    *language*:
        Language of the text. Full support is offered for the languages supported by Spacy: 
            Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
            Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
        Limited support for other languages is available.
    
    *emotion_lexicon*:
        A lexicon with every word-emotion association. By default, the NRCLexicon will be loaded.
            
    *emotions*:
        A list of emotions, depending on the model required. Default is Pluthick's wheel of emotions model.
    
    Returns:
    ----------
    *baseline_distr*:
        A list of lists. Each entry is a list of emotions associated to a word in wordlist.
    """
    
    baseline_distr = None
    
    if not emotion_lexicon:
        emotion_lexicon = _load_dictionary(language)
        emotion_lexicon = emotion_lexicon.groupby('word')['emotion'].apply(list).to_dict()
        
    
    if not emotions:
        emotions = ['anger', 'trust', 'surprise', 'disgust', 'joy', 'sadness', 'fear', 'anticipation']
        
    if not baseline:
        baseline_wordlist = list(emotion_lexicon.keys())
        baseline_distr = _dstr._emotion_distribution(wordlist = baseline_wordlist, 
                                                         emotion_lexicon = emotion_lexicon, 
                                                         emotions = emotions, 
                                                         language = language)
    # String
    elif type(baseline) == str: 
        if spacy_model:
            baseline_wordlist = _txl._load_text(baseline,
                                          language = language, 
                                          spacy_model = spacy_model, 
                                          duplicates = False, 
                                          negation_strategy = 'ignore', 
                                          antonyms = None, 
                                          negations = None)
            
            
            baseline_distr = _dstr._emotion_distribution(wordlist = baseline_wordlist, 
                                                         emotion_lexicon = emotion_lexicon, 
                                                         emotions = emotions, 
                                                         language = language)
            
        else:
            raise ValueError("Cannot build a baseline emotion distribution without a spacy model!")
            
    
    # Formamentis edgelist
    elif type(baseline) == list and type(baseline[0]) == tuple:
        baseline_wordlist = _txl._load_formamentis_edgelist(baseline,
                                          language = language, 
                                          spacy_model = spacy_model, 
                                          duplicates = False, 
                                          negation_strategy = 'ignore', 
                                          antonyms = None, 
                                          negations = None)
        
        baseline_distr = _dstr._emotion_distribution(wordlist = baseline_wordlist, 
                                                         emotion_lexicon = emotion_lexicon, 
                                                         emotions = emotions, 
                                                         language = language)
        
    elif 'pandas.core.frame.DataFrame' in str(type(baseline)) :
        baseline_wordlist = _txl._load_formamentis_edgelist(baseline,
                                          language = language, 
                                          spacy_model = spacy_model, 
                                          duplicates = False, 
                                          negation_strategy = 'ignore', 
                                          antonyms = None, 
                                          negations = None)
        
        baseline_distr = _dstr._emotion_distribution(wordlist = baseline_wordlist, 
                                                         emotion_lexicon = emotion_lexicon, 
                                                         emotions = emotions, 
                                                         language = language)
        
    # Baseline previously made by this library
    elif type(baseline) == list and type(baseline[0]) == list:
        baseline_distr = baseline
    
    
    if not baseline_distr:
            raise ValueError("Baseline has no emotions. Please provide a meaningful baseline or None.")
        
    return baseline_distr
