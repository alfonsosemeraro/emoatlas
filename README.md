# emolib
A Python library for the detection and visualization of emotions in texts, coming soon with the first release ✨

**Installation:**
emolib installs with pip:

```
~$ pip install git+https://github.com/alfonsosemeraro/emolib
```
then install the relevant language using:

```
~$ python -m spacy download en_core_web_lg
```
the command above installs English, but a list of possible language codes can be found [here](https://spacy.io/usage/models), and different languages installed by changing `en` in the final argument to one of the listed language codes. 

Running the files in `demos/` additionally requires [jupyter notebook](https://github.com/jupyter/notebook)

**Main Features:**
  - Extraction of emotions from texts in multiple languages
  - Statistical significance of emotions distribution
  - Extraction of emotions via structured semantic networks 👉 check the Formamentis Networks [here](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0222870)
  - Visualization of emotions 👉 check the PyPlutchik library [here](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0256503)


Emolib is a Python library that checks against the input text, after having enriched it and structured as a semantic network, against the multilingual [NRC Lexicon](https://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm). The library is built upon the [Formamentis Networks](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0222870) from Stella et al. and the [PyPlutchik library]() (paper [here](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0256503)).

It has already been used for our analysis of the [semantic and emotional frames around COVID-19 vaccines](https://arxiv.org/abs/2201.07538), repository [here](https://github.com/alfonsosemeraro/vaccines-and-press).
Check out our analysis of the emotional content of the [Festival di Sanremo 2022](https://arcs.di.unito.it/2022/02/04/i-fiori-di-sanremo/) songs! 

**Usage**
see the jupyter notebooks in `demos/` for examples of how to use emolib.

Authors: 

**ALFONSO SEMERARO**: University of Turin, ARC²S Group [🎓 ](https://scholar.google.it/citations?user=wrUG4-cAAAAJ) [🐦](https://twitter.com/AlfonsoSemeraro) <br/>
**SALVATORE VILELLA**: University of Turin, ARC²S Group [🎓 ](https://scholar.google.it/citations?user=zQFTgBEAAAAJ) [🐦](https://twitter.com/sal_vilella) <br/>
**GIANCARLO RUFFO**: University of Turin, ARC²S Group [🎓 ](https://scholar.google.it/citations?user=tTIeDa4AAAAJ) [🐦](https://twitter.com/giaruffo) <br/>
**MASSIMO STELLA**: University of Exeter, CogNosco Lab [🎓 ](https://scholar.google.it/citations?user=TUJkCbkAAAAJ) [🐦](https://twitter.com/MassimoSt) <br/>
13
