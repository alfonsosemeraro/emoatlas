#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  5 11:03:33 2021

@author: alfonso
"""
from resources import _load_spacy, _load_dictionary, _load_antonyms
import formamentis_edgelist as fme
import emo_scores as es
import baselines as bsl
import draw_plutchik as dp
from nltk.corpus import wordnet as wn

class EmoScores:
    
    def __init__(self, language = 'english', spacy_model = None, emotion_model = 'plutchik'):
        self.language = language
        self.spacy_model = _load_spacy(spacy_model, language)
        self.emotion_lexicon = _load_dictionary(language)
        self.emotion_lexicon = self.emotion_lexicon.groupby('word')['emotion'].apply(list).to_dict()
        self.antonyms = _load_antonyms(language)
        self.wn = wn
        
        if emotion_model == 'plutchik':
            self.emotionslist = ['anger', 'trust', 'surprise', 'disgust', 'joy', 'sadness', 'fear', 'anticipation']
            self.emotion_model = 'plutchik'
            
        self.baseline = None
        
        
        
    
        
        
    def set_baseline(self, baseline):
        """
        Set as a baseline emotion distribution the inputed baseline. 
        If no baseline is inputed, a new one will be created from the default emotion lexicon loaded.
        
        Required arguments:
        ----------
              
        *baseline*:
            Either a list of lists, a text, or None.
            If baseline is a list of list, it contains the distribution of emotions of the text used as baseline.
            If baseline is a text, a new emotion distribution will be computed from it.
            If baseline is None, it will be computed the emotion distribution of the default emotion lexicon loaded.
            
        """
        self.baseline = bsl._make_baseline(baseline, spacy_model = self.spacy_model, language = self.language)
        
        
        
    def baseline_distribution(self, emotionslist = None, emotion_model = 'plutchik', normalization_strategy = 'num_emotions'):
        """
        Gets the emotion distribution of the loaded baseline.
        
        Required arguments:
        ----------
              
        *emotionslist*:
            A list of emotions. Default is None.
       
        *emotion_model*:
            A model of emotions. Default is 'plutchik', that loads as emotions
                ['joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust', 'anger', 'anticipation']
            
        *normalization_strategy*:
            A string, whether to normalize emotion scores over the number of words. Accepted values are:
                'none': no normalization at all
                'text_lenght': normalize emotion counts over the total text length
                'emotion_words': normalize emotion counts over the number of words associated to an emotion
                
        Return:
        ----------
        A list of lists ?
            
        """
        return bsl._baseline_distribution(self.baseline, emotions = self.emotionslist, emotion_model = self.emotion_model, normalization_strategy = normalization_strategy)
        
    def formamentis_network(self, text, 
                             target_word = None,
                             keepwords = [],
                             stopwords = [],
                             antonyms = None,
                             max_distance = 3,
                             with_type = False):
        
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
            Limited support for other languages is available. By default, English will be loaded.
            
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
        
        if not antonyms:
            antonyms = self.antonyms
        
        return fme._get_formamentis_edgelist(text, language = self.language, 
                                            spacy_model = self.spacy_model, 
                                            target_word = target_word,
                                            keepwords = keepwords, 
                                            stopwords = stopwords, 
                                            antonyms = antonyms,
                                            wn = wn,
                                            max_distance = max_distance,
                                            with_type = with_type)
        
    def draw_formamentis(self, edgelist, language = None):
        
        """
        Draw the Formamentis network.
        
        Required arguments:
        ----------
              
        *edgelist*:
            A list of tuples. Each tuple is a couple of words connected into the Formamentis edgelist.
            
        """
        if not language:
            language = self.language
            
        fme._draw_formamentis(edgelist = edgelist, language = language)
        
        
        
    def valence(self, obj,
            emotion_lexicon = None, 
           normalization_strategy = 'none', 
           emotions = None, 
           language = None,
           spacy_model = None,
           duplicates = False,
           negation_strategy = 'ignore',
           negations = None,
           antonyms = None,
           method = 'default',
           target_word = None,
           emotion_model = 'plutchik'):
        
        """
        Count emotions in an inputed text or formamentis network.
        
        Required arguments:
        ----------
              
        *obj*:
            Either a string or a list of tuples, with the former being the text to extract emotion from, 
            and the latter being the standard representation of a formamentis edgelist.
            
        *emotion_lexicon*:
            A lexicon with every word-emotion association. By default, the NRCLexicon will be loaded.
        
        *normalization_strategy*:
            A string, whether to normalize emotion scores over the number of words. Accepted values are:
                'none': no normalization at all
                'text_lenght': normalize emotion counts over the total text length
                'emotion_words': normalize emotion counts over the number of words associated to an emotion
                
        *emotionslist*:
            A list of emotions. Default is None.
       
        *language*:
            Language of the text. Full support is offered for the languages supported by Spacy: 
                Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
                Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
            Limited support for other languages is available. By default, English will be loaded.
            
        *spacy_model*:
            Either a string or a spacy_model. If a string, it must be the name of a spacy model to load.
        
        *duplicates*:
            A boolean: if True, words associated with emotions will be counted as many times as they appear into the wordlist.
            If False, each word will be counted only once. Default is False.
            
        *negation_strategy*:
            A string, if words introduced by negations will be replaced by their antynomies.
            Default is 'ignore', for which no action will be done.
            Other values accepted are 'replace', i.e. words introduced by negations will be replaced,
            and 'delete', i.e. those words will be deleted.
        
        *antonyms*:
            A dict. For each word in the dict's keys, the correspondent value is its antynomy.
            Default is None: a pre-compiled dictionary will be loaded.
            
        *negations*:
            A custom-defined list of negations. 
            Default is None: a pre-compiled list will be loaded.
            
        *method*:
            A string, either 'default' or 'formamentis'. 
            If obj is a string and method is 'formamentis', the inputed text will be transformed into a formamentis network
            before extracting emotions.
            
        *target_word*:
            A string or None. If a string and method is 'formamentis', it will be computed the emotion distribution
            only of the neighborhood of 'target_word' in the formamentis network.
            
        *emotion_model*:
            A model of emotions. Default is 'plutchik', that loads as emotions
                ['joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust', 'anger', 'anticipation']
                
        Returns:
        ----------
        *emotions*:
            A dict. Keys are emotions, and values the scores.            
        """
        
        emotion_lexicon = self.emotion_lexicon if not emotion_lexicon else emotion_lexicon
        emotionslist = self.emotionslist if not emotions else emotions
        language = self.language if not language else language
        spacy_model = self.spacy_model if not spacy_model else spacy_model
        antonyms = self.antonyms if not antonyms else antonyms
        
        
        return es._valence(obj = obj, 
                       emotion_lexicon = emotion_lexicon, 
                       emotions = emotionslist, 
                       language = language,
                       spacy_model = spacy_model,
                       duplicates = duplicates,
                       negation_strategy = negation_strategy,
                       negations = negations,
                       antonyms = antonyms,
                       method = method,
                       target_word = target_word,
                       emotion_model = emotion_model)
                                 
        
    def emotions(self, obj, 
                       emotion_lexicon = None, 
                       normalization_strategy = 'none', 
                       emotionslist = None, 
                       language = None,
                       spacy_model = None,
                       duplicates = False,
                       negation_strategy = 'ignore',
                       negations = None,
                       antonyms = None,
                       method = 'default',
                       target_word = None,
                       emotion_model = 'plutchik'):
        
        """
        Count emotions in an inputed text or formamentis network.
        
        Required arguments:
        ----------
              
        *obj*:
            Either a string or a list of tuples, with the former being the text to extract emotion from, 
            and the latter being the standard representation of a formamentis edgelist.
            
        *emotion_lexicon*:
            A lexicon with every word-emotion association. By default, the NRCLexicon will be loaded.
        
        *normalization_strategy*:
            A string, whether to normalize emotion scores over the number of words. Accepted values are:
                'none': no normalization at all
                'text_lenght': normalize emotion counts over the total text length
                'emotion_words': normalize emotion counts over the number of words associated to an emotion
                
        *emotionslist*:
            A list of emotions. Default is None.
       
        *language*:
            Language of the text. Full support is offered for the languages supported by Spacy: 
                Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
                Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
            Limited support for other languages is available. By default, English will be loaded.
            
        *spacy_model*:
            Either a string or a spacy_model. If a string, it must be the name of a spacy model to load.
        
        *duplicates*:
            A boolean: if True, words associated with emotions will be counted as many times as they appear into the wordlist.
            If False, each word will be counted only once. Default is False.
            
        *negation_strategy*:
            A string, if words introduced by negations will be replaced by their antynomies.
            Default is 'ignore', for which no action will be done.
            Other values accepted are 'replace', i.e. words introduced by negations will be replaced,
            and 'delete', i.e. those words will be deleted.
        
        *antonyms*:
            A dict. For each word in the dict's keys, the correspondent value is its antynomy.
            Default is None: a pre-compiled dictionary will be loaded.
            
        *negations*:
            A custom-defined list of negations. 
            Default is None: a pre-compiled list will be loaded.
            
        *method*:
            A string, either 'default' or 'formamentis'. 
            If obj is a string and method is 'formamentis', the inputed text will be transformed into a formamentis network
            before extracting emotions.
            
        *target_word*:
            A string or None. If a string and method is 'formamentis', it will be computed the emotion distribution
            only of the neighborhood of 'target_word' in the formamentis network.
            
        *emotion_model*:
            A model of emotions. Default is 'plutchik', that loads as emotions
                ['joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust', 'anger', 'anticipation']
                
        Returns:
        ----------
        *emotions*:
            A dict. Keys are emotions, and values the scores.            
        """
        
        emotion_lexicon = self.emotion_lexicon if not emotion_lexicon else emotion_lexicon
        emotionslist = self.emotionslist if not emotionslist else emotionslist
        language = self.language if not language else language
        spacy_model = self.spacy_model if not spacy_model else spacy_model
        antonyms = self.antonyms if not antonyms else antonyms
        
        
        return es._count_emotions(obj = obj, 
                       emotion_lexicon = emotion_lexicon, 
                       normalization_strategy = normalization_strategy, 
                       emotions = emotionslist, 
                       language = language,
                       spacy_model = spacy_model,
                       duplicates = duplicates,
                       negation_strategy = negation_strategy,
                       negations = negations,
                       antonyms = antonyms,
                       method = method,
                       target_word = target_word,
                       emotion_model = emotion_model,
                       wn = self.wn).emotions
        
    
    def emotion_words(self, obj, 
                       emotion_lexicon = None, 
                       normalization_strategy = 'none', 
                       emotionslist = None, 
                       language = None,
                       spacy_model = None,
                       duplicates = False,
                       negation_strategy = 'ignore',
                       negations = None,
                       antonyms = None,
                       method = 'default',
                       target_word = None,
                       emotion_model = 'plutchik'):
        
        """
        Returns the words most associated to emotions in an inputed text or formamentis network.
        
        Required arguments:
        ----------
              
        *obj*:
            Either a string or a list of tuples, with the former being the text to extract emotion from, 
            and the latter being the standard representation of a formamentis edgelist.
            
        *emotion_lexicon*:
            A lexicon with every word-emotion association. By default, the NRCLexicon will be loaded.
        
        *normalization_strategy*:
            A string, whether to normalize emotion scores over the number of words. Accepted values are:
                'none': no normalization at all
                'text_lenght': normalize emotion counts over the total text length
                'emotion_words': normalize emotion counts over the number of words associated to an emotion
                
        *emotionslist*:
            A list of emotions. Default is None.
       
        *language*:
            Language of the text. Full support is offered for the languages supported by Spacy: 
                Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
                Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
            Limited support for other languages is available. By default, English will be loaded.
            
        *spacy_model*:
            Either a string or a spacy_model. If a string, it must be the name of a spacy model to load.
        
        *duplicates*:
            A boolean: if True, words associated with emotions will be counted as many times as they appear into the wordlist.
            If False, each word will be counted only once. Default is False.
            
        *negation_strategy*:
            A string, if words introduced by negations will be replaced by their antynomies.
            Default is 'ignore', for which no action will be done.
            Other values accepted are 'replace', i.e. words introduced by negations will be replaced,
            and 'delete', i.e. those words will be deleted.
        
        *antonyms*:
            A dict. For each word in the dict's keys, the correspondent value is its antynomy.
            Default is None: a pre-compiled dictionary will be loaded.
            
        *negations*:
            A custom-defined list of negations. 
            Default is None: a pre-compiled list will be loaded.
            
        *method*:
            A string, either 'default' or 'formamentis'. 
            If obj is a string and method is 'formamentis', the inputed text will be transformed into a formamentis network
            before extracting emotions.
            
        *target_word*:
            A string or None. If a string and method is 'formamentis', it will be computed the emotion distribution
            only of the neighborhood of 'target_word' in the formamentis network.
            
        *emotion_model*:
            A model of emotions. Default is 'plutchik', that loads as emotions
                ['joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust', 'anger', 'anticipation']
                
        Returns:
        ----------
        *emotions*:
            A dict. Keys are emotions, and values the scores.            
        """
        
        emotion_lexicon = self.emotion_lexicon if not emotion_lexicon else emotion_lexicon
        emotionslist = self.emotionslist if not emotionslist else emotionslist
        language = self.language if not language else language
        spacy_model = self.spacy_model if not spacy_model else spacy_model
        antonyms = self.antonyms if not antonyms else antonyms
        
        
        return es._emotion_words(obj = obj, 
                       emotion_lexicon = emotion_lexicon, 
                       normalization_strategy = normalization_strategy, 
                       emotions = emotionslist, 
                       language = language,
                       spacy_model = spacy_model,
                       duplicates = duplicates,
                       negation_strategy = negation_strategy,
                       negations = negations,
                       antonyms = antonyms,
                       method = method,
                       target_word = target_word,
                       emotion_model = emotion_model,
                       wn = self.wn)
                                 
                                 
                                 
    def zscores(self, obj, 
           language = None, 
           spacy_model = None,
           baseline = None, 
           emotion_lexicon = None, 
           duplicates = False, 
           negation_strategy = 'ignore', 
           antonyms = None, 
           negations = None, 
           n_samples = 300, 
           method = 'default',
           target_word = None,
           emotion_model = 'plutchik', 
           epsilon = 0.0):
        
        """
        Checks the emotion distribution in an inputed text or formamentis network against a baseline, and return the z-scores.
        
        Required arguments:
        ----------
              
        *obj*:
            Either a string or a list of tuples, with the former being the text to extract emotion from, 
            and the latter being the standard representation of a formamentis edgelist.
            
        *emotion_lexicon*:
            A lexicon with every word-emotion association. By default, the NRCLexicon will be loaded.
            
        *baseline*:
            Either a list of lists, a text, or None.
            If baseline is a list of list, it contains the distribution of emotions of the text used as baseline.
            If baseline is a text, a new emotion distribution will be computed from it.
            If baseline is None, it will be computed the emotion distribution of the default emotion lexicon loaded.
        
        *normalization_strategy*:
            A string, whether to normalize emotion scores over the number of words. Accepted values are:
                'none': no normalization at all
                'text_lenght': normalize emotion counts over the total text length
                'emotion_words': normalize emotion counts over the number of words associated to an emotion
                
        *emotionslist*:
            A list of emotions. Default is None.
       
        *language*:
            Language of the text. Full support is offered for the languages supported by Spacy: 
                Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
                Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
            Limited support for other languages is available. By default, English will be loaded.
            
        *spacy_model*:
            Either a string or a spacy_model. If a string, it must be the name of a spacy model to load.
        
        *duplicates*:
            A boolean: if True, words associated with emotions will be counted as many times as they appear into the wordlist.
            If False, each word will be counted only once. Default is False.
            
        *negation_strategy*:
            A string, if words introduced by negations will be replaced by their antynomies.
            Default is 'ignore', for which no action will be done.
            Other values accepted are 'replace', i.e. words introduced by negations will be replaced,
            and 'delete', i.e. those words will be deleted.
        
        *antonyms*:
            A dict. For each word in the dict's keys, the correspondent value is its antynomy.
            Default is None: a pre-compiled dictionary will be loaded.
            
        *negations*:
            A custom-defined list of negations. 
            Default is None: a pre-compiled list will be loaded.
            
        *method*:
            A string, either 'default' or 'formamentis'. 
            If obj is a string and method is 'formamentis', the inputed text will be transformed into a formamentis network
            before extracting emotions.
            
        *target_word*:
            A string or None. If a string and method is 'formamentis', it will be computed the emotion distribution
            only of the neighborhood of 'target_word' in the formamentis network.
            
        *emotion_model*:
            A model of emotions. Default is 'plutchik', that loads as emotions
                ['joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust', 'anger', 'anticipation']
                
        *n_samples*:
            An integer, how many time the baseline emotion distribution will be sampled before checking for z-scores.
            Default is 300.
            
                
        Returns:
        ----------
        *z-scores*:
            A dict. Keys are emotions, and values the z-scores.
            
        """
        
        language = self.language if not language else language
        spacy_model = self.spacy_model if not spacy_model else spacy_model
        emotion_lexicon = self.emotion_lexicon if not emotion_lexicon else emotion_lexicon
        emotion_model = self.emotion_model if not emotion_model else emotion_model
        antonyms = self.antonyms if not antonyms else antonyms
        
        if not baseline:
            if not self.baseline:
                self.baseline = bsl._make_baseline(language = language, emotions = self.emotionslist, spacy_model = spacy_model)
            baseline = self.baseline
        
        
        return es._zscores(obj, 
           language = language, 
           spacy_model = spacy_model,
           baseline = baseline, 
           emotion_lexicon = emotion_lexicon, 
           duplicates = duplicates, 
           negation_strategy = negation_strategy, 
           antonyms = antonyms, 
           negations = negations, 
           n_samples = n_samples, 
           method = method,
           target_word = target_word,
           emotion_model = emotion_model,
           wn = self.wn,
           epsilon = epsilon)
        
    
    def stats(self, obj, 
          emotion_lexicon = None,
          emotionslist = None, 
          language = None,
          spacy_model = None,
          duplicates = False,
          negation_strategy = 'ignore',
          negations = None,
          antonyms = None,
          method = 'default',
          target_word = None,
          emotion_model = 'plutchik'):
        
        """
        Checks the input text or formamentis network, and return a dict of statistics about words, emotions and negations.
        
        Required arguments:
        ----------
              
        *obj*:
            Either a string or a list of tuples, with the former being the text to extract emotion from, 
            and the latter being the standard representation of a formamentis edgelist.
            
        *emotion_lexicon*:
            A lexicon with every word-emotion association. By default, the NRCLexicon will be loaded.
                
        *emotionslist*:
            A list of emotions. Default is None.
       
        *language*:
            Language of the text. Full support is offered for the languages supported by Spacy: 
                Catalan, Chinese, Danish, Dutch, English, French, German, Greek, Japanese, Italian, Lithuanian,
                Macedonian, Norvegian, Polish, Portuguese, Romanian, Russian, Spanish.
            Limited support for other languages is available. By default, English will be loaded.
            
        *spacy_model*:
            Either a string or a spacy_model. If a string, it must be the name of a spacy model to load.
        
        *duplicates*:
            A boolean: if True, words associated with emotions will be counted as many times as they appear into the wordlist.
            If False, each word will be counted only once. Default is False.
            
        *negation_strategy*:
            A string, if words introduced by negations will be replaced by their antynomies.
            Default is 'ignore', for which no action will be done.
            Other values accepted are 'replace', i.e. words introduced by negations will be replaced,
            and 'delete', i.e. those words will be deleted.
        
        *antonyms*:
            A dict. For each word in the dict's keys, the correspondent value is its antynomy.
            Default is None: a pre-compiled dictionary will be loaded.
            
        *negations*:
            A custom-defined list of negations. 
            Default is None: a pre-compiled list will be loaded.
            
        *method*:
            A string, either 'default' or 'formamentis'. 
            If obj is a string and method is 'formamentis', the inputed text will be transformed into a formamentis network
            before extracting emotions.
            
        *target_word*:
            A string or None. If a string and method is 'formamentis', it will be computed the emotion distribution
            only of the neighborhood of 'target_word' in the formamentis network.
            
        *emotion_model*:
            A model of emotions. Default is 'plutchik', that loads as emotions
                ['joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust', 'anger', 'anticipation']
                
                
        Returns:
        ----------
        *z-scores*:
            A dict of statistics about words, emotions and negations in text.
            
        """
        
        language = self.language if not language else language
        spacy_model = self.spacy_model if not spacy_model else spacy_model
        emotion_lexicon = self.emotion_lexicon if not emotion_lexicon else emotion_lexicon
        emotion_model = self.emotion_model if not emotion_model else emotion_model
        
        return es._stats(obj, 
          emotion_lexicon = emotion_lexicon,
          emotions = self.emotionslist, 
          language = language,
          spacy_model = spacy_model,
          duplicates = duplicates,
          negation_strategy = negation_strategy,
          negations = negations,
          antonyms = antonyms,
          method = method,
          target_word = target_word,
          emotion_model = emotion_model,
          wn = self.wn)
        
        
    def draw_plutchik(self, scores,
             ax = None,
             rescale = False,
             reject_range = None, 
             highlight = 'all',
             show_intensity_levels = 'none', 
             font = None, 
             fontweight = 'light', 
             fontsize = 15, 
             show_coordinates = True,  
             show_ticklabels = False, 
             ticklabels_angle = 0, 
             ticklabels_size = 11, 
             height_width_ratio = 1, 
             title = None, 
             title_size = None):
        
        """
        Draw the emotions or dyads Plutchik flower.
        Full details at https://github.com/alfonsosemeraro/pyplutchik/blob/master/Documentation.md
        
        Required arguments:
        ----------
              
        *scores*:
            A dictionary with emotions or dyads. 
            For each entry, values accepted are a 3-values iterable (for emotions only) or a scalar value between 0 and 1.
            The sum of the 3-values iterable values must not exceed 1, and no value should be negative.
            See emo_params() and dyad_params() for accepted keys.
                    
            Emotions and dyads are mutually exclusive. Different kinds of dyads are mutually exclusive.
       
        *ax*:
            Axes to draw the coordinates.
            
        *rescale*:
            Either None or a 2-item tuple, with minimum and maximum value of the printable area.
            
        *reject_range*:
            A 2-item tuple. All petal scores that fall within the range must be considered non-interesting, thus drawed in grey.
            Default is None (no range at all).
            
        *highlight*:
            A string or a list of main emotions to highlight. If a list of emotions is given, other emotions will be shadowed. 
            Default is 'all'.
            
        *show_intensity_levels*:
            A string or a list of main emotions. It shows all three intensity scores for each emotion in the list, 
            and for the others cumulative scores. Default is 'none'.
            
        *font*:
            Font of text. Default is sans-serif.
            
        *fontweight*:
            Font weight of text. Default is light.
            
        *fontsize*:
            Font size of text. Default is 15.
            
        *show_coordinates*:
            A boolean, wether to show polar coordinates or not.
            
        *show_ticklabels*:
            Boolean, wether to show tick labels under Joy petal. Default is False.
            
        *ticklabels_angle*:
            How much to rotate tick labels from y=0. Value should be given in radians. Default is 0.
            
        *ticklabels_size*:
            Size of tick labels. Default is 11.
            
        *height_width_ratio*:
            Ratio between height and width of the petal. Lower the ratio, thicker the petal. Default is 1.
            
        *title*:
            Title for the plot.
            
        *title_size*:
            Size of the title. Default is font_size.
            
        Returns:
        ----------
        *ax*:
            The input Axes modified, if provided, otherwise a new generated one.     
            
        """
    
        dp._draw_plutchik(scores,
             ax = ax,
             rescale = rescale,
             reject_range = reject_range, 
             highlight = highlight,
             show_intensity_levels = show_intensity_levels, 
             font = font, 
             fontweight = fontweight, 
             fontsize = fontsize, 
             show_coordinates = show_coordinates,  
             show_ticklabels = show_ticklabels, 
             ticklabels_angle = ticklabels_angle, 
             ticklabels_size = ticklabels_size, 
             height_width_ratio = height_width_ratio, 
             title = title, 
             title_size = title_size)