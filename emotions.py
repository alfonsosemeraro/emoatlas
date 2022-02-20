"""
**********
Plutchik :: emotions
**********

This script manages emotions drawing functions.
--------
repository available at https://www.github.com/alfonsosemeraro/pyplutchik
@author: Alfonso Semeraro <alfonso.semeraro@gmail.com>

"""

import shapely.geometry as sg
import descartes
from math import sqrt, cos, sin, radians
from matplotlib import colors


def emo_params(emotion):
    """
    Gets color and angle for drawing a petal.
    Color and angle depend on the emotion name.

    Required arguments:
    ----------
    *emotion*:
        Emotion's name. Possible values: 
        ['joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust', 'anger', 'anticipation']
    
    
    Returns:
    ----------
    *color*:
        Matplotlib color for the petal. See: https://matplotlib.org/3.1.0/gallery/color/named_colors.html
        
    *angle*:
        Each subsequent petal is rotated 45° around the origin.    
        
        
    Notes:
    -----
    This function allows also 8 principal emotions, one for each Plutchik's flower petal.
    No high or low intensity emotions are allowed (no 'ecstasy' or 'serenity', for instance).
    """
    
    if emotion == 'joy':
        color = 'gold'
        angle = 0
    elif emotion == 'trust':
        color = 'olivedrab'
        angle = -45
    elif emotion == 'fear':
        color = 'forestgreen'
        angle = -90
    elif emotion == 'surprise':
        color = 'skyblue'
        angle = -135
    elif emotion == 'sadness':
        color = 'dodgerblue'
        angle = -180
    elif emotion == 'disgust':
        color = 'slateblue'
        angle = -225
    elif emotion == 'anger':
        color = 'orangered'
        angle = -270
    elif emotion == 'anticipation':
        color = 'darkorange'
        angle = -315
    else:
        raise Exception("""Bad input: {} is not an accepted emotion.
                        Must be one of 'joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust', 'anger', 'anticipation'""".format(emotion))
    return color, angle, 0



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


def _petal_shape_emotion(ax, emotion_score, color, angle, font, fontweight, fontsize, highlight, will_circle, offset = .15, height_width_ratio = 1, rescale = False):
    """
    Draw a petal.
    A petal is the intersection area between two circles.
    The height of the petal depends on the radius and the center of the circles.
    Full details at http://www.github.com/alfonsosemeraro/plutchik/tutorial.ipynb
    
    Required arguments:
    ----------
    *ax*:
        Axes to draw the coordinates.
        
    *emotion_score*:
        Score of the emotion. Values range from 0 to 1.
       
    *color*:
        Color of the petal. See emo_params().
        
    *angle*:
        Rotation angle of the petal. See emo_params().
        
    *font*:
        Font of text. Default is Montserrat.
        
    *fontweight*:
        Font weight of text. Default is light.
        
    *fontsize*:
        Font size of text. Default is 15.
        
    *highlight*:
        String. 'opaque' if the petal must be shadowed, 'regular' is default.
        
    *will_circle*:
        Boolean. If three intensities will be plotted, then the lower petal must be pale.
        
    *offset*:
        Central neutral circle has radius = .15, and petals must start from there.
    
    *height_width_ratio*:
        Ratio between height and width of the petal. Lower the ratio, thicker the petal. Default is 1.
        
    *rescale*:
        Either False or a 2-item tuple, with minimum and maximum value of the printable area.
        
    Returns:
    ----------
    *petal*:
        The petal, a shapely shape.     
        
    """

    if rescale:
        emotion_score = ((emotion_score - rescale[0]) / (rescale[1] - rescale[0]))
    
    # Computing proportions. 
    h = 1*emotion_score + offset
    x = height_width_ratio*emotion_score
    y = h/2 
    r = sqrt(x**2 + y**2)
    
    # Computing rotated centers
    x_right, y_right = _rotate_point((x, y), angle)
    x_left, y_left = _rotate_point((-x, y), angle)
    
    # Circles and intersection
    right = sg.Point(x_right, y_right).buffer(r)
    left = sg.Point(x_left, y_left).buffer(r)
    petal = right.intersection(left)
    
    # Alpha for highlighting
    if highlight == 'regular':
        if will_circle:
            alpha = .3
        else:
            alpha = .5
            
    elif will_circle:
        alpha = .0
        
    else:
        alpha = .0
    
    ax.add_patch(descartes.PolygonPatch(petal, fc='white', lw = 0, alpha=1, zorder = 0))
    ax.add_patch(descartes.PolygonPatch(petal, fc=color, lw= 0, alpha=alpha, zorder = 10))
    
    return petal




