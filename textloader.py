"""
@author: alfonso.semeraro@unito.it

"""

import re
from language_dependencies import _check_language
import itertools



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
    text = re.sub('\<u\+[0-9A-Za-z]+\>', '', text)
    text = text.strip()
    return text




def _load_text(text, language, tagger):
    
    """ Loads a wordlist from a text. """
    
     # clean text
    text = _clean_text(text)
    
    # Check for language
    _check_language(language)
    
    # get tokens
    tokens = [token.lemma_ for token in tagger(text)]
        
    
    return tokens




def _load_object(obj,
                tagger,
                language,
                emojis_dict,
                convert_emojis):
    
    """ Checks the format of the input, then loads the wordlist in the right way. """
    
    # DEALING WITH STRINGS
    if type(obj) == str:
        text = obj

    # DEALING WITH PANDAS
    elif 'pandas.core.frame.Series' in str(type(obj)):
        wordlist = list(itertools.chain(*obj.values))
        text = ' '.join(wordlist)
        
    # DEALING WITH FORMAMENTIS  
    elif 'FormamentisNetwork' in str(obj.__class__):
        wordlist = obj.vertices
        text = ' '.join(wordlist)
        
        
    else:
        raise ValueError("Only <str>, <pandas.core.frame.Series> and <FormamentisNetwork> objects accepted as inputs.")
        
    if convert_emojis:
        text = _convert_emojis(text, emojis_dict)
        
    wordlist = _load_text(text = text, tagger = tagger, language = language)
    
    
    return wordlist



def _convert_emojis(text, emojis_dict):
    text = [' ' + emojis_dict[f"U+{ord(s):X}"] + ' ' if f"U+{ord(s):X}" in emojis_dict else s for s in text]
    text = ''.join(text)   
    return text



