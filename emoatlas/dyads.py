"""
**********
Plutchik :: dyads
**********

This script manages dyads drawing functions.
--------
repository available at https://www.github.com/alfonsosemeraro/pyplutchik
@author: Alfonso Semeraro <alfonso.semeraro@gmail.com>

"""

import shapely.geometry as sg
from math import sqrt, cos, sin, radians
from matplotlib import colors
import emoatlas.emotions as _emo_pluthick_

def dyad_params(dyad):
    """
    Gets colormap and angle for drawing a dyad.
    Colormap and angle depend on the dyad name.

    Required arguments:
    ----------
    *dyad*:
        Dyad's name. Possible values:

        {"primary": ['love', 'submission', 'alarm', 'disappointment', 'remorse', 'contempt', 'aggression', 'optimism'],
         "secondary": ['guilt', 'curiosity', 'despair', '', 'envy', 'cynism', 'pride', 'fatalism'],
         "tertiary": ['delight', 'sentimentality', 'shame', 'outrage', 'pessimism', 'morbidness', 'dominance', 'anxiety']}

    Returns:
    ----------
    *colormap*:
        Matplotlib colormap for the dyad. See: https://matplotlib.org/3.1.0/gallery/color/named_colors.html

    *angle*:
        Each subsequent dyad is rotated 45° around the origin.


    """

    # PRIMARY DYADS
    if dyad == "love":
        cmap = ["gold", "olivedrab"]
        angle = -45 / 2
        emos = ["joy", "trust"]
        level = 1

    elif dyad == "submission":
        cmap = ["olivedrab", "forestgreen"]
        angle = (-45 / 2) + (-45)
        emos = ["trust", "fear"]
        level = 1

    elif dyad == "alarm":
        cmap = ["forestgreen", "skyblue"]
        angle = (-45 / 2) + (-90)
        emos = ["fear", "surprise"]
        level = 1

    elif dyad == "disappointment":
        cmap = ["skyblue", "dodgerblue"]
        angle = (-45 / 2) + (-135)
        emos = ["surprise", "sadness"]
        level = 1

    elif dyad == "remorse":
        cmap = ["dodgerblue", "slateblue"]
        angle = (-45 / 2) + (-180)
        emos = ["sadness", "disgust"]
        level = 1

    elif dyad == "contempt":
        cmap = ["slateblue", "orangered"]
        angle = (-45 / 2) + (-225)
        emos = ["disgust", "anger"]
        level = 1

    elif dyad == "aggressiveness":
        cmap = ["orangered", "darkorange"]
        angle = (-45 / 2) + (-270)
        emos = ["anger", "anticipation"]
        level = 1

    elif dyad == "optimism":
        cmap = ["darkorange", "gold"]
        angle = (-45 / 2) + (-315)
        emos = ["anticipation", "joy"]
        level = 1

    # SECONDARY DYADS
    elif dyad == "guilt":
        cmap = ["gold", "forestgreen"]
        angle = -45
        emos = ["joy", "fear"]
        level = 2

    elif dyad == "curiosity":
        cmap = ["olivedrab", "skyblue"]
        angle = -90
        emos = ["trust", "surprise"]
        level = 2

    elif dyad == "despair":
        cmap = ["forestgreen", "dodgerblue"]
        angle = -135
        emos = ["fear", "sadness"]
        level = 2

    elif dyad == "unbelief":
        cmap = ["skyblue", "slateblue"]
        angle = -180
        emos = ["surprise", "disgust"]
        level = 2

    elif dyad == "envy":
        cmap = ["dodgerblue", "orangered"]
        angle = -225
        emos = ["sadness", "anger"]
        level = 2

    elif dyad == "cynism":
        cmap = ["slateblue", "darkorange"]
        angle = -270
        emos = ["disgust", "anticipation"]
        level = 2

    elif dyad == "pride":
        cmap = ["orangered", "gold"]
        angle = -315
        emos = ["anger", "joy"]
        level = 2

    elif dyad == "hope":
        cmap = ["darkorange", "olivedrab"]
        angle = 0
        emos = ["anticipation", "trust"]
        level = 2

    # TERTIARY DYADS
    elif dyad == "delight":
        cmap = ["gold", "skyblue"]
        angle = (-45 / 2) + (-45)
        emos = ["joy", "surprise"]
        level = 3

    elif dyad == "sentimentality":
        cmap = ["olivedrab", "dodgerblue"]
        angle = (-45 / 2) + (-90)
        emos = ["trust", "sadness"]
        level = 3

    elif dyad == "shame":
        cmap = ["forestgreen", "slateblue"]
        angle = (-45 / 2) + (-135)
        emos = ["fear", "disgust"]
        level = 3

    elif dyad == "outrage":
        cmap = ["skyblue", "orangered"]
        angle = (-45 / 2) + (-180)
        emos = ["surprise", "anger"]
        level = 3

    elif dyad == "pessimism":
        cmap = ["dodgerblue", "darkorange"]
        angle = (-45 / 2) + (-225)
        emos = ["sadness", "anticipation"]
        level = 3

    elif dyad == "morbidness":
        cmap = ["slateblue", "gold"]
        angle = (-45 / 2) + (-270)
        emos = ["disgust", "joy"]
        level = 3

    elif dyad == "dominance":
        cmap = ["orangered", "olivedrab"]
        angle = (-45 / 2) + (-315)
        emos = ["anger", "trust"]
        level = 3

    elif dyad == "anxiety":
        cmap = ["darkorange", "forestgreen"]
        angle = -45 / 2
        emos = ["anticipation", "fear"]
        level = 3

    # OPPOSITES
    elif dyad == "bittersweetness":
        cmap = ["gold", "dodgerblue"]
        angle = 0
        emos = ["joy", "sadness"]
        level = 4

    elif dyad == "ambivalence":
        cmap = ["olivedrab", "slateblue"]
        angle = -45
        emos = ["trust", "disgust"]
        level = 4

    elif dyad == "frozenness":
        cmap = ["forestgreen", "orangered"]
        angle = -90
        emos = ["fear", "anger"]
        level = 4

    elif dyad == "confusion":
        cmap = ["skyblue", "darkorange"]
        angle = -135
        emos = ["surprise", "anticipation"]
        level = 4

    else:
        raise Exception(
            """Bad input: '{}' is not an accepted name for a dyad.
                        Must be one of:
                            'love', 'submission', 'alarm', 'disappointment', 'remorse', 'contempt', 'aggressiveness', 'optimism',
                            'guilt', 'curiosity', 'despair', 'unbelief', 'envy', 'cynism', 'pride', 'hope',
                            'delight', 'sentimentality', 'shame', 'outrage', 'pessimism', 'morbidness', 'dominance', 'anxiety',
                            'bittersweetness', 'ambivalence', 'frozenness', 'confusion'
                        """.format(
                dyad
            )
        )
    return emos, cmap, angle, level


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


