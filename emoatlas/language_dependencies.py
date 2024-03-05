"""
Created on Wed Aug 25 14:07:11 2021

@author: alfonso
"""

_negations = {
    "german": ["nicht", "nein"],
    "english": [
        "no",
        "neither",
        "not",
        "cannot",
        "never",
        "can't",
        "won't",
        "nothing",
        "don't",
        "doesn't",
        "didn't",
        "n't",
    ],
    "italian": ["non", "no", "né"],
    "french": ["non", "pas", "ne"],
    "danish": ["nej", "ikke"],
    "dutch": ["nee", "niet"],
    "catalan": ["no", "tampoc"],
    "chinese": ["都不是", "不"],
    "greek": ["δεν", "ούτε", "όχι"],
    "japanese": ["いいえ"],
    "lituanian": ["ne", "nei"],
    "macedonian": ["не", "ниту"],
    "norvegian": ["ikke", "nei"],
    "polish": ["nie", "ani"],
    "portuguese": ["não", "nem"],
    "romanian": ["nu", "nici"],
    "russian": ["нет", "ни"],
    "spanish": ["no", "ni"],
}

_pronouns = {
    "german": [
        "dir",
        "mich",
        "es",
        "ihnen",
        "unser",
        "uns",
        "wir",
        "euer",
        "sein",
        "sie",
        "du",
        "mein",
        "er",
        "dein",
        "euch",
        "dich",
        "ihr",
        "ich",
        "mir",
        "ihn",
        "ihm",
        "sich",
    ],
    "english": [
        "he",
        "his",
        "we",
        "her",
        "them",
        "i",
        "they",
        "me",
        "us",
        "you",
        "she",
    ],
    "italian": [
        "ella",
        "esso",
        "io",
        "te",
        "lei",
        "egli",
        "vi",
        "voi",
        "tu",
        "noi",
        "essa",
        "lui",
        "essi",
        "me",
        "loro",
    ],
    "french": ["ils", "elle", "elles", "il", "on", "tu", "vous", "nous", "je"],
    "danish": ["de", "hun", "han", "vi", "jeg", "i", "du"],
    "dutch": ["jullie", "u", "ik", "jij", "zij", "hij", "wij"],
    "catalan": [
        "jo",
        "ella",
        "nosaltres",
        "ells",
        "vós",
        "tu",
        "vos",
        "vosaltres",
        "el",
    ],
    "chinese": [
        "您",
        "你们",
        "我",
        "他们",
        "它",
        "你",
        "它们",
        "我们",
        "她们",
        "咱们",
        "她",
        "他",
    ],
    "greek": [
        "εσείς",
        "αυτος",
        "αυτά",
        "eγώ",
        "αυτή",
        "αυτη",
        "αυτα",
        "αυτο",
        "αυτοι",
        "εμείς",
        "αυτοί",
        "αυτός",
        "αυτες",
        "εσύ",
    ],
    "japanese": [
        "僕",
        "私",
        "我々",
        "彼",
        "俺",
        "おれ",
        "方",
        "お前",
        "彼女",
        "かのじょ",
        "貴方",
        "あのひと",
        "あなた",
        "あの人",
        "私達",
        "君",
        "ぼく",
        "わたし",
        "おまえ",
        "かれ",
        "きみ",
    ],
    "lituanian": [
        "jóms",
        "jám",
        "tavyjè",
        "tavimì",
        "noi",
        "mùms",
        "jùs",
        "manè",
        'jiẽ", "essi',
        "jomìs",
        "mán",
        "jū̃s",
        "mùs",
        "mumysè",
        "mẽs",
        "jumìs",
        "jùms",
        "juosè",
        "jaĩs",
        "jõs",
        "jái",
        "jumysè",
        "jį̃",
        "mumìs",
        "josè",
        "mū́sų",
        "jojè",
        "jàs",
        "juõs",
        "jà",
        "j¡ems",
        "voi",
        "táu",
        "tavè",
        "esse",
        "juõ",
        "manimì",
        "ją̃",
        "jū́sų",
        "jamè",
        "jų̃",
        "manyjè",
    ],
    "macedonian": ["ти", "јас", "таа", "тие", "вие", "ние", "тој"],
    "norvegian": [
        "de",
        "hun",
        "han",
        "henne",
        "dem",
        "han, ham",
        "seg",
        "det",
        "vi",
        "jeg",
        "dere",
        "deg",
        "den",
        "oss",
        "meg",
        "du",
    ],
    "polish": ["wy", "on", "ja", "my", "ty", "ona", "oni", "pan"],
    "portuguese": ["nós", "vós", "elas", "eu", "ele", "tu", "eles", "ela"],
    "romanian": [
        "dumneaei",
        "ei",
        "eu",
        "ele",
        "dvs",
        "voi",
        "tu",
        "dumnealui",
        "noi",
        "dumnealor",
        "dumneavoastră",
        "ea",
        "el",
    ],
    "russian": [
        "o ней",
        "онa",
        "ими",
        "мне",
        "вами",
        "них",
        "нами",
        "ему",
        "тебе",
        "нам",
        "o вас",
        "её",
        "вас",
        "ей",
        "они",
        "o нас",
        "его",
        "я",
        "меня",
        "oбo мне",
        "тобой",
        "него",
        "ты",
        "тебя",
        "неё",
        "вам",
        "он/оно",
        "их",
        "o нём",
        "вы",
        "нас",
        "мы",
        "o тебe",
        "мной",
        "им",
        "о них",
    ],
    "spanish": [
        "ella",
        "vosotros",
        "vosotras",
        "las",
        "usted",
        "los",
        "nos",
        "vusted",
        "te",
        "yo",
        "le",
        "ellos",
        "vustedes",
        "os",
        "nosotros",
        "vuecencia",
        "vuecencias",
        "ustedes",
        "les",
        "ello",
        "nosotras",
        "vusías",
        "ellas",
        "me",
        "la",
        "tú",
        "se",
        "lo",
        "vusía",
        "él",
    ],
}


