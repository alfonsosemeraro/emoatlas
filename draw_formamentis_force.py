from math import sqrt, cos, sin, radians
import random
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.path as mpath
from matplotlib.collections import PatchCollection
import networkx as nx
from resources import _valences
import community.community_louvain as commlouv
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt


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

def _noise(v, eps):
    return random.uniform(v-eps, v+eps)
    
def _initial_positions(n, eps):
    m = n-1
    points = [(0, 0)] + [_rotate_point((0,.8), (360/m)*i) for i in range(m)]
    points = [(_noise(x, eps), _noise(y, eps)) for x, y in points]
    
    return points


def _compute_link(posx, posy, centr1, centr2):
    
    # Middle point between the centroids of the clusters of x and y
    xx = _prop(centr1, centr2, .5)
    
    # Define Bezier curve
    Path = mpath.Path
    path_data = [
        (Path.MOVETO, posx),
        (Path.CURVE3, xx),
        (Path.CURVE3, posy)
        ]
    
    # add the Path to ax
    codes, verts = zip(*path_data)
    path = mpath.Path(verts, codes)
    patch = mpatches.PathPatch(path)
    
    return patch


def _prop(a, b, t = .5):
        
    midx = a[0]*t + b[0]*(1-t)
    midy = a[1]*t + b[1]*(1-t)
    
    return (midx, midy)


def _hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    lv = [int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3)]
    lv = [l/255 for l in lv] + [1]
    return lv


def _edge_color(w1, w2, _positive, _negative, _ambivalent, colz):
    if w1 in _positive and w1 in _positive:
        return colz['positive']
    if w1 in _negative and w2 in _negative:
        return colz['negative']
    
    if w1 in _negative and w2 in _positive:
        return 'purple'
    if w1 in _positive and w2 in _negative:
        return 'purple'
    
    return 'lightgrey'

def draw_formamentis_force_layout(edgelist, highlight = [], language = 'english', ax = None):
    """
    
    """
    
    
    # Define color-blind palette
    colz = {'positive': (26/256, 133/256, 255/256),
            'negative': (212/256, 17/256, 89/256)}
    
    # Get positive or negative valences
    _positive, _negative, _ambivalent = _valences(language)
    
    # Prepare the patch effect for bicolor patches
    eff = [path_effects.PathPatchEffect(fc=(.9, .9, .9), edgecolor = colz['negative'], linewidth = 2),
    path_effects.PathPatchEffect(edgecolor=colz['positive'], linewidth=2, facecolor=(0, 0, 0, 0), linestyle = '--')]
    
    if not ax:
        _, ax = plt.subplots(figsize=(9,9)) 
        
        
    # Build the Graph
    edgelist = [(a, b) for a, b in edgelist if a != b]    
    G = nx.Graph(edgelist)
     
    # Clusters and centroids
    louv = commlouv.best_partition(G)    
    comms = set(louv.values())
    eps = 2 / (len(comms) - 2)
    
    
    # Positions
    centroids = _initial_positions(len(comms), eps)
    centroids = {c: cent for c, cent in zip(comms, centroids)}
    
    # Noise nodes position around their centroids
    pos = {}
    eps = eps / 3
    for node in G.nodes():
        pos[node] = (_noise(centroids[louv[node]][0], eps), _noise(centroids[louv[node]][1], eps))
        # here one should avoid overlaps!
    
    # Just one quick iteration of spring_layout to optimize intra- and inter-cluster distances
    pos = nx.spring_layout(G, pos = pos, iterations = 1, scale=4, k = 1)
    
     
    
    # Draw EDGES :: Bezier curves
    
    patches = []
    
    for x, y in G.edges():
        if louv[x] != louv[y]:
            
            c1 = centroids[louv[x]]
            c2 = centroids[louv[y]]
            patches.append(_compute_link(pos[x], pos[y], c1, c2))
    
        else:
            plt.plot([pos[x][0], pos[y][0]], [pos[x][1], pos[y][1]], color = 'lightgrey', 
                     linewidth = 1, alpha = .1, zorder = -1)
    
    patches = PatchCollection(patches, facecolor = 'none', linewidth = 1, edgecolor = 'lightgrey', 
                              match_original=True, alpha = .3, zorder = 0)
    ax.add_collection(patches)
    
    
    
    
    
    
    # Draw NODES
    
    degs = dict(G.degree())
    mindeg, maxdeg = min(degs.values()), max(degs.values())
    degs = {k: (v-mindeg)/(maxdeg-mindeg) for k, v in degs.items()}
    
    minfont = 10
    maxorder = 7   
           
    
    for key, val in pos.items():
        
        fontsize = minfont + 5*(degs[key]**3)
        zorder = int(degs[key]*6)
        weight = 'regular'
        
        if key in highlight:
            fontsize = 18
            zorder = maxorder+1
            weight = 'heavy'
        
        if key in _positive:
            #shadow!
            plt.annotate(key, xy = (val[0]*1.01, val[1]*1.005), zorder = maxorder, fontsize = fontsize, 
                         weight = weight, color = (.7, .7, .7), 
                        bbox=dict(boxstyle='round', fc=(.7, .7, .7), ec=(.7, .7, .7), linewidth = 4))
            
            plt.annotate(key, xy = (val[0], val[1]), zorder = maxorder, fontsize = fontsize, 
                         weight = weight, color = colz['positive'], 
                        bbox=dict(boxstyle='round', fc=(.9, .9, .9), ec=(.9, .9, .9), linewidth = 4))

        elif key in _negative:
            #shadow!
            plt.annotate(key, xy = (val[0]*1.01, val[1]*1.005), zorder = maxorder, fontsize = fontsize, 
                         weight = weight, color = (.7, .7, .7), 
                        bbox=dict(boxstyle='round', fc=(.7, .7, .7), ec=(.7, .7, .7), linewidth = 4))
            
            plt.annotate(key, xy = (val[0], val[1]), zorder = maxorder, fontsize = fontsize, 
                         weight = weight, color = colz['negative'], 
                         bbox=dict(boxstyle='round', fc=(.9, .9, .9), ec=(.9, .9, .9), linewidth = 4))

        elif key in _ambivalent:
            #shadow!
            plt.annotate(key, xy = (val[0]*1.01, val[1]*1.005), zorder = maxorder, fontsize = fontsize, 
                         weight = weight, color = (.7, .7, .7), 
                        bbox=dict(boxstyle='round', fc=(.7, .7, .7), ec=(.7, .7, .7), linewidth = 4))
            
            plt.annotate(key, xy = (val[0], val[1]), zorder = maxorder, 
                         fontsize = fontsize, weight = weight,
                         bbox=dict(boxstyle='round', 
                         fc=(.9, .9, .9), ec=(119/255, 221/255, 118/255, .7), 
                         path_effects = eff, linewidth = 3))
            
        
        else:
            plt.annotate(key, xy = (val[0], val[1]), 
                         zorder = zorder, fontsize = fontsize,
                         weight = weight,  
                        bbox=dict(boxstyle='round', fc=(.85, .85, .85), ec=(.8, .8, .8), linewidth = 1))
            
    
    
    
    ax.axis('off')
    
    return ax
    