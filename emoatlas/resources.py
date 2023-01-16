"""
@author: alfonso.semeraro@unito.it

"""

import spacy
import json
import os
import emoatlas
from nltk.stem.snowball import SnowballStemmer


def _load_dictionary(language, stem_or_lem="lemmatization"):
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

    try:
        if stem_or_lem == "lemmatization":
            with open(
                f"{emoatlas.__path__[0]}{os.sep}langs{os.sep}{language}.json", "r"
            ) as fr:
                lang_df = json.load(fr)

        elif stem_or_lem == "stemming":
            with open(
                f"{emoatlas.__path__[0]}{os.sep}langs{os.sep}{language}_stem.json", "r"
            ) as fr:
                lang_df = json.load(fr)

        return lang_df

    except:
        raise ValueError("Language not supported.")


def _load_idiomatic_tokens(language, stem_or_lem="lemmatization"):
    """
    It loads the lexicon of replacements of idiomatic expressions with tokens, for the required languages.

    Required arguments:
    ----------

    *language*:
        One of the languages supported by Spacy:
            Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
            Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.

    Returns:
    ----------
    *idiomatic_tokens*:
        A dict: the replacements with < idiomatic_expression, token >.

    """
    try:
        if stem_or_lem == "lemmatization":
            with open(
                f"{emoatlas.__path__[0]}{os.sep}langs{os.sep}{language}_idiomatic_tokens.json",
                "r",
            ) as fr:
                idiomatic_tokens = json.load(fr)

        elif stem_or_lem == "stemming":
            with open(
                f"{emoatlas.__path__[0]}{os.sep}langs{os.sep}{language}_stem_idiomatic_tokens.json",
                "r",
            ) as fr:
                idiomatic_tokens = json.load(fr)

        return idiomatic_tokens

    except:
        raise ValueError("Language not supported.")


def _load_spacy(language="english"):
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
        raise ValueError(
            "spacy_model must be either a string or a loaded Spacy model. Can't find Spacy model '{}' on your system. Please install a model from https://spacy.io/models.".format(
                spacy_model_lang
            )
        )


def _spacy_model_by_language(language):

    if language == "catalan":
        return "ca_core_news_lg"
    if language == "chinese":
        return "zh_core_web_lg"
    if language == "danish":
        return "da_core_news_lg"
    if language == "dutch":
        return "nl_core_news_lg"
    if language == "english":
        return "en_core_web_lg"
    if language == "french":
        return "fr_core_news_lg"
    if language == "german":
        return "de_core_news_lg"
    if language == "greek":
        return "el_core_news_lg"
    if language == "italian":
        return "it_core_news_lg"
    if language == "japanese":
        return "ja_core_news_lg"
    if language == "lithuanian":
        return "lt_core_news_lg"
    if language == "macedonian":
        return "mk_core_news_lg"
    if language == "norwegian":
        return "nb_core_news_lg"
    if language == "polish":
        return "pl_core_news_lg"
    if language == "portuguese":
        return "pt_core_news_lg"
    if language == "romanian":
        return "ro_core_news_lg"
    if language == "russian":
        return "ru_core_news_lg"
    if language == "spanish":
        return "es_core_news_lg"


def _load_stemmer(language):

    try:
        stemmer = SnowballStemmer(language)
    except:
        raise ValueError("Language not supported.")

    return stemmer


def _emotion_model_resources(
    emotion_lexicon=None, emotion_model="plutchik", language="english"
):
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

    if emotion_model == "plutchik":
        emotions = [
            "anger",
            "trust",
            "surprise",
            "disgust",
            "joy",
            "sadness",
            "fear",
            "anticipation",
        ]

        if not emotion_lexicon:
            emotion_lexicon = _load_dictionary(language)
            emotion_lexicon = (
                emotion_lexicon.groupby("word")["emotion"].apply(list).to_dict()
            )

        return emotion_lexicon, emotions