def _outer_border(
    ax,
    dyad_score,
    color,
    angle,
    highlight,
    offset=0.15,
    height_width_ratio=1,
    rescale=False,
):
    """
    Draw a the outer border of a petal.

    Required arguments:
    ----------
    *ax*:
        Axes to draw the coordinates.

    *dyad_score*:
        Score of the dyad.

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
        dyad_score = (dyad_score - rescale[0]) / (rescale[1] - rescale[0])

    # Computing proportions.
    h = 1 * dyad_score + offset
    x = height_width_ratio * dyad_score
    y = h / 2
    r = sqrt(x**2 + y**2)

    # Computing rotated centers
    x_right, y_right = _rotate_point((x, y), angle)
    x_left, y_left = _rotate_point((-x, y), angle)

    # Circles and intersection
    right = sg.Point(x_right, y_right).buffer(r)
    left = sg.Point(x_left, y_left).buffer(r)
    petal = right.intersection(left)

    # alpha and color
    alpha = 1 if highlight == "regular" else 0.8
    ecol = (
        colors.to_rgba(color)[0],
        colors.to_rgba(color)[1],
        colors.to_rgba(color)[2],
        alpha,
    )

    ax.add_patch(_emo_pluthick_.PolygonPatch(petal, fc=(0, 0, 0, 0), ec=ecol, lw=1))


def _petal_shape_dyad(
    ax,
    dyad_score,
    colorA,
    colorB,
    angle,
    font,
    fontweight,
    fontsize,
    highlight,
    will_circle,
    offset=0.15,
    height_width_ratio=1,
    rescale=False,
):
    """
    Draw a petal.
    A petal is the intersection area between two circles.
    The height of the petal depends on the radius and the center of the circles.
    Full details at https://github.com/alfonsosemeraro/pyplutchik/blob/master/Documentation.md

    Required arguments:
    ----------
    *ax*:
        Axes to draw the coordinates.

    *emotion_score*:
        Score of the emotion. Values range from 0 to 1.

    *colorA*:
        First color of the petal. See dyad_params().

    *colorB*:
        Second color of the petal. See dyad_params().

    *angle*:
        Rotation angle of the petal. See dyad_params().

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

    if dyad_score == 0:
        return ax

    if rescale:
        dyad_score = (dyad_score - rescale[0]) / (rescale[1] - rescale[0])

    # Computing proportions.
    h = 1 * dyad_score + offset
    x = height_width_ratio * dyad_score
    y = h / 2
    r = sqrt(x**2 + y**2)

    # Computing rotated centers
    x_right, y_right = _rotate_point((x, y), angle)
    x_left, y_left = _rotate_point((-x, y), angle)

    # Circles and intersection
    right = sg.Point(x_right, y_right).buffer(r)
    left = sg.Point(x_left, y_left).buffer(r)
    petal = right.intersection(left)

    # Computing squares: left
    A = _rotate_point((-2 * x, 0), angle)
    B = _rotate_point((-2 * x, h), angle)
    C = _rotate_point((0, h), angle)
    D = _rotate_point((0, 0), angle)
    square_left = sg.Polygon([A, B, C, D, A])

    # Computing squares: right
    A = _rotate_point((0, 0), angle)
    B = _rotate_point((0, h), angle)
    C = _rotate_point((2 * x, h), angle)
    D = _rotate_point((2 * x, 0), angle)
    square_right = sg.Polygon([A, B, C, D, A])

    # Computing semipetals
    petalA = petal.intersection(square_left)
    petalB = petal.intersection(square_right)

    # white petal underneath
    ax.add_patch(_emo_pluthick_.PolygonPatch(petal, fc="white", lw=0, alpha=1, zorder=0))

    # Draw each half-petal in alpha 0.7
    alpha = 0.7

    if highlight == "opaque":
        alpha = 0.0
        colorA = "lightgrey"
        colorB = "lightgrey"

    xs, ys = petalA.exterior.xy
    ax.fill(xs, ys, alpha=alpha, fc=colorA, ec="none")

    xs, ys = petalB.exterior.xy
    ax.fill(xs, ys, alpha=alpha, fc=colorB, ec="none")

    return ax


