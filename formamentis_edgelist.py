#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 18:00:50 2021

@author: alfonso
"""

import networkx as nx
import itertools
from textloader import _clean_text, multiple_replace
from language_dependencies import _negations, _pronouns, _language_code3, _valences
import re
import matplotlib.pyplot as plt
from nltk.corpus import wordnet as wn
from collections import namedtuple


def _wordnet_synonyms(vertexlist, language, with_type = False):
    """
    1. For each word `i` in vertexlist, get all synonims `S_i`
    2. For each pair of word in vertexlist that are synonims, draw an edge
       like (i, j \in S_i)
    """
    lang = _language_code3(language)
    if not lang:
        return []
    
#    L = len(edgelist)
    synonims_list = [list(set(itertools.chain(*[w.lemma_names(lang) for w in wn.synsets(x, lang = lang)]))) for x in vertexlist]
    synonims_pairs = [list(itertools.combinations(syn, 2)) for syn in synonims_list if len(syn) > 0]
    
    synonims_pairs = [[(a, b) for (a, b) in w if a in vertexlist and b in vertexlist] for w in synonims_pairs]
    synonims_pairs = list(set(itertools.chain(*synonims_pairs)))
    
    if with_type:
        synonims_pairs = [(a, b, 'synonyms') for a, b in synonims_pairs]
        
        
    synonims_pairs

    return synonims_pairs       


def _wordnet_hypernyms(vertexlist, language, with_type = False):
    """
    1. For each word `i` in vertexlist, get all hypernyms `S_i`
    2. For each pair of word in vertexlist that are hypernyms and synonyms, draw an edge
       like (i, j \in S_i)
    """
    lang = _language_code3(language)
    if not lang:
        return []
    
    hypernyms_pairs = []
    
    for vertex in vertexlist:
        hyp_list = [a for a in itertools.chain(*[[hyp.lemma_names(lang) for hyp in ss.hypernyms()] for ss in wn.synsets(vertex, lang = lang)])]
        hyp_pairs = list(set([(vertex, hyp) for hyp in itertools.chain(*hyp_list)]))
        hyp_pairs = [(a, b) for a, b in hyp_pairs if a != b and a in vertexlist and b in vertexlist]
        
        hypernyms_pairs.extend(hyp_pairs)
        
    if with_type:
        hypernyms_pairs = [(a, b, 'hypernyms') for a, b in hypernyms_pairs]
        
    return hypernyms_pairs   

    
# remove duplicates
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


# Finds tokens to be negated
def handle_negations(tokens):
    negations = [token for token in tokens if token.dep_ == 'neg']
    
    tonegate = []
    
    for neg in negations:
        head = neg.head
        children = [x for x in head.children if 'comp' in x.dep_]
        tonegate += [child.lemma_ for child in children]
        
        for child in children:
            grandchildren = [gc for gc in child.children]
            if not any([gc.text == 'but' for gc in grandchildren]):
                grandchildren = [gc.lemma_ for gc in grandchildren if gc.dep_ == 'conj']
                tonegate += grandchildren
    
    negations = [neg.lemma_ for neg in negations]
    
    return negations, tonegate


# Replace negated words
def replace_antonyms(lemma, negate_lemmas, antonyms):
    
    if lemma in negate_lemmas:
        idx, lm = lemma.split('__')
        if lm in antonyms:
            lemma = idx + '__' + antonyms[lm]
        else:
            lemma = idx + '__' + 'not-' + lm
    
    return lemma

    
def _get_edges_vertex(text, spacy_model, stemmer = None, stem_or_lem = 'lemmatization', language = 'english', keepwords = [], stopwords = [], antonyms = {}, wn = None, max_distance = 3, semantic_enrichment = '', with_type = False):
    """ Get an edgelist, with also stopwords in it, and a vertex list with no stopwords in it. """
    
    
    if stem_or_lem == 'stemming' and stemmer is None:
        raise Exception("Value Error: Stemming was requested instead of lemmatization, but no stemmer was initialized. Please run set_stemming_lemmatization('stemming') before trying again.")
    
    edgelist = []
    vertexlist = []

#     keeptags = ['JJ', 'JJR', 'JJS', 'CD', 'PRP', 'NN', 'NNS', 'FW', 'NNP', 'NNPS', 'PDT', 'RB', 'RBR', 
#                 'RBS', 'RP', 'VB', 'VBZ', 'VBP', 'VBD', 'VBN', 'VBG'] # this goes with .tag_
    keeppos = ['VERB', 'AUX', 'NOUN', 'PROPN', 'ADJ', 'NUM', 'PRON', 'ADV'] # this goes with .pos_
    
    # Getting or using spacy model
    nlp = spacy_model
    
    # get sentences
    nlp.create_pipe('sentencizer')
    sentences = nlp(text).sents
    

    for sentence in sentences:
        
        sent_edges = []
        sent_vertex = []
        
        # tokenize sentence
        tokens = [token for token in nlp(sentence.text)]
        for i, token in enumerate(tokens):
            token.lemma_ = '{}__'.format(i) + token.lemma_
            
            
        # some tokens must be negated!
        negations_lemmas, negate_lemmas = handle_negations(tokens)
                
        for token in tokens:
            
            #is it a negation? skip it
            if token.lemma_ in negations_lemmas:
                continue
            
            # a pair <word, parent_word> unless word is ROOT
            if token.dep_ != 'ROOT':
                sent_edges += [(token.head.lemma_, token.lemma_)]
            
            # should you keep the word? Yes if it is in keeppos or it is a negation or a pronoun
            keep = (token.pos_ in keeppos)
            # reasons to overtake on keep
            nokeep = (token.text in stopwords) or (token.is_stop) or len(token.text) <= 2 or bool(re.search('[0-9]', token.text))
            # reasons to overtake on everything
            yakeep = (token.text in keepwords) or  (token.text in _pronouns[language])  
            # old implementation            
            # yakeep = (token.text in keepwords) or (token.text in _negations[language]) or (token.text in _pronouns[language])  
            
            if (keep and not nokeep) or yakeep:
                sent_vertex += [token.lemma_]
                
        # all the lemmas we kept from the sentence
        sent_vertex = list(set(sent_vertex)) # there are NO stopwords in the vertex list.
        
        # all possible pairs of edges between syntactically dependent words - no matter if we kept them!
        sent_edges = f7(sent_edges) # there are stopwords in the edgelist!
        
        # only edges between words at distance < threshold
        sent_edges, sent_vertex = _get_network(sent_edges, sent_vertex, max_distance)     
        
        # Replace antonyms
        if negate_lemmas:
            sent_vertex = [replace_antonyms(word, negate_lemmas, antonyms) for word in sent_vertex]
            sent_edges = [(replace_antonyms(a, negate_lemmas, antonyms), replace_antonyms(b, negate_lemmas, antonyms)) for a,b in sent_edges]
        
        
        # stemming?
        if stem_or_lem == 'stemming':
            sent_vertex = [stemmer.stem(word) for word in sent_vertex]
            sent_edges = [(stemmer.stem(a), stemmer.stem(b)) for a, b in sent_edges]
        
        # with type?
        if with_type:
            sent_edges = [(a, b, 'syntactic') for a, b in sent_edges]
        
        # add this sentence's words and edges to global
        edgelist += sent_edges
        vertexlist += sent_vertex


    # remove indexes and add type
    if with_type:
        edgelist = [(a.split('__')[1], b.split('__')[1], c) for a, b, c in edgelist]
    else:
        edgelist = [(a.split('__')[1], b.split('__')[1]) for a, b in edgelist]
        
    
    # remove indexes
    vertexlist = list(set([vertex.split('__')[1] for vertex in vertexlist]))
    
    
    # add synonims
    if semantic_enrichment == 'synonyms' or 'synonyms' in semantic_enrichment:
        syn_edges = _wordnet_synonyms(vertexlist, language, with_type)
        edgelist.extend(syn_edges)
        
    # add hypernyms
    if semantic_enrichment == 'hypernyms' or 'hypernyms' in semantic_enrichment:
        hyp_edges = _wordnet_hypernyms(vertexlist, language, with_type)
        edgelist.extend(hyp_edges)
    
    # unique edges and no self-loops
    if with_type:
        edgelist.extend([(b, a, c) for a, b, c in edgelist])
        edgelist = [(a, b, c) for a, b, c in edgelist if a < b]
    else:
        edgelist.extend([(b, a) for a, b in edgelist])
        edgelist = [(a, b) for a, b in edgelist if a < b]
        
    edgelist = f7(edgelist)
    
    
    return edgelist, vertexlist


    
def _get_network(edges, vertex, max_distance = 3):
    """ Builds a graph from the edgelist, keeps only pairs of vertex that:
        - are at maximum distance of `max_distance` links
        - are both in the vertex list
    """

    G = nx.Graph(edges)

#     spl = nx.all_pairs_shortest_path_length(G, cutoff = max_distance)
#     print(dict(spl))
    spl = nx.all_pairs_shortest_path_length(G, cutoff = max_distance)

    # spl is {source: {target: distance}, ... }
    # must check that: 
    # 1. source != target
    # 2. source in vertex, target in vertex
    # 3. distance <= max_distance
    edges = [[(source, target) for target, distance in path.items() if (1 <= distance <= max_distance) and (target in vertex)] for source, path in dict(spl).items() if source in vertex]
    
    # unlist
    edges = list(itertools.chain(*edges))
    
    # list of lists of tuples (a, b), where a < b, no duplicates
    edges = [(a, b) for a, b in edges if a < b]
        
    
    return edges, vertex
    

    
def get_formamentis_edgelist(text, 
                             language = 'english', 
                             spacy_model = 'en_core_web_sm',
                             stemmer = None,
                             stem_or_lem = 'lemmatization',
                             target_word = None,
                             keepwords = [],
                             stopwords = [],
                             antonyms = None,
                             max_distance = 3,
                             semantic_enrichment = 'synonyms',
                             multiplex = False,
                             idiomatic_tokens = None
                             ):
    """
    FormaMentis edgelist from input text.
    
    Required arguments:
    ----------
          
    *text*:
        A string, the text to extract emotions from.
   
    *language*:
        Language of the text. Full support is offered for the languages supported by Spacy: 
            Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
            Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
        Limited support for other languages is available.
        
    *target_word*:
        A string or None. If a string and method is 'formamentis', it will be computed the emotion distribution
        only of the neighborhood of 'target_word' in the formamentis network.
        
    *keepwords*:
        A list. Words that shall be included in formamentis networks regardless from their part of speech. Default is an empty list.
        By default implementation, a pre-compiled list of negations and pronouns will be loaded and used as keepwords.
        
    *stopwords*:
        A list. Words that shall be discarded from formamentis networks regardless from their part of speech. Default is an empty list.
        If a word is both in stopwords and in keepwords, the word will be discarded.
        
    *max_distance*:
        An integer, by default 2. Links in the formamentis network will be established from each word to each neighbor within a distance
        defined by max_distance.
        
     *semantic_enrichment*:
        A str or a list of str. If 'synonyms', will be added semantic arcs between synonyms into the network. If 'hypernyms', will be
        added semantic arcs between hypernyms and hyponyms. Also ['synonyms', 'hypernyms'] is accepted.
        
    *multiplex*:
        A bool: whether to return different edgelist for different kinds of edges (syntactic, synonyms, hypernyms) or not. Default is False.
           
        
    Returns:
    ----------
    *edges*:
        A list of 2-items tuples, defining the edgelist of the formamentis network. If multiplex is True,
        it returns a dictionary with syntactic and semantic edges separately.
    
    *vertex*:
        A list of string, defining the list of vertices of the network.
        
    """
    
    # semantic_enrichment must be either a string in ['synonyms', 'hypernyms']
    accepted_values = ['synonyms', 'hypernyms', '']
    
    if type(semantic_enrichment) == str and semantic_enrichment not in accepted_values:
        wrong = [val for val in semantic_enrichment if val not in accepted_values][0]
        raise Exception(f"Value Error: wrong value '{wrong}' for semantic enrichment: it must be either 'synonyms', 'hypernyms' or empty, or any combination of the above.")
    elif semantic_enrichment is None:
        semantic_enrichment = ''
    elif type(semantic_enrichment) == list and any([val not in accepted_values for val in semantic_enrichment]):
        wrong = [val for val in semantic_enrichment if val not in accepted_values][0]
        raise Exception(f"Value Error: wrong value '{wrong}' for semantic enrichment: it must be either 'synonyms', 'hypernyms' or empty, or any combination of the above.")
    
    
    text = _clean_text(text)
    
    with_type = multiplex
        
        
    edges, vertex = _get_edges_vertex(text = text, spacy_model = spacy_model, 
                                      stemmer = stemmer, stem_or_lem = stem_or_lem, 
                                      language = language, 
                                      keepwords = keepwords, stopwords = stopwords, 
                                      antonyms = antonyms,
                                      max_distance = max_distance,
                                      semantic_enrichment = semantic_enrichment,
                                      with_type = with_type)
    
    
    # target words!
    if target_word:
        neighbors = list(set(list(itertools.chain(*[e for e in edges if target_word in e]))))
        
        if with_type:
            edges = [(a, b, c) for a, b, c in edges if a in neighbors and b in neighbors]
            vertex = list(set.union(set([a for a, _, _ in edges]), set([b for _, b, _ in edges])))
        else:
            edges = [(a, b) for a, b in edges if a in neighbors and b in neighbors]
            vertex = list(set.union(set([a for a, _ in edges]), set([b for _, b in edges])))
            
    # should we return a dictionary?
    if multiplex:
        edgelist = {}
        edgelist['syntactic'] = [(a, b) for a, b, c in edges if c == 'syntactic']
        if 'synonyms' == semantic_enrichment or 'synonyms' in semantic_enrichment:
            edgelist['synonyms'] = [(a, b) for a, b, c in edges if c == 'synonyms']
        if 'hypernyms' == semantic_enrichment or 'hypernyms' in semantic_enrichment:
            edgelist['hypernyms'] = [(a, b) for a, b, c in edges if c == 'hypernyms']
        edges = edgelist
        
        
    FormamentisNetwork = namedtuple('FormamentisNetwork', 'edges vertices')
    return FormamentisNetwork(edges, vertex)


def draw_formamentis(edgelist, language = 'english', ax = None):
    """
    
    """
    
    # Get the network
    M = nx.MultiGraph()
    M.add_edges_from(edgelist)
    
    try:
        _ = edgelist[0][2]
        color = ['blue' if t[2] == 'syntactic' else 'red' for t in edgelist]
    except:
        color = ['grey' for _ in range(len(edgelist))]
    
    # Get positive or negative valences
    _positive, _negative, _ambivalent = _valences(language)
    
    # Prepare the patch effect for bicolor patches
    import matplotlib.patheffects as path_effects
    eff = [path_effects.PathPatchEffect(facecolor='white', edgecolor = 'red', linewidth = 2),
    path_effects.PathPatchEffect(edgecolor='green', linewidth=2.1, facecolor=(0, 0, 0, 0), linestyle = '--')]
    
    
    if not ax:
        _, ax = plt.subplots(figsize=(9,9)) 
    
    
    pos = nx.spring_layout(M)
    nx.draw_networkx(M, pos = pos, node_size = 0, with_labels = False, font_size=12, edge_color=color, width=3.5, alpha = 0.5)
    for key, val in pos.items():
        
        if key in _positive:
            plt.annotate(s = key, xy = (val[0], val[1]),
                    bbox=dict(boxstyle='round', fc='white', ec= 'green', linewidth = 4))

        if key in _negative:
            plt.annotate(s = key, xy = (val[0], val[1]),
                    bbox=dict(boxstyle='round', fc='white', ec= 'red', linewidth = 4))


        if key in _ambivalent:
            plt.annotate(s = key, xy = (val[0], val[1]),
                    bbox=dict(boxstyle='round', fc='white', ec=(119/255, 221/255, 118/255, .7), path_effects = eff, linewidth = 1))
        else:
            plt.annotate(s = key, xy = (val[0], val[1]),
                    bbox=dict(boxstyle='round', fc='white', ec = 'grey', linewidth = 1))
    ax.axis('off')