#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 12:02:51 2021

@author: alfonso
"""

import numpy as np
from language_dependencies import _negations
from resources import _load_valences, _emotion_model_resources
import distributions as _dstr
import itertools
import textloader as _txl 
from collections import namedtuple
from baselines import _make_baseline


def _valence(obj,
            emotion_lexicon = None, 
           normalization_strategy = 'none', 
           emotions = None, 
           language = 'english',
           spacy_model = None,
           duplicates = True,
           negation_strategy = 'ignore',
           negations = None,
           antonyms = None,
           method = 'default',
           target_word = None,
           emotion_model = 'plutchik',
           wn = None):
        
    

    if not emotions and emotion_model == 'plutchik':
        emotions = ['anger', 'trust', 'surprise', 'disgust', 'joy', 'sadness', 'fear', 'anticipation']
        
    wordlist = _txl._load_object(obj = obj,
                           language = language,
                           spacy_model = spacy_model,
                           negation_strategy = negation_strategy,
                           negations = negations,
                           antonyms = antonyms,
                           method = method,
                           target_word = target_word,
                           duplicates = duplicates,
                           keepwords = [],
                           stopwords = ['it'],
                           wn = wn)
        
    
    _positive, _negative, _ = _load_valences(language)
    
    pos_score = len([w for w in wordlist if w in _positive])
    neg_score = len([w for w in wordlist if w in _negative])
    
    
    
    try:
        score = pos_score / (pos_score + neg_score)
        score = (score*2) - 1
    except Exception as e:
        print(e)
        score = 0
        
    return score

def _count_emotions(obj, 
                   emotion_lexicon = None, 
                   normalization_strategy = 'none', 
                   emotions = None, 
                   language = 'english',
                   spacy_model = 'en_core_web_sm',
                   duplicates = True,
                   negation_strategy = 'ignore',
                   negations = None,
                   antonyms = None,
                   method = 'default',
                   target_word = None,
                   emotion_model = 'plutchik',
                   wn = None):
    
    """
    Count emotions in given wordlist.

    Required arguments:
    ----------
    *text*:
        The input text. 
        
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
    *emo_counts*:
        A dict. For each emotion the associated counts.  
        
    *n_emotionwords*:
        An integer, the number of words associated with an emotion in wordlist.
    """        
    

    
    if not emotions and emotion_model == 'plutchik':
        emotions = ['anger', 'trust', 'surprise', 'disgust', 'joy', 'sadness', 'fear', 'anticipation']
        
    wordlist = _txl._load_object(obj = obj,
                           language = language,
                           spacy_model = spacy_model,
                           negation_strategy = negation_strategy,
                           negations = negations,
                           antonyms = antonyms,
                           method = method,
                           target_word = target_word,
                           duplicates = duplicates,
                           keepwords = [],
                           stopwords = ['it'],
                           wn = wn)
        
        
    emo_distr = _dstr._emotion_distribution(wordlist = wordlist, emotion_lexicon = emotion_lexicon, emotions = emotions, language = language)   
    n_emotionwords = len(emo_distr)
    
    
    emo = list(itertools.chain(*emo_distr))
    emo_counts = {emotion: emo.count(emotion) for emotion in emotions}
    
    if normalization_strategy not in ['none', 'num_words', 'num_emotions']:
        raise ValueError("'normalization_strategy' must be one of 'none', 'num_words', 'num_emotions'.")
        
    if normalization_strategy == 'num_words':
        emo_counts = {key: val / len(wordlist) for key, val in emo_counts.items()}
    elif normalization_strategy == 'num_emotions':
        try:
            emo_counts = {key: val / n_emotionwords for key, val in emo_counts.items()}
        except ZeroDivisionError:
            emo_counts = {key: 0 for key, _ in emo_counts.items()}
    
    ecounts = namedtuple('emotion_counts', 'emotions num_emotion_words')
    return ecounts(emo_counts, n_emotionwords)
    


def _emotion_words(obj, 
                   emotion_lexicon = None, 
                   normalization_strategy = 'none', 
                   emotions = None, 
                   language = 'english',
                   spacy_model = 'en_core_web_sm',
                   duplicates = True,
                   negation_strategy = 'ignore',
                   negations = None,
                   antonyms = None,
                   method = 'default',
                   target_word = None,
                   emotion_model = 'plutchik',
                   wn = None):
    
    """
    Count the words most associated to emotions in given object.

    Required arguments:
    ----------
    *text*:
        The input text. 
        
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
    *emo_counts*:
        A dict. For each emotion the associated counts.  
        
    *n_emotionwords*:
        An integer, the number of words associated with an emotion in wordlist.
    """        
    

    
    if not emotions and emotion_model == 'plutchik':
        emotions = ['anger', 'trust', 'surprise', 'disgust', 'joy', 'sadness', 'fear', 'anticipation']
        
    wordlist = _txl._load_object(obj = obj,
                           language = language,
                           spacy_model = spacy_model,
                           negation_strategy = negation_strategy,
                           negations = negations,
                           antonyms = antonyms,
                           method = method,
                           target_word = target_word,
                           duplicates = duplicates,
                           keepwords = [],
                           stopwords = ['it'],
                           wn = wn)
        
        
    emo_distr = _dstr._emotion_words(wordlist = wordlist, emotion_lexicon = emotion_lexicon, emotions = emotions, language = language)   

    for emo, val in emo_distr.items():
        emo_distr[emo] = {k: c for k, c in zip(val['word'], val['count'])}
    
    
    return emo_distr


def _stats(obj, 
          emotion_lexicon = None,
          emotions = None, 
          language = 'english',
          spacy_model = 'en_core_web_sm',
          duplicates = True,
          negation_strategy = 'ignore',
          negations = None,
          antonyms = None,
          method = 'default',
          target_word = None,
          emotion_model = 'plutchik',
          wn = None):
    
    
    wordlist = _txl._load_object(obj = obj,
                           language = language,
                           spacy_model = spacy_model,
                           negation_strategy = negation_strategy,
                           negations = negations,
                           antonyms = antonyms,
                           method = method,
                           target_word = target_word,
                           duplicates = duplicates,
                           keepwords = [],
                           stopwords = ['it'],
                           wn = wn)
        
        
    emo_distr = _dstr._emotion_distribution(wordlist = wordlist, emotion_lexicon = emotion_lexicon, emotions = emotions, language = language)   
    n_emotionwords = len(emo_distr)
    
    emo_distr_unique = _dstr._emotion_distribution(wordlist = list(set(wordlist)), emotion_lexicon = emotion_lexicon, emotions = emotions, language = language)
    n_emotionwords_unique = len(emo_distr_unique)
    
    
    emo = list(itertools.chain(*emo_distr))
    emo_counts = {emotion: emo.count(emotion) for emotion in emotions}
    
    
    emo_unique = list(itertools.chain(*emo_distr_unique))
    emo_counts_unique = {emotion: emo_unique.count(emotion) for emotion in emotions}
    
 
    out = {}
    out['emotions'] = {'num_emotionwords': n_emotionwords,
                       'num_emotionwords_unique': n_emotionwords_unique,
                       'perc_emotionwords': n_emotionwords / len(wordlist),
                       'perc_emotionwords_unique': n_emotionwords_unique / len(set(wordlist))}
    
    for emotion in emotions:
        out[emotion] = {'num_words': emo_counts[emotion],
                        'num_words_unique': emo_counts_unique[emotion],
                        'perc_text': emo_counts[emotion] / len(wordlist),
                        'perc_text_unique': emo_counts_unique[emotion] / len(set(wordlist))}
    
    for emotion in emotions:
        try:
            out[emotion]['perc_emotionwords'] = out[emotion]['num_words'] / n_emotionwords
            out[emotion]['perc_emotionwords_unique'] = out[emotion]['num_words_unique'] / n_emotionwords_unique
        except:
            out[emotion]['perc_emotionwords'] = 0
            out[emotion]['perc_emotionwords_unique'] = 0
            
    negations = _negations[language] if not negations else negations
    out['negations'] = {'num_negations': len([word for word in wordlist if word in negations]),
                        'num_negations_unique': len([word for word in set(wordlist) if word in negations])}
    
    out['words'] = {'num_words': len(wordlist), 'num_words_unique': len(set(wordlist))}
    
    return out
    





def _zscores(obj, 
           language = 'english', 
           spacy_model = 'en_core_web_sm',
           baseline = None, 
           emotion_lexicon = None, 
           duplicates = False, 
           negation_strategy = 'ignore', 
           antonyms = None, 
           negations = None, 
           n_samples = 300, 
           method = 'default',
           target_word = None,
           emotion_model = 'plutchik',
           wn = None, 
           epsilon = 0.0):
    
    """
    Get z-scores for each emotion detected in the any word of the wordlist.
    It compares emotions detected against mean and standard deviation of the same emotion
    in 300 random samples.

    Required arguments:
    ----------
    *text*:
        The input text. 
        
    *language*:
        Language of the text. Full support is offered for the languages supported by Spacy: 
            Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
            Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
        Limited support for other languages is available.
    
    *spacy_model*:
        Either a string or a spacy object. If string, it must be the name of a spacy model installed on your system.
        
    *baseline*:
        A list of words. Wordlist's emotion distribution will be checked against the baseline's emotion distribution.
        Default is None: wordlist will be checked against a random sample from the emotion_lexicon.
        
    *emotion_lexicon*:
        A lexicon with every word-emotion association. By default, the NRCLexicon will be loaded.
        
    *negation_strategy*:
        A string, if words introduced by negations will be replaced by their antynomies.
        Default is ignore', for which no action will be done.
        Other values accepted are 'replace', i.e. words introduced by negations will be replaced,
        and 'delete', i.e. those words will be deleted.
    
    *antonyms*:
        A dict. For each word in the dict's keys, the correspondent value is its antynomy.
        Default is None: a pre-compiled dictionary will be loaded.
        
    *negations*:
        A custom-defined list of negations. 
        Default is None: a pre-compiled list will be loaded.
    
    *duplicates*:
        A boolean: if True, words associated with emotions will be counted as many times as they appear into the wordlist.
        If False, each word will be counted only once. Default is False.
        
    *n_samples*:
        An integer: how many times the wordlist will be checked against a random sample taken from a custom baseline.
        
    *emotion_model*:
        A string, what emotion model to use. Default is 'plutchik', i.e. the Plutchik's wheel of emotions.
    
    Returns:
    ----------
    
    *zscores*:
        A dict. For each emotion the associated z-score.    
    """
    
    
    # 1. load 
    # 2. get resources for emotion model == plutchik?
    # 3. check data duplicates
    # 4. handle negations
    # 5. get emotion counts
    # 6. manage the baseline
    # 7. get random samples distribution
    # 8. return z-scores
    
    
#    # Check for language
#    check_language(language)
    
    # Check emotions resources: lexicon and emtions
    emotion_lexicon, emotions = _emotion_model_resources(emotion_lexicon = emotion_lexicon, 
                                                               emotion_model = emotion_model,
                                                               language = language)
    
    
    # check data format
    if len(obj) == 0:
        return {emo: np.nan for emo in emotions}
    
    
    # count emotions in wordlist
    emo_counts, n_emotionwords = _count_emotions(obj = obj, 
                                                emotion_lexicon = emotion_lexicon,
                                                normalization_strategy = 'none',
                                                language = language,
                                                spacy_model = spacy_model, 
                                                duplicates = duplicates,
                                                negation_strategy = negation_strategy,
                                                negations = negations,
                                                antonyms = antonyms,
                                                emotions = emotions,
                                                method = method,
                                                target_word = target_word,
                                                wn = wn)
    
    # sample against baseline
    baseline = _make_baseline(baseline = baseline, spacy_model = spacy_model, emotion_lexicon = emotion_lexicon, emotions = emotions, language = language)
    
    
    # Get emotions in 300 random samples
    emo_samples = _dstr._samples(baseline_distr = baseline, sample_size = n_emotionwords, n_samples = n_samples, emotions = emotions, epsilon = epsilon)
    
    # Get z-scores
    zscores = {key.lower(): (emo_counts.get(key, 0) - emo_samples[key]['mean']) / emo_samples[key]['std'] for key in emotions}

    
    return zscores

 
    