def _petal_spine_dyad(
    ax,
    dyad,
    dyad_score,
    color,
    emotion_names,
    angle,
    font,
    fontweight,
    fontsize,
    highlight="all",
    offset=0.15,
):
    """
    Draw the spine beneath a petal, and the annotation of dyad and dyad's value.
    The spine is a straight line from the center, of length 1.03 (default).
    Full details at https://github.com/alfonsosemeraro/pyplutchik/blob/master/Documentation.md

    Required arguments:
    ----------
    *ax*:
        Axes to draw the coordinates.

    *dyad*:
        Dyad's name.

    *dyad_score*:
        Score of the dyad. Values range from 0 to 1. if list, it must contain 3 values that sum up to 1.

    *color*:
        Color of the two emotions of the dyad. See dyad_params().

    *emotion_names*:
        Name of the emotions the dyad is made of. See dyad_params().

    *angle*:
        Rotation angle of the petal. See dyad_params().

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
    step = 0.03
    p1 = (0, 0)  # 0, 0 + offset
    p2 = _rotate_point(
        (0, 1 + step + offset), angle
    )  # draw line until 0, 1 + step + offset
    p3 = _rotate_point((-step, 1 + step + offset), angle)  # draw tick
    ax.plot(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        zorder=5,
        color="black",
        alpha=0.3,
        linewidth=0.75,
    )
    ax.plot(
        [p2[0], p3[0]],
        [p2[1], p3[1]],
        zorder=5,
        color="black",
        alpha=0.3,
        linewidth=0.75,
    )

    # Managing highlighting and opacity
    if highlight == "opaque":
        alpha = 0.8
        color = ["lightgrey", "lightgrey"]
    else:
        alpha = 1

    ## Drawing the two-colored circular arc over dyads
    from matplotlib.patches import Arc

    H = 3.2

    pac1 = Arc(
        (0, 0),
        width=H,
        height=H,
        angle=90,
        theta2=angle,
        theta1=angle - 18,
        ec=color[1],
        linewidth=3,
    )
    pac2 = Arc(
        (0, 0),
        width=H,
        height=H,
        angle=90,
        theta2=angle + 18,
        theta1=angle,
        ec=color[0],
        linewidth=3,
    )
    ax.add_patch(pac1)
    ax.add_patch(pac2)

    # Labels over the arcs
    angle2 = angle + 180 if -110 > angle > -260 else angle
    p9 = _rotate_point((0, 1.7), angle - 9)
    ax.annotate(
        text=emotion_names[1],
        xy=p9,
        rotation=angle2 - 8,
        ha="center",
        va="center",
        zorder=30,
        fontfamily=font,
        size=fontsize * 0.7,
        fontweight="demibold",
        color=color[1],
    )
    p10 = _rotate_point((0, 1.7), angle + 9)
    ax.annotate(
        text=emotion_names[0],
        xy=p10,
        rotation=angle2 + 8,
        ha="center",
        va="center",
        zorder=30,
        fontfamily=font,
        size=fontsize * 0.7,
        fontweight="demibold",
        color=color[0],
    )

    # Dyad label must be grey
    color = "#363636"

    # Label
    angle2 = angle + 180 if -110 > angle > -260 else angle
    p4 = _rotate_point((0, 1.23 + step + offset), angle)
    ax.annotate(
        text=dyad,
        xy=p4,
        rotation=angle2,
        ha="center",
        va="center",
        fontfamily=font,
        size=fontsize,
        fontweight=fontweight,
    )

    # Score
    p5 = _rotate_point((0, 1.1 + step + offset), angle)
    ax.annotate(
        text="{0:.2f}".format(round(dyad_score, 2)),
        xy=p5,
        rotation=angle2,
        ha="center",
        va="center",
        color=color,
        fontfamily=font,
        size=fontsize,
        fontweight="demibold",
        alpha=alpha,
    )


def _petal_circle(
    ax, petal, radius, color, inner=False, highlight="none", offset=0.15, rescale=False
):
    """
    Each petal may have 3 degrees of intensity.
    Each of the three sections of a petal is the interception between
    the petal and up to two concentric circles from the origin.
    This function draws one section.
    Full details at https://github.com/alfonsosemeraro/pyplutchik/blob/master/Documentation.md

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
            radius = (radius - rescale[0]) / (rescale[1] - rescale[0])

        # Define the intersection between circle c and petal
        c = sg.Point(0, 0).buffer(radius + offset)
        area = petal.intersection(c)

        # Managing alpha and color
        alpha0 = 1 if highlight == "regular" else 0.2
        ecol = (
            colors.to_rgba(color)[0],
            colors.to_rgba(color)[1],
            colors.to_rgba(color)[2],
            alpha0,
        )

        alpha1 = 0.5 if highlight == "regular" else 0.0

        # Drawing separately the shape and a thicker border
        ax.add_patch(
            _emo_pluthick_.PolygonPatch(area, fc=color, ec="black", lw=0, alpha=alpha1)
        )
        ax.add_patch(_emo_pluthick_.PolygonPatch(area, fc=(0, 0, 0, 0), ec=ecol, lw=1.3))

        # The innermost circle gets to be brighter because of the repeated overlap
        # Its alpha is diminished to avoid too much bright colors
        if inner:
            alpha2 = 0.3 if highlight == "regular" else 0.0
            ax.add_patch(
                _emo_pluthick_.PolygonPatch(area, fc=color, ec="w", lw=0, alpha=alpha2)
            )
            ax.add_patch(_emo_pluthick_.PolygonPatch(area, fc=(0, 0, 0, 0), ec=ecol, lw=1.5))