def _petal_spine_emotion(ax, emotion, emotion_score, color, angle, font, fontweight, fontsize, highlight = 'all', offset = .15):
    """
    Draw the spine beneath a petal, and the annotation of emotion and emotion's value.
    The spine is a straight line from the center, of length 1.03.
    Full details at http://www.github.com/alfonsosemeraro/plutchik/tutorial.ipynb
    
    Required arguments:
    ----------
    *ax*:
        Axes to draw the coordinates.
        
    *emotion*:
        Emotion's name.
        
    *emotion_score*:
        Score of the emotion. Values range from 0 to 1. if list, it must contain 3 values that sum up to 1.
       
    *color*:
        Color of the petal. See emo_params().
        
    *angle*:
        Rotation angle of the petal. See emo_params().
        
    *font*:
        Font of text. Default is Montserrat.
        
    *fontweight*:
        Font weight of text. Default is light.
        
    *fontsize*:
        Font size of text. Default is 15.
        
    *highlight*:
        String. 'opaque' if the petal must be shadowed, 'regular' is default.
        
    *offset*:
        Central neutral circle has radius = .15, and petals must start from there.
        
    """
    
    # Diagonal lines and ticks
    step = .03
    p1 = (0, 0)
    p2 = _rotate_point((0, 1 + step + offset), angle) # draw line until 0, 1 + step + offset
    p3 = _rotate_point((-step, 1 + step + offset), angle) # draw tick
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], zorder = 5, color = 'black', alpha = .3, linewidth = .75)
    ax.plot([p2[0], p3[0]], [p2[1], p3[1]], zorder = 5, color = 'black', alpha = .3, linewidth = .75)
    
    # Managing highlighting and transparency
    if highlight == 'opaque':
        alpha = .8
        color = 'lightgrey'
    else:
        alpha = 1
    
    # Checking if iterable
    try:
        _ = emotion_score[0]
        iterable = True
    except:
        iterable = False
       
        
    if iterable:
        # Label
        angle2 = angle + 180 if -110 > angle > -260 else angle
        p4 = _rotate_point((0, 1.40 + step + offset), angle)
        ax.annotate(s = emotion, xy = p4, rotation = angle2, ha='center', va = 'center',
                    fontfamily = font, size = fontsize, fontweight = fontweight)
        
        # Score 1
        p5 = _rotate_point((0, 1.07 + step + offset), angle)
        ax.annotate(s = "{0:.2f}".format(round(emotion_score[0],2)), xy = p5, rotation = angle2, ha='center', va = 'center',
                    color = color, fontfamily = font, size = fontsize, fontweight = 'regular', alpha = alpha)
        
        # Score 2
        p6 = _rotate_point((0, 1.17 + step + offset), angle)
        ax.annotate(s = "{0:.2f}".format(round(emotion_score[1],2)), xy = p6, rotation = angle2, ha='center', va = 'center',
                    color = color, fontfamily = font, size = fontsize, fontweight = 'demibold', alpha = alpha)
        
        # Score 3
        p7 = _rotate_point((0, 1.27 + step + offset), angle)
        ax.annotate(s = "{0:.2f}".format(round(emotion_score[2],2)), xy = p7, rotation = angle2, ha='center', va = 'center',
                    color = color, fontfamily = font, size = fontsize, fontweight = 'regular', alpha = alpha)        
        
    else:  
        # Label
        angle2 = angle + 180 if -110 > angle > -260 else angle
        p4 = _rotate_point((0, 1.23 + step + offset), angle)
        ax.annotate(s = emotion, xy = p4, rotation = angle2, ha='center', va = 'center',
                    fontfamily = font, size = fontsize, fontweight = fontweight)
        
        # Score
        p5 = _rotate_point((0, 1.1 + step + offset), angle)
        ax.annotate(s = "{0:.2f}".format(round(emotion_score,2)), xy = p5, rotation = angle2, ha='center', va = 'center',
                    color = color, fontfamily = font, size = fontsize, fontweight = 'demibold', alpha = alpha)
        



    