def _valences(language):

    if language == "catalan":
        from valence.catalan import _positive, _negative, _ambivalent

    elif language == "chinese":
        from valence.chinese import _positive, _negative, _ambivalent

    elif language == "danish":
        from valence.danish import _positive, _negative, _ambivalent

    elif language == "dutch":
        from valence.dutch import _positive, _negative, _ambivalent

    elif language == "english":
        from valence.english import _positive, _negative, _ambivalent

    elif language == "french":
        from valence.french import _positive, _negative, _ambivalent

    elif language == "german":
        from valence.german import _positive, _negative, _ambivalent

    elif language == "greek":
        from valence.greek import _positive, _negative, _ambivalent

    elif language == "italian":
        from valence.italian import _positive, _negative, _ambivalent

    elif language == "japanese":
        from valence.japanese import _positive, _negative, _ambivalent

    elif language == "lithuanian":
        from valence.lithuanian import _positive, _negative, _ambivalent

    elif language == "norwegian":
        from valence.norwegian import _positive, _negative, _ambivalent

    elif language == "polish":
        from valence.polish import _positive, _negative, _ambivalent

    elif language == "portuguese":
        from valence.portuguese import _positive, _negative, _ambivalent

    elif language == "romanian":
        from valence.romanian import _positive, _negative, _ambivalent

    elif language == "russian":
        from valence.russian import _positive, _negative, _ambivalent

    elif language == "spanish":
        from valence.spanish import _positive, _negative, _ambivalent

    elif language == "macedonian":
        from valence.macedonian import _positive, _negative, _ambivalent

    return _positive, _negative, _ambivalent


def _language_code3(language):

    missing = ["russian", "macedonian", "german"]
    if language in missing:
        return None

    if language == "chinese":
        return "cmn"
    if language == "greek":
        return "ell"
    if language == "norwegian":
        return "nno"
    if language == "romanian":
        return "ron"
    if language == "japanese":
        return "jpn"
    if language == "dutch":
        return "nld"
    if language == "french":
        return "fra"

    ok_lang = [
        "catalan",
        "danish",
        "spanish",
        "italian",
        "polish",
        "english",
        "lithuanian",
        "portuguese",
    ]
    if language in ok_lang:
        return language[:3]

    return None


def _check_language(language):

    # Check for language
    try:
        allowed_languages = [
            "catalan",
            "chinese",
            "danish",
            "dutch",
            "english",
            "french",
            "german",
            "greek",
            "japanese",
            "italian",
            "lithuanian",
            "macedonian",
            "norwegian",
            "polish",
            "portuguese",
            "romanian",
            "russian",
            "spanish",
        ]
        assert language in allowed_languages
    except:
        raise ValueError(
            "'{}' is not allowed as a language. Please specify a language among '{}'.".format(
                language, "', '".join(allowed_languages)
            )
        )

    return


def _language_correction_tokens(token, language):
    if language == "italian":
        if "'" in token:
            return token.split("'")[1]
    return token


def _language_correction_text(text, language):
    if language == "italian":
        return text.replace("'", "o ")
    return text