def _draw_dyad_petal(
    ax,
    dyad,
    dyad_score,
    highlight,
    font,
    fontweight,
    fontsize,
    show_coordinates,
    height_width_ratio,
    reject_range,
    offset=0.15,
    rescale=False,
):
    """
    Draw the petal of the dyad.
    Full details at https://github.com/alfonsosemeraro/pyplutchik/blob/master/Documentation.md

    Required arguments:
    ----------
    *ax*:
        Axes to draw the coordinates.

    *dyad*:
        Dyad's name.

    *dyad_score*:
        Score of the dyad. Values range from 0 to 1.

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

    *offset*:
        Central neutral circle has radius = .15, and petals must start from there.

    *rescale*:
        Either False or a 2-item tuple, with minimum and maximum value of the printable area.

    """
    emos, color, angle, _ = dyad_params(dyad)
    colorA, colorB = color

    # Reject range overrides general highlighting settings
    if reject_range:
        if reject_range[0] < dyad_score < reject_range[1]:
            highlight = "opaque"
        else:
            highlight = "regular"

    elif highlight == "all" or dyad in highlight:
        highlight = "regular"
    else:
        highlight = "opaque"

    if show_coordinates:
        # Draw the line and tick behind a petal
        _petal_spine_dyad(
            ax=ax,
            dyad=dyad,
            dyad_score=dyad_score,
            emotion_names=emos,
            color=color,
            angle=angle,
            font=font,
            fontweight=fontweight,
            fontsize=fontsize,
            highlight=highlight,
            offset=0.15,
        )

    # Draw petal (and get the modified ax)
    ax = _petal_shape_dyad(
        ax,
        dyad_score,
        colorA,
        colorB,
        angle,
        font,
        fontweight,
        fontsize,
        height_width_ratio=height_width_ratio,
        highlight=highlight,
        will_circle=False,
        rescale=rescale,
    )
    # Draw border
    _outer_border(
        ax,
        dyad_score,
        colorA,
        angle,
        height_width_ratio=height_width_ratio,
        highlight="all",
        rescale=rescale,
    )
