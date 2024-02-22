<img src="ea.png" data-canonical-src="ea.png" width="200" height="200" />

A Python library for the detection and visualization of emotions in texts, coming soon with the first release ✨


## Description

EmoAtlas is a Python library that checks against the input text, after having enriched it and structured as a semantic network, against the multilingual [NRC Lexicon](https://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm). The library is built upon the [Formamentis Networks](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0222870) from Stella et al. and the [PyPlutchik library](https://www.github.com/alfonsosemeraro/pyplutchik) (paper [here](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0256503)).

![](fig1_1500.png)

It has already been used for our analysis of the [semantic and emotional frames around COVID-19 vaccines](https://arxiv.org/abs/2201.07538), repository [here](https://github.com/alfonsosemeraro/vaccines-and-press).

## Installation
emolib installs with pip:

```
~$ pip install git+https://github.com/alfonsosemeraro/emoatlas
```
then install the relevant language using:

```
~$ python -m spacy download en_core_web_lg
```
the command above installs English, but a list of possible language codes can be found [here](https://spacy.io/usage/models), and different languages installed by changing `en` in the final argument to one of the listed language codes. 


## Usage
See the Jupyter notebooks in `demos/` for examples of how to use emoatlas ([Jupyter notebook](https://github.com/jupyter/notebook) required). Guides and other information on the package are also available in that folder.

#### Google Colab
A Google Colab simple demo is also available [here](https://colab.research.google.com/drive/1qzymy0-5EXv3E6dQ0c_D3mv8tyvjSduX?usp=sharing).

## Acknowledgements
Thanks to [@FinleyGibson](https://github.com/FinleyGibson) and [@GiulioRossetti](https://github.com/GiulioRossetti) for their contribution to the testing, debugging and refactoring this library.