def _load_emojis(language):

    if language == "english":
        with open(f"{emoatlas.__path__[0]}{os.sep}langs{os.sep}emojis.json", "r") as fr:
            return json.load(fr)

    return {}


def _load_antonyms(language):

    if language == "catalan":
        from emoatlas.antonyms.catalan import _antonyms

        return _antonyms
    if language == "chinese":
        from emoatlas.antonyms.chinese import _antonyms

        return _antonyms
    if language == "danish":
        from emoatlas.antonyms.danish import _antonyms

        return _antonyms
    if language == "dutch":
        from emoatlas.antonyms.dutch import _antonyms

        return _antonyms
    if language == "english":
        from emoatlas.antonyms.english import _antonyms

        return _antonyms
    if language == "french":
        from emoatlas.antonyms.french import _antonyms

        return _antonyms
    if language == "german":
        from emoatlas.antonyms.german import _antonyms

        return _antonyms
    if language == "greek":
        from emoatlas.antonyms.greek import _antonyms

        return _antonyms
    if language == "italian":
        from emoatlas.antonyms.italian import _antonyms

        return _antonyms
    if language == "japanese":
        from emoatlas.antonyms.japanese import _antonyms

        return _antonyms
    if language == "lithuanian":
        from emoatlas.antonyms.lithuanian import _antonyms

        return _antonyms
    if language == "macedonian":
        from emoatlas.antonyms.macedonian import _antonyms

        return _antonyms
    if language == "norwegian":
        from emoatlas.antonyms.norwegian import _antonyms

        return _antonyms
    if language == "polish":
        from emoatlas.antonyms.polish import _antonyms

        return _antonyms
    if language == "portuguese":
        from emoatlas.antonyms.portuguese import _antonyms

        return _antonyms
    if language == "romanian":
        from emoatlas.antonyms.romanian import _antonyms

        return _antonyms
    if language == "russian":
        from emoatlas.antonyms.russian import _antonyms

        return _antonyms
    if language == "spanish":
        from emoatlas.antonyms.spanish import _antonyms

        return _antonyms


def _valences(language):

    if language == "catalan":
        from emoatlas.valence.catalan import _positive, _negative, _ambivalent

    elif language == "chinese":
        from emoatlas.valence.chinese import _positive, _negative, _ambivalent

    elif language == "danish":
        from emoatlas.valence.danish import _positive, _negative, _ambivalent

    elif language == "dutch":
        from emoatlas.valence.dutch import _positive, _negative, _ambivalent

    elif language == "english":
        from emoatlas.valence.english import _positive, _negative, _ambivalent

    elif language == "french":
        from emoatlas.valence.french import _positive, _negative, _ambivalent

    elif language == "german":
        from emoatlas.valence.german import _positive, _negative, _ambivalent

    elif language == "greek":
        from emoatlas.valence.greek import _positive, _negative, _ambivalent

    elif language == "italian":
        from emoatlas.valence.italian import _positive, _negative, _ambivalent

    elif language == "japanese":
        from emoatlas.valence.japanese import _positive, _negative, _ambivalent

    elif language == "lithuanian":
        from emoatlas.valence.lithuanian import _positive, _negative, _ambivalent

    elif language == "norwegian":
        from emoatlas.valence.norwegian import _positive, _negative, _ambivalent

    elif language == "polish":
        from emoatlas.valence.polish import _positive, _negative, _ambivalent

    elif language == "portuguese":
        from emoatlas.valence.portuguese import _positive, _negative, _ambivalent

    elif language == "romanian":
        from emoatlas.valence.romanian import _positive, _negative, _ambivalent

    elif language == "russian":
        from emoatlas.valence.russian import _positive, _negative, _ambivalent

    elif language == "spanish":
        from emoatlas.valence.spanish import _positive, _negative, _ambivalent

    elif language == "macedonian":
        from emoatlas.valence.macedonian import _positive, _negative, _ambivalent

    return _positive, _negative, _ambivalent
