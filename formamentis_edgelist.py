#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 18:00:50 2021

@author: alfonso
"""

import networkx as nx
import itertools
from textloader import _clean_text
from language_dependencies import _negations, _pronouns, _language_code3, _valences
import re
import matplotlib.pyplot as plt
from nltk.corpus import wordnet as wn
from collections import namedtuple


def _wordnet_synonims(vertexlist, edgelist, language, with_type = False):
    """
    1. For each word `i` in vertexlist, get all synonims `S_i`
    2. For each pair of word in vertexlist that are synonims, draw an edge
       like (i, j \in S_i)
    """
    lang = _language_code3(language)
    if not lang:
        return edgelist
    
#    L = len(edgelist)
    synonims_list = [list(set(itertools.chain(*[w.lemma_names(lang) for w in wn.synsets(x, lang = lang)]))) for x in vertexlist]
    synonims_pairs = [list(itertools.combinations(syn, 2)) for syn in synonims_list if len(syn) > 0]
    
    synonims_pairs = [[(a, b) for (a, b) in w if a in vertexlist and b in vertexlist] for w in synonims_pairs]
    synonims_pairs = list(set(itertools.chain(*synonims_pairs)))
    
    if with_type:
        synonims_pairs = [(a, b, 'semantic') for a, b in synonims_pairs]
    edgelist += synonims_pairs

    return edgelist    
    

def _get_edges_vertex(text, spacy_model, language = 'english', keepwords = [], stopwords = [], antonyms = {}, wn = None, max_distance = 3, with_type = False):
    """ Get an edgelist, with also stopwords in it, and a vertex list with no stopwords in it. """
    
    
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
        negations_lemmas = []
        to_negate = []
    
        # tokenize sentence
        tokens = [(index, token) for index, token in enumerate(nlp(sentence.text))]
        for i, token in tokens:
            token.lemma_ = '{}__'.format(i) + token.lemma_
        tokens = [token for _, token in tokens]    
        
        for token in tokens:
                        
            #lemmatization
            stem = token.lemma_
            stem_head = token.head.lemma_
            
            #is it a negation?
            if token.text in _negations[language]:
                negations_lemmas += [token.lemma_, token.text]
                
            # a pair < word, parent_word > unless word is ROOT
            if token.dep_ != 'ROOT':
                sent_edges += [(stem, stem_head)]
            
            # add edges with negated words (negation is parent)
            if token.head.text in negations_lemmas:
                num, ss = stem.split('__')
                
                if ss in antonyms.keys():
                    sent_edges += [(num + '__' + antonyms[ss], stem)]
                    to_negate += [stem]
                    
            # add edges with negated words (negation is children)
            if token.text in negations_lemmas:
                num, ss = stem_head.split('__')
                
                if ss in antonyms.keys():
                    sent_edges += [(num + '__' + antonyms[ss], stem_head)]
                    to_negate += [stem_head]
                
            # should you keep the word? Yes if it is in keeppos or it is a negation or a pronoun
            keep = (token.pos_ in keeppos)
            # reasons to overtake on keep
            nokeep = (token.text in stopwords) or (token.is_stop) or len(token.text) <= 2 or bool(re.search('[0-9]', token.text))
            # reasons to overtake on everything
            yakeep = (token.text in keepwords) or (token.text in _negations[language]) or (token.text in _pronouns[language])  
            
            if (keep and not nokeep) or yakeep:
                sent_vertex += [stem]
                
                # add negated words to vertex
                if stem in to_negate:
                    num, ss = stem.split('__')
                    if ss in antonyms.keys():
                        sent_vertex += [num + '__' + antonyms[ss]]
                                                
                        
        sent_vertex = list(set(sent_vertex)) # there are NO stopwords in the vertex list.
        sent_edges = list(set(sent_edges)) # there are stopwords in the edgelist!
        
        #print([edge for edge in sent_edges if any([nl in edge for nl in negations_lemmas])])
        
        sent_edges, sent_vertex = _get_network(sent_edges, sent_vertex, max_distance, with_type)        
        edgelist += sent_edges
        vertexlist += sent_vertex

    
    if with_type:
        edgelist = [(a.split('__')[1], b.split('__')[1], c) for a, b, c in edgelist]
    else:
        edgelist = [(a.split('__')[1], b.split('__')[1]) for a, b in edgelist]

    vertexlist = list(set([vertex.split('__')[1] for vertex in vertexlist]))
    edgelist = _wordnet_synonims(vertexlist, edgelist, language, with_type)
    edgelist = list(set(edgelist))
    
    
    
    return edgelist, vertexlist


    
def _get_network(edges, vertex, max_distance = 3, with_type = False):
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
    if with_type:
        edges = [[(source, target, 'syntactic') for target, distance in path.items() if (1 <= distance <= max_distance) and (target in vertex)] for source, path in dict(spl).items() if source in vertex]
    else:
        edges = [[(source, target) for target, distance in path.items() if (1 <= distance <= max_distance) and (target in vertex)] for source, path in dict(spl).items() if source in vertex]
    
    # unlist
    edges = list(itertools.chain(*edges))
    
    # list of lists of tuples (a, b), where a < b, no duplicates
    if with_type:
        edges = [(a, b, c) for a, b, c in edges if a < b]
    else:
        edges = [(a, b) for a, b in edges if a < b]
        
    return edges, vertex
    

    
def get_formamentis_edgelist(text, 
                             language = 'english', 
                             spacy_model = 'en_core_web_sm',
                             target_word = None,
                             keepwords = [],
                             stopwords = [],
                             antonyms = None,
                             max_distance = 3,
                             with_type = False,
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
        
    *with_type*:
        A boolean. If True, each edge will come with an attribute that tells if the edge is syntactic or semantic. 
        Default is False
        
    Returns:
    ----------
    *edges*:
        A list of 2-items tuples, defining the edgelist of the formamentis network.
    
    *vertex*:
        A list of string, defining the list of vertices of the network.
        
    """
    
    
    text = _clean_text(text)
        
    edges, vertex = _get_edges_vertex(text = text, spacy_model = spacy_model, language = language, 
                                      keepwords = keepwords, stopwords = stopwords, 
                                      antonyms = antonyms,
                                      max_distance = max_distance, 
                                      with_type = with_type)
    
    # TODO: synonims from WordNet
    print("BEFORE:", edges)
    edges = _wordnet_synonims(vertex, edges, language, with_type)
    print("AFTER:", edges)
    
    # target words!
    if target_word:
        neighbors = list(set(list(itertools.chain(*[e for e in edges if target_word in e]))))
        
        if with_type:
            edges = [(a, b, c) for a, b, c in edges if a in neighbors and b in neighbors]
        else:
            edges = [(a, b) for a, b in edges if a in neighbors and b in neighbors]
            
        vertex = list(set.union(set([a for a, _ in edges]), set([b for _, b in edges])))
    
    
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