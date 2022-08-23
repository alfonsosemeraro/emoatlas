"""
@author: alfonso.semeraro@unito.it

"""

import spacy
import json

def _load_dictionary( language ):
    """
    It loads the emotional lexicon for the required languages.

    Required arguments:
    ----------
    
    *language*:
        One of the languages supported by Spacy: 
            Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
            Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.   
    
    Returns:
    ----------
    *lang_df*:
        A pandas dataframe: the table that contains the association < word, emotion >.    
        
    """
    
    if language == 'catalan':
        from langs.catalan import lang_df
        
    elif language == 'chinese':
        from langs.chinese import lang_df
        
    elif language == 'danish':
        from langs.danish import lang_df
        
    elif language == 'dutch':
        from langs.dutch import lang_df
        
    elif language == 'english':
        from langs.english import lang_df
        
    elif language == 'french':
        from langs.french import lang_df
        
    elif language == 'german':
        from langs.german import lang_df
        
    elif language == 'greek':
        from langs.greek import lang_df
        
    elif language == 'italian':
        from langs.italian import lang_df
        
    elif language == 'japanese':
        from langs.japanese import lang_df
        
    elif language == 'lithuanian':
        from langs.lithuanian import lang_df
        
    elif language == 'norwegian':
        from langs.norwegian import lang_df
        
    elif language == 'polish':
        from langs.polish import lang_df
        
    elif language == 'portuguese':
        from langs.portuguese import lang_df
        
    elif language == 'romanian':
        from langs.romanian import lang_df
        
    elif language == 'russian':
        from langs.russian import lang_df
        
    elif language == 'spanish':
        from langs.spanish import lang_df
        
    elif language == 'macedonian':
        from langs.macedonian import lang_df
        
    else:
        raise ValueError("Language not supported.")
        
    lang_df = lang_df.sort_values('emotion').reset_index()
    del lang_df['index']
    
    lang_df = lang_df.groupby('word')['emotion'].apply(list).to_dict()
        
    return lang_df





def _load_spacy(language = 'english'):
    """
    Returns a spacy model object depending on the input provided.
    If no spacy_model will be inputed, a spacy model will be loaded according with the language parameter.
    
    Required arguments:
    ----------
          
    *language*:
        Language of the text. Full support is offered for the languages supported by Spacy: 
            Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
            Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
        Limited support for other languages is available.  By default, English will be loaded.
        
    Returns:
    ----------
    *spacy_model*:
        spacy model loaded
    """
    
    try:
        # Spacy model depends on language
        spacy_model_lang = _spacy_model_by_language(language)
        
        return spacy.load(spacy_model_lang)

    except:
        raise ValueError("spacy_model must be either a string or a loaded Spacy model. Can't find Spacy model '{}' on your system. Please install a model from https://spacy.io/models.".format(spacy_model_lang))



def _spacy_model_by_language( language ):
                
    if language == 'catalan':
        return 'ca_core_news_lg'
    if language == 'chinese':
        return 'zh_core_web_lg'
    if language == 'danish':
        return 'da_core_news_lg'
    if language == 'dutch':
        return 'nl_core_news_lg'
    if language == 'english':
        return 'en_core_web_lg'
    if language == 'french':
        return 'fr_core_news_lg'
    if language == 'german':
        return 'de_core_news_lg'
    if language == 'greek':
        return 'el_core_news_lg'
    if language == 'italian':
        return 'it_core_news_lg'
    if language == 'japanese':
        return 'ja_core_news_lg'
    if language == 'lithuanian':
        return 'lt_core_news_lg'
    if language == 'macedonian':
        return 'mk_core_news_lg'
    if language == 'norwegian':
        return 'nb_core_news_lg'
    if language == 'polish':
        return 'pl_core_news_lg'
    if language == 'portuguese':
        return 'pt_core_news_lg'
    if language == 'romanian':
        return 'ro_core_news_lg'
    if language == 'russian':
        return 'ru_core_news_lg'
    if language == 'spanish':
        return 'es_core_news_lg'


