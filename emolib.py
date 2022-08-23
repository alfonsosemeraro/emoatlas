"""
@author: alfonso.semeraro@unito.it

"""

from resources import _load_spacy, _load_dictionary, _load_emojis, _load_antonyms
import formamentis_edgelist as fme
import emo_scores as es
import baselines as bsl
import draw_plutchik as dp
from baselines import _load_lookup_table, _make_baseline
import matplotlib.pyplot as plt
import draw_formamentis_force as dff
import draw_formamentis_bundling as dfb


class EmoScores:
    
    def __init__(self, language = 'english', spacy_model = None, emotion_model = 'plutchik'):
        
        # Basic imports
        self.language = language
        self.emotion_lexicon = _load_dictionary(language)
        self.tagger = _load_spacy(language)
        self.emotionlist = None
        self.emojis_dict = _load_emojis(language)
        
        # Formamentis imports
        self.antonyms = _load_antonyms(language)        
        
        # Z-scores imports
        self.baseline = _make_baseline(language = self.language, emotion_lexicon = self.emotion_lexicon)
        self.lookup = _load_lookup_table(language = self.language)
        
        if emotion_model == 'plutchik':
            self.emotionslist = ['anger', 'trust', 'surprise', 'disgust', 'joy', 'sadness', 'fear', 'anticipation']
            self.emotion_model = 'plutchik'
        
        
        
        
    def set_baseline(self, baseline = None):
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
        self.baseline = bsl._make_baseline(baseline, emotion_lexicon = self.emotion_lexicon, tagger = self.tagger)
        self.lookup = {}
        
    
        
    def emotions(self, 
                 obj, 
                 normalization_strategy = 'none',
                 return_words = False,
                 convert_emojis = True):
        
        """
        Count emotions in an inputed text or formamentis network.
        
        Required arguments:
        ----------
              
        *obj*:
            Either a string or a list of tuples, with the former being the text to extract emotion from, 
            and the latter being the standard representation of a formamentis edgelist.
        
        *normalization_strategy*:
            A string, whether to normalize emotion scores over the number of words. Accepted values are:
                'none': no normalization at all
                'text_lenght': normalize emotion counts over the total text length
                'emotion_words': normalize emotion counts over the number of words associated to an emotion
                
       
                
        Returns:
        ----------
        *emotions*:
            A dict. Keys are emotions, and values the scores.            
        """
        
        
        return es._get_emotions(obj = obj, 
                       normalization_strategy = normalization_strategy, 
                       emotion_lexicon = self.emotion_lexicon, 
                       language = self.language,
                       tagger = self.tagger,
                       emotions = self.emotionslist,
                       return_words = return_words,
                       emojis_dict = self.emojis_dict,
                       convert_emojis = convert_emojis)
        
    
   
                                 
                                 
    def zscores(self, 
                obj,
                baseline = None,
                n_samples = 300,
                convert_emojis = True):
        
        """
        Checks the emotion distribution in an inputed text or formamentis network against a baseline, and return the z-scores.
        
        Required arguments:
        ----------
              
        *obj*:
            Either a string or a list of tuples, with the former being the text to extract emotion from, 
            and the latter being the standard representation of a formamentis edgelist.
            
            
        *baseline*:
            Either a list of lists, a text, or None.
            If baseline is a list of list, it contains the distribution of emotions of the text used as baseline.
            If baseline is a text, a new emotion distribution will be computed from it.
            If baseline is None, it will be computed the emotion distribution of the default emotion lexicon loaded.
        
        *n_samples*:
            An integer, how many time the baseline emotion distribution will be sampled before checking for z-scores.
            Default is 300.
                
        Returns:
        ----------
        *z-scores*:
            A dict. Keys are emotions, and values the z-scores.
            
        """
        
        
        if not baseline:
            if not self.baseline:
                self.baseline = bsl._make_baseline(baseline = None, tagger = self.tagger, language = self.language, emotion_lexicon = self.emotion_lexicon)
            baseline = self.baseline
        else:
            baseline = bsl._make_baseline(baseline = baseline, tagger = self.tagger, language = self.language, emotion_lexicon = self.emotion_lexicon)
            
        
        
        return es._zscores(obj, 
                           baseline = baseline,
                           n_samples = n_samples,
                           emotion_lexicon = self.emotion_lexicon,
                           language = self.language,
                           tagger = self.tagger,
                           emotions = self.emotionslist,
                           lookup = self.lookup,
                           emojis_dict = self.emojis_dict,
                           convert_emojis = convert_emojis)
        
  
    def formamentis_network(self, 
                            text,
                            target_word = None,
                            keepwords = [],
                            stopwords = [],
                            max_distance = 3,
                            with_type = False
                         ):
        """
        FormaMentis edgelist from input text.
        
        Required arguments:
        ----------
              
        *text*:
            A string, the text to extract emotions from.
            
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
        
        
        
        return fme.get_formamentis_edgelist(text, 
                                     language = self.language, 
                                     spacy_model = self.tagger,
                                     target_word = target_word,
                                     keepwords = keepwords,
                                     stopwords = stopwords,
                                     antonyms = self.antonyms,
                                     max_distance = max_distance,
                                     with_type = with_type
                                     )
        
    
    def draw_formamentis(self, fmn, layout = 'edge_bundling', highlight = [], ax = None):
        
        if layout == 'force_layout':
            dff.draw_formamentis_force_layout(fmn.edges, highlight = highlight, language = self.language, ax = ax)
        elif layout == 'edge_bundling':
            dfb.draw_formamentis_circle_layout(fmn, highlight = highlight, language = self.language, ax = ax)
            
        
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
    
        dp.draw_plutchik(scores,
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
        
        
        