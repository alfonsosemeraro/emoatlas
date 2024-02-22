"""
@author: alfonso.semeraro@unito.it

"""

import re
from emoatlas.language_dependencies import _check_language
import itertools
from nltk import word_tokenize
from emoatlas.resources import _load_spacy, _load_emojis, _load_idiomatic_tokens


def multiple_replace(string, rep_dict):
    pattern = re.compile(
        "|".join([re.escape(k) for k in sorted(rep_dict, key=len, reverse=True)]),
        flags=re.DOTALL,
    )
    return pattern.sub(lambda x: rep_dict[x.group(0)], string)


def _clean_text(text):
    """Preliminary text cleaning: removing weird punctuation from words, stripping spaces."""

    text = text.replace("’", "'")
    text = text.replace('"', "")
    text = text.replace("”", "")
    text = text.replace("“", "")
    text = text.replace("«", "")
    text = text.replace("»", "")
    text = re.sub("\t", " ", text)
    text = re.sub("\n", " ", text)
    text = re.sub("[ ]+", " ", text)
    text = text.lower()
    text = re.sub("\<u\+[0-9A-Za-z]+\>", "", text)
    text = text.strip()

    return text


def _load_text(text, language, tagger, idiomatic_tokens):
    """Loads a wordlist from a text."""

    # clean text
    text = _clean_text(text)

    # Check for language
    _check_language(language)

    # replace idiomatic expressions with tokens
    if language != "english" and idiomatic_tokens:
        text = multiple_replace(text, idiomatic_tokens)

    # get tokens
    if "snowballstemmer" in str(tagger).lower():
        tokens = [tagger.stem(token) for token in word_tokenize(text)]
    elif "spacy" in str(tagger).lower():
        tokens = [token.lemma_ for token in tagger(text)]

    return tokens


def _load_object(obj, tagger, language, emojis_dict, convert_emojis, idiomatic_tokens):
    """Checks the format of the input, then loads the wordlist in the right way."""

    # DEALING WITH STRINGS
    if type(obj) == str:
        text = obj

    # DEALING WITH PANDAS
    elif "pandas.core.frame.Series" in str(type(obj)):
        wordlist = list(itertools.chain(*obj.values))
        text = " ".join(wordlist)

    # DEALING WITH FORMAMENTIS
    elif "FormamentisNetwork" in str(obj.__class__):
        wordlist = obj.vertices
        text = " ".join(wordlist)

    else:
        raise ValueError(
            "Only <str>, <pandas.core.frame.Series> and <FormamentisNetwork> objects accepted as inputs."
        )

    if convert_emojis:
        text = _convert_emojis(text, emojis_dict)

    wordlist = _load_text(
        text=text, tagger=tagger, language=language, idiomatic_tokens=idiomatic_tokens
    )

    return wordlist


def _convert_emojis(text, emojis_dict):
    text = [
        (
            " " + emojis_dict[f"U+{ord(s):X}"] + " "
            if f"U+{ord(s):X}" in emojis_dict
            else s
        )
        for s in text
    ]
    text = "".join(text)
    return text


# Used if you are only interested in lemmatizing texts
def lemmatize_text(text, language="english", idiomaticreplacement=False):
    tagger = _load_spacy(language)
    if idiomaticreplacement:
        idiomatictokens = _load_idiomatic_tokens(language)
    else:
        idiomatictokens = {}
    emojis = _load_emojis(language)

    lemmatized = _load_object(
        text,
        language=language,
        tagger=tagger,
        idiomatic_tokens=idiomatictokens,
        convert_emojis=True,
        emojis_dict=emojis,
    )
    print(lemmatized)
