#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 18:52:01 2021

@author: alfonso
"""

import re
import pandas as pd
from resources import _load_spacy
from language_dependencies import _check_language
import formamentis_edgelist as fme



def _clean_text(text):
    """ Preliminary text cleaning: removing weird punctuation from words, stripping spaces. """
    
    text = text.replace('’', "'")
    text = text.replace('"', '')
    text = text.replace('”', '')
    text = text.replace('“', '')
    text = text.replace('«', '')
    text = text.replace('»', '')
    text = re.sub('\t', ' ', text)
    text = re.sub('\n', ' ', text)
    text = re.sub('[ ]+', ' ', text)
    text = text.lower()
#    text.encode("utf-8", "ignore").decode() 
    text = re.sub('\<u\+[0-9A-Za-z]+\>', '', text)
    # eccezioni e parole troppo corte
    text = text.strip()
    return text


def _handle_negations(wordlist, negations = None, language = 'english', antonyms = None, negation_strategy = 'ignore'):
    """
    Delete words preceded by negations.

    Required arguments:
    ----------
    *wordlist*:
        A list of words. 
        
    *negations*:
        A custom-defined list of negations. 
        Default is None: a pre-compiled list will be loaded.
        
    *language*:
        Language of the text. Full support is offered for the languages supported by Spacy: 
            Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
            Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
        Limited support for other languages is available.
    
    Returns:
    ----------
    
    *wordlist*:
        A list of words. Words preceded by negations have been eliminated.    
    """
    
    if not negations:
        from language_dependencies import _negations as negs
        
        negations = negs[language]
            
        
    if negation_strategy == 'delete':
        wordlist = [wordlist[i] for i in range(len(wordlist)) if (i == 0 or wordlist[i-1] not in negations)]
        
    elif negation_strategy == 'replace':
        wordlist = [antonyms.get(wordlist[i], wordlist[i]) if (i > 0 and wordlist[i-1] in negations) else wordlist[i] for i in range(len(wordlist))]
    
    elif negation_strategy == 'add':
        wordlist += [antonyms.get(wordlist[i], wordlist[i]) for i in range(len(wordlist)) if (i > 0 and wordlist[i-1] in negations)]        

    return wordlist
    





def _load_formamentis_edgelist(edgelist, spacy_model, target_word = None, language = 'english', duplicates = True, negation_strategy = 'ignore', negations = None, antonyms = None):
        
    """ Loads a wordlist from a formamentis network. """
    
    
     # Check for edgelist consistency
    if len(edgelist) == 0:
        return []
    elif type(edgelist) == list:
        if len(edgelist[0]) == 3:
            edgelist = [(a, b) for a, b, _ in edgelist]
        
        edgelist = pd.DataFrame(edgelist, columns = ['word', 'neighbor'])
        edgelist = edgelist.append(pd.DataFrame({'word': edgelist['neighbor'], 'neighbor': edgelist['word']}))
    elif 'pandas.core.frame.DataFrame' in str(type(edgelist)):
        edgelist.columns = ['word', 'neighbor']
        edgelist = edgelist.append(pd.DataFrame({'word': edgelist['neighbor'], 'neighbor': edgelist['word']}))  
        
    if negation_strategy != 'ignore':
        pass # do something here with negations
    
    
    if target_word:
        # Get neighbors of `target_word`
        L = edgelist.loc[edgelist['word'] == target_word, 'neighbor'].values
        
    else:
        # Get all words
        L = edgelist['neighbor'].values
        
    if not duplicates:
        L = list(set(L))
        
        
    return L
    



def _load_text(text, spacy_model, language = 'english', duplicates = False, negation_strategy = 'ignore', negations = None, antonyms = None):
    
    """ Loads a wordlist from a text. """
    
     # clean text
    text = _clean_text(text)
    
    # Check for language
    _check_language(language)
    
    
    ## REPLACED WITH TREETAGWRAPPER!
    
    # Load the correct spacy model
    nlp = _load_spacy(spacy_model, language)    
    # get tokens
    tokens = [token.lemma_ for token in nlp(text)]
    
    
        
    
    
    # Duplicates strategy
    if not duplicates:
        tokens = list(set(tokens))
        
    # Negation strategy
    if negation_strategy != 'ignore':
        tokens = _handle_negations(tokens, language = language, negations = negations, antonyms = antonyms, negation_strategy = negation_strategy)
    return tokens




def _load_object(obj,
                spacy_model,
                language,
                target_word,
                duplicates,
                negation_strategy,
                negations,
                antonyms,
                method,
                keepwords,
                stopwords,
                wn):
    
    """ Checks the format of the input, then loads the wordlist in the right way. """
    
    if type(obj) == tuple and type(obj[0][0]) == tuple:
        raise ValueError("You inputed a tuple of two elements, the first one being a list of tuples. Perhaps you are using a formamentis network as input? Only edges should be used.")
        
    if type(obj) == list:
        wordlist = _load_formamentis_edgelist(edgelist = obj,
                                 spacy_model = spacy_model,
                                 language = language,
                                 target_word = target_word,
                                 duplicates = duplicates,
                                 negation_strategy = negation_strategy,
                                 negations = negations,
                                 antonyms = antonyms)
        
        
    elif type(obj) == str and method == 'formamentis':
        edgelist, _ = fme._get_formamentis_edgelist(text = obj, 
                                            language = language, 
                                            spacy_model = spacy_model,
                                            keepwords = [],
                                            stopwords = ['it'],
                                            antonyms = antonyms,
                                            wn = wn)
        
        wordlist = _load_formamentis_edgelist(edgelist = edgelist,
                                 spacy_model = spacy_model,
                                 language = language,
                                 target_word = target_word,
                                 duplicates = duplicates,
                                 negation_strategy = negation_strategy,
                                 negations = negations,
                                 antonyms = antonyms)
    elif type(obj) == str:  
        
        if target_word and method != 'formamentis':
            raise ValueError("You must use the Formamentis networks if you want to target '{}' as target_word.".format(target_word))
        
        
        wordlist = _load_text(text = obj, 
                             spacy_model = spacy_model, 
                             language = language,
                             duplicates = duplicates,
                             negation_strategy = negation_strategy,
                             negations = negations,
                             antonyms = antonyms
                             )
    
    return wordlist