def _petal_circle(ax, petal, radius, color, inner = False, highlight = 'none', offset = .15, rescale = False):
    """
    Each petal may have 3 degrees of intensity.
    Each of the three sections of a petal is the interception between
    the petal and up to two concentric circles from the origin.
    This function draws one section.
    Full details at http://www.github.com/alfonsosemeraro/plutchik/tutorial.ipynb
    
    Required arguments:
    ----------
    *ax*:
        Axes to draw the coordinates.
        
    *petal*:
        The petal shape. See petal().
        
    *radius*:
        Radius of the section.
       
    *color*:
        Color of the section. See emo_params().
        
    *inner*:
        Boolean. If True, a second patch is drawn with alpha = 0.3, making the inner circle darker.
        
    *highlight*:
        String. 'opaque' if the petal must be shadowed, 'regular' is default.
        
    *offset*:
        Central neutral circle has radius = .15, and petals must start from there.
        
    *rescale*:
        Either False or a 2-item tuple, with minimum and maximum value of the printable area.
    
    """
    
    if radius:
        
        if rescale:
            radius = ((radius - rescale[0]) / (rescale[1] - rescale[0]))
            
        # Define the intersection between circle c and petal
        c = sg.Point(0, 0).buffer(radius + offset)
        area = petal.intersection(c)
        
        # Managing alpha and color
        alpha0 = 1 if highlight == 'regular' else .2
        ecol = (colors.to_rgba(color)[0], colors.to_rgba(color)[1], colors.to_rgba(color)[2], alpha0)
        
        alpha1 = .5 if highlight == 'regular' else .0
        
        # Drawing separately the shape and a thicker border
        ax.add_patch(descartes.PolygonPatch(area, fc=color, ec = 'black', lw = 0, alpha=alpha1))
        ax.add_patch(descartes.PolygonPatch(area, fc=(0, 0, 0, 0), ec = ecol, lw = 1.3))
        
        # The innermost circle gets to be brighter because of the repeated overlap
        # Its alpha is diminished to avoid too much bright colors
        if inner:
            alpha2 = .3 if highlight == 'regular' else .0
            ax.add_patch(descartes.PolygonPatch(area, fc=color, ec = 'w', lw = 0, alpha=alpha2))
            ax.add_patch(descartes.PolygonPatch(area, fc=(0, 0, 0, 0), ec = ecol, lw = 1.5))
    