def _emotion_model_resources(emotion_lexicon = None, emotion_model = 'plutchik', language = 'english'):
    """
    Fetch the lexicon (if not provided by the user) and the emotion names list, depending on the emotion model required.

    Required arguments:
    ----------        
    *emotion_lexicon*:
        A lexicon with every word-emotion association. Required format is a dict <word, emotion_list>.
        By default, the NRCLexicon will be loaded.
        
    *emotion_model*:
        A string, what emotion model to use. Default is 'plutchik', i.e. the Plutchik's wheel of emotions.
        
    *language*:
        Language of the text. Full support is offered for the languages supported by Spacy: 
            Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
            Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
        Limited support for other languages is available.
    
    Returns:
    ----------
    *emotion_lexicon*:
        A dict. For each word in the keys, the value is a list of emotions associated.  
    
    *emotions*:
        A list of emotions, depending on the model.
    """
    
    
    if emotion_model == 'plutchik':
        emotions = ['anger', 'trust', 'surprise', 'disgust', 'joy', 'sadness', 'fear', 'anticipation']
        
        if not emotion_lexicon:
            emotion_lexicon = _load_dictionary(language)
            emotion_lexicon = emotion_lexicon.groupby('word')['emotion'].apply(list).to_dict()
        
        return emotion_lexicon, emotions
    
    
def _load_emojis( language ):
    
    if language == 'english':
        with open('lexicons/emojis.json', 'r') as fr:
            return json.load(fr)
       
    return {}



def _load_antonyms(language):
    
    if language == 'catalan':
        from antonyms.catalan import _antonyms
        return _antonyms
    if language == 'chinese':
        from antonyms.chinese import _antonyms
        return _antonyms
    if language == 'danish':
        from antonyms.danish import _antonyms
        return _antonyms
    if language == 'dutch':
        from antonyms.dutch import _antonyms
        return _antonyms
    if language == 'english':
        from antonyms.english import _antonyms
        return _antonyms
    if language == 'french':
        from antonyms.french import _antonyms
        return _antonyms
    if language == 'german':
        from antonyms.german import _antonyms
        return _antonyms
    if language == 'greek':
        from antonyms.greek import _antonyms
        return _antonyms
    if language == 'italian':
        from antonyms.italian import _antonyms
        return _antonyms
    if language == 'japanese':
        from antonyms.japanese import _antonyms
        return _antonyms
    if language == 'lithuanian':
        from antonyms.lithuanian import _antonyms
        return _antonyms
    if language == 'macedonian':
        from antonyms.macedonian import _antonyms
        return _antonyms
    if language == 'norwegian':
        from antonyms.norwegian import _antonyms
        return _antonyms
    if language == 'polish':
        from antonyms.polish import _antonyms
        return _antonyms
    if language == 'portuguese':
        from antonyms.portuguese import _antonyms
        return _antonyms
    if language == 'romanian':
        from antonyms.romanian import _antonyms
        return _antonyms
    if language == 'russian':
        from antonyms.russian import _antonyms
        return _antonyms
    if language == 'spanish':
        from antonyms.spanish import _antonyms
        return _antonyms
    
    

def _valences(language):
    
    if language == 'catalan':
        from valence.catalan import _positive, _negative, _ambivalent
        
    elif language == 'chinese':
        from valence.chinese import _positive, _negative, _ambivalent
        
    elif language == 'danish':
        from valence.danish import _positive, _negative, _ambivalent
        
    elif language == 'dutch':
        from valence.dutch import _positive, _negative, _ambivalent
        
    elif language == 'english':
        from valence.english import _positive, _negative, _ambivalent
        
    elif language == 'french':
        from valence.french import _positive, _negative, _ambivalent
        
    elif language == 'german':
        from valence.german import _positive, _negative, _ambivalent
        
    elif language == 'greek':
        from valence.greek import _positive, _negative, _ambivalent
        
    elif language == 'italian':
        from valence.italian import _positive, _negative, _ambivalent
        
    elif language == 'japanese':
        from valence.japanese import _positive, _negative, _ambivalent
        
    elif language == 'lithuanian':
        from valence.lithuanian import _positive, _negative, _ambivalent
        
    elif language == 'norwegian':
        from valence.norwegian import _positive, _negative, _ambivalent
        
    elif language == 'polish':
        from valence.polish import _positive, _negative, _ambivalent
        
    elif language == 'portuguese':
        from valence.portuguese import _positive, _negative, _ambivalent
        
    elif language == 'romanian':
        from valence.romanian import _positive, _negative, _ambivalent
        
    elif language == 'russian':
        from valence.russian import _positive, _negative, _ambivalent
        
    elif language == 'spanish':
        from valence.spanish import _positive, _negative, _ambivalent
        
    elif language == 'macedonian':
        from valence.macedonian import _positive, _negative, _ambivalent
        
    return _positive, _negative, _ambivalent
