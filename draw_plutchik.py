
"""
**********
Plutchik
**********

This package contains a data visualization tool for corpora annotated with emotions.
Given a JSON representation of the Plutchik's emotions (or dyads) in a text or in a group of texts, 
it draws the corresponding Plutchik's flower.

See Plutchik, Robert. "A general psychoevolutionary theory of emotion." Theories of emotion. Academic press, 1980. 3-33.

--------
repository available at https://www.github.com/alfonsosemeraro/pyplutchik
@author: Alfonso Semeraro <alfonso.semeraro@gmail.com>

"""

import shapely.geometry as sg
import matplotlib.pyplot as plt
import descartes
from math import cos, sin, radians
import numpy as np
import emotions as _emo_pluthick_
import dyads as _dyads_pluthick_

__author__ = """Alfonso Semeraro (alfonso.semeraro@gmail.com)"""
__all__ = ['_rotate_point',
           '_polar_coordinates',
           '_neutral_central_circle',
           '_check_scores_kind',
           '_draw_plutchik',
           '_get_random_emotions',
           '_get_random_dyads']







def _rotate_point(point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    Required arguments:
    ----------
    *point*:
        A two-values tuple, (x, y), of the point to rotate
        
    *angle*:
        The angle the point is rotated. The angle should be given in radians.
    
    Returns:
    ----------
    *(qx, qy)*:
        A two-values tuple, the new coordinates of the rotated point.     
        
    """
    ox, oy = 0, 0
    px, py = point
    angle = radians(angle)
    qx = ox + cos(angle) * (px - ox) - sin(angle) * (py - oy)
    qy = oy + sin(angle) * (px - ox) + cos(angle) * (py - oy)
    return (qx, qy)




def _polar_coordinates(ax, font, fontweight, fontsize, show_ticklabels, ticklabels_angle, ticklabels_size, rescale, all_ticks = True, offset = .15):
    """
    Draws polar coordinates as a background.

    Required arguments:
    ----------
    *ax*:
        Axes to draw the coordinates.
        
    *font*:
        Font of text. Default is Montserrat.
        
    *fontweight*:
        Font weight of text. Default is light.
        
    *fontsize*:
        Font size of text. Default is 15.
        
    *show_ticklabels*:
        Boolean, wether to show tick labels under Joy petal. Default is False.
        
    *ticklabels_angle*:
        How much to rotate tick labels from y=0. Value should be given in radians. Default is 0.
        
    *ticklabels_size*:
        Size of tick labels. Default is 11.
        
    *all_ticks*:
        A boolean: wether underneath polar lines must be drawed or not.
        
    *offset*:
        Central neutral circle has radius = .15, and coordinates must start from there.
    
    Returns:
    ----------
    *ax*:
        The input Axes modified.     
        
    """
    
    rg = range(0, 110, 20) if all_ticks else [100]
    
    # Lines
    for i in rg:
        c = plt.Circle((0, 0), offset + i/100, color = 'grey', alpha = .3, fill = False, zorder = -20)
        ax.add_artist(c)

    if rescale:
        true_values = list(np.arange(rescale[0], rescale[1], (rescale[1]-rescale[0])/5)) + [rescale[1]]
        true_values = true_values[-5:]
        
    else:
        true_values = np.arange(0.2, 1.2, .2)
        
    # Tick labels
    if show_ticklabels:
        for x, tv in zip(np.arange(0.2, 1.2, .2), true_values):
            a = '+{}'.format(round(tv, 1)) if tv >= 0 else str(round(tv,1))
            x, y = _rotate_point((0, x + offset), ticklabels_angle) #-.12
            ax.annotate(s = a, xy = (x, y),  fontfamily = font, size = ticklabels_size, fontweight = fontweight, zorder = 8, rotation = ticklabels_angle)
    return ax


def _neutral_central_circle(ax, r = .15):
    """
    Draws central neutral circle (in grey).

    Required arguments:
    ----------
    *ax*:
        Axes to draw the coordinates.
        
    *r*:
        Radius of the circle. Default is .15.
        
    Returns:
    ----------
    *ax*:
        The input Axes modified.     
        
    """
    c = sg.Point(0, 0).buffer(r)
    ax.add_patch(descartes.PolygonPatch(c, fc='white', ec=(.5, .5, .5, .3), alpha=1, zorder = 15))
    
    return ax
    



    

def _check_scores_kind(tags):
    """
    Checks if the inputed scores are all of the same kind 
    (emotions or primary dyads or secondary dyads or tertiary dyads or opposites).
    
    No mixed kinds are allowed.
    
    Required arguments:
    ----------
          
    *tags*:
        List of the tags provided as 'scores'.
        
        
    Returns:
    ----------
    
    A boolean, True if `scores` contains emotions, False if it contains dyads.
    
    """
    kinds = []
    for t in tags:
        try:
            kinds += [_emo_pluthick_.emo_params(t)[2]]
        except:
            kinds += [_dyads_pluthick_.dyad_params(t)[3]]

    unique_kinds = list(set(sorted(kinds)))
    
    if len(unique_kinds) > 1:
        unique_kinds_str = ', '.join([str(a) for a in unique_kinds])
        unique_kinds_str = unique_kinds_str.replace('0', 'emotions')
        unique_kinds_str = unique_kinds_str.replace('1', 'primary dyads')
        unique_kinds_str = unique_kinds_str.replace('2', 'secondary dyads')
        unique_kinds_str = unique_kinds_str.replace('3', 'tertiary dyads')
        unique_kinds_str = unique_kinds_str.replace('4', 'opposite emotions')
        unique_kinds_str = ' and'.join(unique_kinds_str.rsplit(',', 1))
                
        error_str = "Bad input: can't draw {} altogether. Please input only one of them as 'scores'.".format(unique_kinds_str)
        raise Exception(error_str)
        
    else:
        
        kind = kinds[0]
        
        if kind == 0:
            return True
        else:
            return False
        
        
def _check_scores_list_kind(tags_list):
    """
    Checks if the inputed scores are all of the same kind 
    (emotions or primary dyads or secondary dyads or tertiary dyads or opposites).
    
    No mixed kinds are allowed.
    
    Required arguments:
    ----------
          
    *tags_list*:
        List of the emotion/dyads scores, provided as 'scores_list'.
        
        
    Returns:
    ----------
    
    A boolean, True if `scores` contains emotions, False if it contains dyads.
    
    """
    kinds = []
    for tags in tags_list:
        print(tags)
        for t in tags.keys():
            try:
                kinds += [_emo_pluthick_.emo_params(t)[2]]
            except:
                kinds += [_dyads_pluthick_.dyad_params(t)[3]]

    unique_kinds = list(set(sorted(kinds)))
    
    if len(unique_kinds) > 1:
        unique_kinds_str = ', '.join([str(a) for a in unique_kinds])
        unique_kinds_str = unique_kinds_str.replace('0', 'emotions')
        unique_kinds_str = unique_kinds_str.replace('1', 'primary dyads')
        unique_kinds_str = unique_kinds_str.replace('2', 'secondary dyads')
        unique_kinds_str = unique_kinds_str.replace('3', 'tertiary dyads')
        unique_kinds_str = unique_kinds_str.replace('4', 'opposite emotions')
        unique_kinds_str = ' and'.join(unique_kinds_str.rsplit(',', 1))
                
        error_str = "Bad input: can't draw {} altogether. Please input only one of them as 'scores'.".format(unique_kinds_str)
        raise Exception(error_str)
        
    else:
        
        kind = kinds[0]
        
        if kind == 0:
            return True
        else:
            return False
    
    
def _draw_rejection_region(ax, reject_range, rescale, offset = .15):
    
    """
    Draws the rejection range.
    
    Required arguments:
    ----------
          
    *ax*:
        The matplotlib ax to draw the rejection range upon.
        
    *reject_range*:
        A 2-item tuple, defining a region of values to be considered uninteresting.
        
    *rescale*:
        Either False or a 2-item tuple, with minimum and maximum value of the printable area.
        
    *offset*:
        A scalar, the offset from the center of the circle, where petals begin. Default is 0.15.
        
        
    Returns:
    ----------
    
    The same Matplotlib axes modified.
    
    """
    
    mmin, mmax = reject_range
    
    mmin = (mmin - rescale[0]) / (rescale[1] - rescale[0]) + offset
    mmax = (mmax - rescale[0]) / (rescale[1] - rescale[0]) + offset
    
    
    c = sg.Point(0, 0).buffer(mmax)
    ax.add_patch(descartes.PolygonPatch(c, fc='grey', ec=(.5, .5, .5, .3), alpha=.1, zorder = -2))
    
    c = plt.Circle((0, 0), mmax, color = 'grey', alpha = .4, fill = False, zorder = -1, linestyle = '--')
    ax.add_artist(c)
    
    if reject_range[0] > rescale[0]:
        c = sg.Point(0, 0).buffer(mmin)
        ax.add_patch(descartes.PolygonPatch(c, fc='white', ec=(.5, .5, .5, 0), zorder = -1))
    
        c = plt.Circle((0, 0), mmin, color = 'grey', alpha = .4, fill = False, zorder = -1, linestyle = '--')
        ax.add_artist(c)
    
    return ax
    


def _get_random_emotions(intensity_levels = False):
    
    """
    Gets a dict with emotions, ready to be drawed.
    
    Required arguments:
    ----------
          
    *intensity_levels*:
        A boolean: True if emotions petals should be splitted in the correspondent three intensity scores.
        
        
    Returns:
    ----------
    
    A dict <emotion: score>, where score can be either a scalar between 0 and 1, or a 3-item list whose sum is between 0 and 1.
    
    """
    
    import random
    
    emotions = ['joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust', 'anger', 'anticipation']
    
    scores = {emotion: random.uniform(0, 1) for emotion in emotions}
    
    if intensity_levels:
        for emotion in emotions:
            scores_emo = [0, 0, 0]
            
            scores_emo[0] = random.uniform(0, scores[emotion])
            scores_emo[1] = random.uniform(0, scores[emotion] - scores_emo[0])
            scores_emo[2] = scores[emotion] - sum(scores_emo)
            
            scores[emotion] = scores_emo

    
    return scores
    
    
    
def _get_random_dyads(dyads_kind = 'primary'):
    """
    Gets a dict with dyads, ready to be drawed.
    
    Required arguments:
    ----------
          
    *dyads_kind*:
        A string: the kind of dyads to get. Accepted values are 'primary', 'secondary', 'tertiary' and 'opposites'
        
        
    Returns:
    ----------
    
    A dict <dyad: score>, where score is a scalar between 0 and 1.
    
    """
    
    import random
    
    if dyads_kind == 'primary':
        dyads = ['love', 'submission', 'alarm', 'disappointment', 'remorse', 'contempt', 'aggressiveness', 'optimism']
    elif dyads_kind == 'secondary':
        dyads = ['guilt', 'curiosity', 'despair', 'unbelief', 'envy', 'cynism', 'pride', 'hope']
    elif dyads_kind == 'tertiary':
        dyads = ['delight', 'sentimentality', 'shame', 'outrage', 'pessimism', 'morbidness', 'dominance', 'anxiety']
    elif dyads_kind == 'opposite':
        dyads = ['bittersweetness', 'ambivalence', 'frozenness', 'confusion']
    else:
        print("Dyads kind must be one of 'primary', 'secondary', 'tertiary' or 'opposite'. Did not recognized '{}': fall back to primary dyads.".format(dyads_kind))
        dyads = ['love', 'submission', 'alarm', 'disappointment', 'remorse', 'contempt', 'aggressiveness', 'optimism']
    
    scores = {dyad: random.uniform(0, 1) for dyad in dyads}
            
    
    return scores
    


def _check_values(scores, rescale, reject_range):
    """
    Check correctness of values inputed by users.
    
    Required arguments:
    ----------
          
    *scores*:
        A dictionary with emotions or dyads. 
        For each entry, values accepted are a 3-values iterable (for emotions only) or a scalar value between 0 and 1.
        The sum of the 3-values iterable values must not exceed 1, and no value should be negative.
        See emo_params() and dyad_params() for accepted keys.
                
        Emotions and dyads are mutually exclusive. Different kinds of dyads are mutually exclusive.
   
    *rescale*:
        A 2-item tuple. If not None, it rescales the petal length over the two values. 
        For more see http://www.github.com/alfonsosemeraro/plutchik/documentation.md
        
    *reject_range*:
        A 2-item tuple. All petal scores that fall within the range must be considered non-interesting, thus drawed in grey.
        Default is None (no range at all).
        
        
    Returns:
    ----------
    
    A 2-items tuple: the new value of the `rescale` argument.
    
    """
    min_score = np.inf
    max_score = -np.inf
    
    
    for key in scores.keys():
        
        # Check correctedness of values
        if hasattr(scores[key], '__iter__'): 
            if (not reject_range) and any([e < 0 for e in scores[key]]):
                raise Exception("Bad input for `{}`. Emotion/dyads scores should be positive.".format(key))
            tmp = sum(scores[key])
            
        else:
#            if (not reject_range) and scores[key] < 0:
#                raise Exception("Bad input for `{}`. Emotion scores should be positive.".format(key))
            tmp = scores[key]
            
            
        # If reject_range, values must be rescaled accordingly
        # Now we take extremes...
        min_score = tmp if tmp < min_score else min_score
        max_score = tmp if tmp > max_score else max_score
        
    
    # ...and now we can compute normalization!
    
    # Case A: users tell a reject_range, but don't decide any normalization scale: we do
    if (not rescale) and (reject_range):
        max_score = max_score if max_score > reject_range[1] else reject_range[1]
        min_score = min_score if min_score < reject_range[0] else reject_range[0]
        emo_diff = max_score - min_score
        min_score -= emo_diff*.1
        max_score += emo_diff*.1
        rescale = (min_score, max_score)
        
    # Case B: users tell a reject_range, and they decide a normalization scale: we check correctness
    elif rescale and reject_range:
        if (rescale[0] > reject_range[0]) or (rescale[1] < reject_range[1]):
            raise Exception("Bad input for `rescale` and `reject_range` arguments: rejection range is outside the rescaled area.")
            
        if (rescale[0] > min_score) or (rescale[1] < max_score):
            raise Exception("Bad input for `rescale` argument: at least one petal is outside the rescale area. Minimum values are ({}, {})".format(min_score, max_score))
    
    # Case C: users don't tell a reject_range, and they decide a normalization scale: pass
    elif (not reject_range) and rescale:
        if (rescale[0] > min_score) or (rescale[1] < max_score):
            print(min_score, max_score, rescale)
            raise Exception("Bad input for `rescale` argument: at least one petal is outside the rescale area. Minimum values are ({}, {})".format(min_score, max_score))

    # Case D: users don't tell a reject_range nor a normalization: we decide [0,1] unless max_value is higher
    elif (not reject_range) and (not rescale):
        if min_score >= 0 and max_score <= 1:
            rescale = (0, 1)
        else:
            emo_diff = max_score - min_score
            min_score -= emo_diff*.1
            max_score += emo_diff*.1
            rescale = (min_score, max_score)
        
    return rescale



    
def _draw_plutchik(scores,
             ax = None,
             rescale = None,
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
        A string or a list of main emotions to highlight. If a list of emotions is given, other emotions will be shadowed. Default is 'all'.
        
    *show_intensity_levels*:
        A string or a list of main emotions. It shows all three intensity scores for each emotion in the list, and for the others cumulative scores. Default is 'none'.
        
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
        The input Axes modified.     
        
    """
    
    # Lowering emotions/dyads names
    scores = {key.lower(): val for key, val in scores.items()}
    
    if any([np.isnan(val) for val in scores.values()]):
        scores = {key: 0 if np.isnan(val) else val for key, val in scores.items()}
    
    # Checking for correctness of scores
    rescale = _check_values(scores, rescale, reject_range)
    
    # Check if dyads or emotions, and what kind of dyads
    score_is_emotions = _check_scores_kind(scores)
    if score_is_emotions:
        emotions, dyads = scores, None
    else:
        emotions, dyads = None, scores
        
    # Create subplot if is not provided as parameter
    if not ax:
        fig, ax = plt.subplots(figsize = (8, 8))
    
    # Managing fonts
    if not font:
        font = 'sans-serif'
        
    
    
    # Drawing the rejection range
    if reject_range:
        _draw_rejection_region(ax, reject_range, rescale)
        
        
    # Draw coordinates (if needed) before any petal
    if show_coordinates:
        all_ticks = reject_range == None
        _polar_coordinates(ax = ax, 
                           font = font, fontweight = fontweight, fontsize = fontsize, 
                           show_ticklabels = show_ticklabels, ticklabels_angle = ticklabels_angle, ticklabels_size = ticklabels_size, 
                           all_ticks = all_ticks, rescale = rescale)
            
    # Draw inner white circle
    _neutral_central_circle(ax)
        
    
    # Emotions and dyads are mutually exclusive
    if emotions:
        
        for emo in emotions:                 
            # Draw emotion petal
            _emo_pluthick_._draw_emotion_petal(ax, emotion_score = emotions[emo], emotion = emo, 
                        font = font, fontweight = fontweight, fontsize = fontsize,
                        highlight = highlight, show_intensity_levels = show_intensity_levels,
                        show_coordinates = show_coordinates, height_width_ratio = height_width_ratio, 
                        reject_range = reject_range, rescale = rescale)
            
    elif dyads:
        
        for dyad in dyads:
                             
            # Draw dyad bicolor petal
            _dyads_pluthick_._draw_dyad_petal(ax, dyad_score = dyads[dyad], dyad = dyad, 
                        font = font, fontweight = fontweight, fontsize = fontsize,
                        highlight = highlight,
                        show_coordinates = show_coordinates, height_width_ratio = height_width_ratio, 
                        reject_range = reject_range, rescale = rescale)
            
            
        # Annotation inside the circle
        _, _, _, level = _dyads_pluthick_.dyad_params(list(dyads.keys())[0]) # get the first dyad level (they all are the same)
        ll = level if level != 4 else 'opp.' # what to annotate
        xy = (-0.03, -0.03) if level != 4 else (-0.13, -0.03) # exact center of '1' or 'opp' is slightly different
        ax.annotate(s = ll, xy = xy, fontsize = fontsize, fontfamily = font, fontweight = 'bold', zorder = 30)   
        
        # Ghost dotted track that connects colored arcs
        c = plt.Circle((0, 0), 1.60, color = 'grey', alpha = .3, fill = False, zorder = -20, linestyle = 'dotted' )
        ax.add_artist(c)         
           
     
    # Adjusting printable area size
    lim = 1.6 if show_coordinates else 1.2
    lim = lim + 0.1 if dyads else lim
    
    ax.set_xlim((-lim, lim))
    ax.set_ylim((-lim, lim))
    
    
    # Default is no axis    
    ax.axis('off')
    
    # Title and title size
    if not title_size:
        title_size = fontsize
    
    if title:
        ax.set_title(title, fontfamily = font, fontsize = title_size, fontweight = 'bold', pad = 20)
        
    return ax



#
#def draw_plutchik_comparison(scores_list,
#             ax = None,
#             rescale = False,
#             reject_range = None, 
#             highlight = 'all',
#             show_intensity_levels = 'none', 
#             font = None, 
#             fontweight = 'light', 
#             fontsize = 15, 
#             show_coordinates = True,  
#             show_ticklabels = False, 
#             ticklabels_angle = 0, 
#             ticklabels_size = 11, 
#             height_width_ratio = 1, 
#             title = None, 
#             title_size = None):
#    """
#    Draw the emotions or dyads Plutchik flower.
#    Full details at https://github.com/alfonsosemeraro/pyplutchik/blob/master/Documentation.md
#    
#    Required arguments:
#    ----------
#          
#    *scores*:
#        A list of dictionaries with emotions or dyads. 
#        For each entry of each dictionary, values accepted are a 3-values iterable (for emotions only) or a scalar.
#        See https://github.com/alfonsosemeraro/pyplutchik/blob/master/Documentation.md for accepted keys.
#                
#        Emotions and dyads are mutually exclusive. Different kinds of dyads are mutually exclusive.
#   
#    *ax*:
#        Axes to draw the coordinates.
#        
#    *rescale*:
#        Either False or a 2-item tuple, with minimum and maximum value of the printable area.
#        
#    *reject_range*:
#        A 2-item tuple. All petal scores that fall within the range must be considered non-interesting, thus drawed in grey.
#        Default is None (no range at all).
#        
#    *highlight*:
#        A string or a list of main emotions/dyads to highlight. If a list of emotions/dyads is given, other emotions/dyads will be shadowed. Default is 'all'.
#        
#    *show_intensity_levels*:
#        A string or a list of main emotions. It shows all three intensity scores for each emotion in the list, and for the others cumulative scores. Default is 'none'.
#        
#    *font*:
#        Font of text. Default is sans-serif.
#        
#    *fontweight*:
#        Font weight of text. Default is light.
#        
#    *fontsize*:
#        Font size of text. Default is 15.
#        
#    *show_coordinates*:
#        A boolean, wether to show polar coordinates or not.
#        
#    *show_ticklabels*:
#        Boolean, wether to show tick labels under Joy petal. Default is False.
#        
#    *ticklabels_angle*:
#        How much to rotate tick labels from y=0. Value should be given in radians. Default is 0.
#        
#    *ticklabels_size*:
#        Size of tick labels. Default is 11.
#        
#    *height_width_ratio*:
#        Ratio between height and width of the petal. Lower the ratio, thicker the petal. Default is 1.
#        
#    *title*:
#        Title for the plot.
#        
#    *title_size*:
#        Size of the title. Default is font_size.
#        
#    Returns:
#    ----------
#    *ax*:
#        The input Axes modified.     
#        
#    """
#    
#    # Lowering emotions/dyads names
#    scores_list = [{key.lower(): val for key, val in scores.items()} for scores in scores_list]
#    
#    # Checking for correctness of scores
#    rescale_values = [_check_values(scores, rescale, reject_range) for scores in scores_list]
#    rescale = (min([rv[0] for rv in rescale_values]), max([rv[1] for rv in rescale_values]))
#    
#    # Check if dyads or emotions, and what kind of dyads
#    scores_are_emotions = _check_scores_list_kind(scores_list)
#    if scores_are_emotions:
#        emotions_list, dyads_list = scores_list, None
#    else:
#        emotions_list, dyads_list = None, scores_list
#        
#    # Create subplot if is not provided as parameter
#    if not ax:
#        fig, ax = plt.subplots(figsize = (8, 8))
#    
#    # Managing fonts
#    if not font:
#        font = 'sans-serif'
#        
#        
#    ## WE ARE HERE!!!!
#    
#    
#    # Drawing the rejection range
#    if reject_range:
#        _draw_rejection_region(ax, reject_range, rescale)
#        
#        
#    # Draw coordinates (if needed) before any petal
#    if show_coordinates:
#        all_ticks = reject_range == None
#        _polar_coordinates(ax = ax, 
#                           font = font, fontweight = fontweight, fontsize = fontsize, 
#                           show_ticklabels = show_ticklabels, ticklabels_angle = ticklabels_angle, ticklabels_size = ticklabels_size, 
#                           all_ticks = all_ticks, rescale = rescale)
#            
#    # Draw inner white circle
#    _neutral_central_circle(ax)
#        
#    
#    # Emotions and dyads are mutually exclusive
#    if emotions_list:
#        
#        for i, emotions in enumerate(emotions_list):
#            for emo in emotions:                 
#                # Draw emotion petal
#                _emo_pluthick_._draw_emotion_petal(ax, emotion_score = emotions[emo], emotion = emo, 
#                            font = font, fontweight = fontweight, fontsize = fontsize,
#                            highlight = highlight, show_intensity_levels = show_intensity_levels,
#                            show_coordinates = show_coordinates, height_width_ratio = height_width_ratio, 
#                            reject_range = reject_range, rescale = rescale,
#                            comparison_tot = len(emotions_list), comparison_index = i)
#            
#    elif dyads_list:
#        
#        for dyads in dyads_list:
#            for dyad in dyads:
#                                 
#                # Draw dyad bicolor petal
#                _dyads_pluthick_._draw_dyad_petal(ax, dyad_score = dyads[dyad], dyad = dyad, 
#                            font = font, fontweight = fontweight, fontsize = fontsize,
#                            highlight = highlight,
#                            show_coordinates = show_coordinates, height_width_ratio = height_width_ratio, 
#                            reject_range = reject_range, rescale = rescale)
#            
#            
#        # Annotation inside the circle
#        _, _, _, level = _dyads_pluthick_.dyad_params(list(dyads.keys())[0]) # get the first dyad level (they all are the same)
#        ll = level if level != 4 else 'opp.' # what to annotate
#        xy = (-0.03, -0.03) if level != 4 else (-0.13, -0.03) # exact center of '1' or 'opp' is slightly different
#        ax.annotate(s = ll, xy = xy, fontsize = fontsize, fontfamily = font, fontweight = 'bold', zorder = 30)   
#        
#        # Ghost dotted track that connects colored arcs
#        c = plt.Circle((0, 0), 1.60, color = 'grey', alpha = .3, fill = False, zorder = -20, linestyle = 'dotted' )
#        ax.add_artist(c)         
#           
#     
#    # Adjusting printable area size
#    lim = 1.6 if show_coordinates else 1.2
#    lim = lim + 0.1 if dyads_list else lim
#    
#    ax.set_xlim((-lim, lim))
#    ax.set_ylim((-lim, lim))
#    
#    
#    # Default is no axis    
#    ax.axis('off')
#    
#    # Title and title size
#    if not title_size:
#        title_size = fontsize
#    
#    if title:
#        ax.set_title(title, fontfamily = font, fontsize = title_size, fontweight = 'bold', pad = 20)
#        
#    return ax
#