def _draw_emotion_petal(ax, emotion, emotion_score, highlight, show_intensity_levels, font, fontweight, fontsize, show_coordinates, height_width_ratio, reject_range, comparison_tot = None, comparison_index = None, rescale = False):
    """
    Draw the petal and its possible sections.
    Full details at http://www.github.com/alfonsosemeraro/plutchik/tutorial.ipynb
    
    Required arguments:
    ----------
    *ax*:
        Axes to draw the coordinates.
        
    *emotion*:
        Emotion's name.
        
    *emotion_score*:
        Score of the emotion. Values range from 0 to 1.
    
    *highlight*:
        A list of main emotions to highlight. Other emotions will be shadowed.
        
    *show_intensity_levels*:
        A string or a list of main emotions. It shows all three intensity scores for each emotion in the list, and for the others cumulative scores. Default is 'none'.
         
    *font*:
        Font of text. Default is Montserrat.
        
    *fontweight*:
        Font weight of text. Default is light.
        
    *fontsize*:
        Font size of text. Default is 15.
       
    *show_coordinates*:
        A boolean, wether to show polar coordinates or not.   
        
    *height_width_ratio*:
        Ratio between height and width of the petal. Lower the ratio, thicker the petal. Default is 1.
        
    *reject_range*:
        A 2-item tuple. All petal scores that fall within the range must be considered non-interesting, thus drawed in grey.
        Default is None (no range at all).
        
    *comparison_tot*:
        Either an integer or None. If an integer, it's the lenght of Plutchik's flowers to be compared.
        
    *comparison_index*:
        Either an integer or None. If an integer, it indicates that this petal is the i-th.
        
    *rescale*:
        Either False or a 2-item tuple, with minimum and maximum value of the printable area.
        
    """
    
    color, angle, _ = emo_params(emotion)
    
    if comparison_tot and comparison_index:
        angle = angle - (45/(1+comparison_tot))*comparison_index
    
    # Check if iterable
    try:
        _ = emotion_score[0]
        iterable = True
    except:
        iterable = False
    
    
    # Manage highlight and opacity
    if highlight != 'all':
        if emotion in highlight:
            highlight = 'regular'
        else:
            highlight = 'opaque'
    else:
        highlight = 'regular'
        
    # Reject range overrides general highlighting settings
    if reject_range:
        
        try:
            emoscore = sum(emotion_score)
        except:
            emoscore = emotion_score
            
        if reject_range[0] < emoscore < reject_range[1]:
            highlight = 'opaque'
        else:
            highlight = 'regular'
            
    ## ! PATCH on petal width
    height_width_ratio *= 1.1
            
            
    # Drawing 
    if not iterable:
        if show_coordinates and not comparison_index:
            
            # Draw the line and tick behind a petal 
            _petal_spine_emotion(ax = ax, emotion = emotion, emotion_score = emotion_score, 
                        color = color, angle = angle, 
                        font = font, fontweight = fontweight, fontsize = fontsize, 
                        highlight = highlight,
                        offset = .15)
        # Draw petal
        _petal_shape_emotion(ax, emotion_score, color, angle, font, fontweight, fontsize, height_width_ratio = height_width_ratio, highlight = highlight, will_circle = False, rescale = rescale)
        # Draw border
        _outer_border(ax, emotion_score, color, angle, height_width_ratio = height_width_ratio, highlight = highlight, rescale = rescale)
        
    else:
        # Total length is the sum of the emotion score
        a, b, c = emotion_score
        length = a + b + c
        # Show three scores or just the cumulative one?
        label = emotion_score if ((show_intensity_levels == 'all') or (emotion in show_intensity_levels)) else length
        
        if show_coordinates and not comparison_index:
            
            # Draw the line and tick behind a petal
            _petal_spine_emotion(ax = ax, emotion = emotion, emotion_score = label, 
                        color = color, angle = angle, 
                        font = font, fontweight = fontweight, fontsize = fontsize,
                        highlight = highlight,
                        offset = .15)
        
        # Draw petal
        petal_shape = _petal_shape_emotion(ax, length, color, angle, font, fontweight, fontsize, height_width_ratio = height_width_ratio, highlight = highlight, will_circle = True, rescale = rescale)
        # Draw inner petal section
        _petal_circle(ax, petal_shape, a + b, color, False, highlight, rescale = rescale)
        # Draw middle petal section
        _petal_circle(ax, petal_shape, a, color, True, highlight, rescale = rescale)        
        # Draw border
        _outer_border(ax, length, color, angle, height_width_ratio = height_width_ratio, highlight = highlight, rescale = rescale)
        



def _outer_border(ax, emotion_score, color, angle, highlight, offset = .15, height_width_ratio = 1, rescale = False):
    """
    Draw a the outer border of a petal.
    
    Required arguments:
    ----------
    *ax*:
        Axes to draw the coordinates.
        
    *emotion_score*:
        Score of the emotion. Values range from 0 to 1.
       
    *color*:
        Color of the petal. See emo_params().       
        
    *angle*:
        Rotation angle of the petal. See emo_params().
        
    *highlight*:
        String. 'opaque' if the petal must be shadowed, 'regular' is default.
        
    *offset*:
        Central neutral circle has radius = .15, and petals must start from there.
    
    *height_width_ratio*:
        Ratio between height and width of the petal. Lower the ratio, thicker the petal. Default is 1.
        
    *rescale*:
        Either False or a 2-item tuple, with minimum and maximum value of the printable area.
        
    """
    
    if rescale:
        emotion_score = ((emotion_score - rescale[0]) / (rescale[1] - rescale[0]))
        
    # Computing proportions. 
    h = 1*emotion_score + offset
    x = height_width_ratio*emotion_score
    y = h/2 
    r = sqrt(x**2 + y**2)
    
    # Computing rotated centers
    x_right, y_right = _rotate_point((x, y), angle)
    x_left, y_left = _rotate_point((-x, y), angle)
    
    # Circles and intersection
    right = sg.Point(x_right, y_right).buffer(r)
    left = sg.Point(x_left, y_left).buffer(r)
    petal = right.intersection(left)
    
    # alpha and color
    alpha = 1 if highlight == 'regular' else .8
    ecol = (colors.to_rgba(color)[0], colors.to_rgba(color)[1], colors.to_rgba(color)[2], alpha)


    ax.add_patch(descartes.PolygonPatch(petal, fc=(0, 0, 0, 0), ec = ecol, lw= 1))
    