#!/usr/bin/env python
""" Provides a few styles for the main driver program to use """
import terrain
from operator import itemgetter

def _alwaysTrue(*args):
    return True

def _firstObj(*args):
    return tuple(args[0])

class Profile():
    """ Generic profile for image_util driver """
    def __init__(self, color_scale_transform = _firstObj, province_filter =
            _alwaysTrue, path_filter = _alwaysTrue):
        """
::color_scale_transform:: 
    returns a color tuple (e.g. (R,G,B,A)) after having inputs of *args:
    args[0] = default color for province label <tuple of 4 ints>
    args[1] = province number
    args[2] = province Terrain Value (Value)
    args[3] = image-xy location
    an example that turns non-'Large Province's black without touching the
    alpha channel would be:
        def myhighlight(x):
            scalar = int( 'Large Province' in terrain.TextFromValue(x[2]) )
            return (scalar*x[0][0], scalar*x[0][1], scalar*x[0][2], x[0][3])
        myProfile = Profile(color_scale_transform = myhighlight)

::province_filter:: 
    returns a bool after having inputs of *args. On True, the label is printed
            """
        self.color_scale_transform = color_scale_transform
        self.province_filter = province_filter
        self.path_filter = path_filter

def _sanitize_color(x):
    """ sanitize entries to 0-255 <int>"""
    def SE(k):
        """ sanitize entry to 0-255 <int>"""
        retval = int(k)
        if k < 0: retval = 0
        elif k > 255: retval = 255
        return retval

    return tuple([SE(xi) for xi in x])

# None of these examples will have the issue, but a color that gets modified
# out of the range of int(0-255) is going to cause errors - so we can sanitize
# it. could also use a decorator to do this, but meh.

# Province Filter
def thronesselection(*args):
    """ Example province_filter that returns True only on Throne sites """
    return bool('Throne' in terrain.TextFromValue(args[2]) )

# Color Scalar
def startsthronesfxn(*args):
    start = ('Start' in terrain.TextFromValue(args[2]) ) 
    throne = ('Throne' in terrain.TextFromValue(args[2]) )
    scalar = int(start or throne)
    scalarfxn = lambda k: scalar if k < 3 else 1
    if start:
        return _sanitize_color([scalarfxn(i) * args[0][i] for i in (0,1,2,3)])
    elif throne:
        return _sanitize_color([scalarfxn(i) * args[0][i] for i in (1,0,2,3)])
    else:
        return _sanitize_color([scalarfxn(i) * args[0][i] for i in (0,1,2,3)])

# Color Scalar
def thronesfxn(*args):
    scalar = int(bool('Throne' in terrain.TextFromValue(args[2]) ))
    scalarfxn = lambda k: scalar if k < 3 else 1
    return _sanitize_color([scalarfxn(i) * args[0][i] for i in range(4) ])

# Color Scalar
def startonlyfxn(*args):
    scalar = int(bool('Start' in terrain.TextFromValue(args[2]) ))
    scalarfxn = lambda k: scalar if k < 3 else 1
    return _sanitize_color([scalarfxn(i) * args[0][i] for i in range(4) ])

# Color Scalar
def specialsfxn(*args):
    scalar = int(len(set(('Many Sites','Fire sites','Air sites','Astral sites','Death sites','Nature sites', 'Blood sites', 'Holy sites',
        'Throne')).intersection(set(terrain.TextFromValue(args[2])))) > 0)
    scalarfxn = lambda k: scalar if k < 3 else 1
    return _sanitize_color([scalarfxn(i) * args[0][i] for i in range(4) ])

# Path Filter based on Province number
def connectsToThese(*args):
    """ If a path connects to one of these places, I want it drawn - maybe they're starting locations and you want to see what they connect to"""
    concerns = [112,154,176,162,208,22]
    return any([xi in concerns for xi in args[0]])

def availablestart(*args):
    return (args[-1] >= 1)

default = Profile()
thrones = Profile(color_scale_transform = thronesfxn)
starts = Profile(color_scale_transform = startonlyfxn)
startsthrones = Profile(color_scale_transform = startsthronesfxn,
        province_filter = availablestart)
specials = Profile(color_scale_transform = specialsfxn)
onlythrones = Profile(province_filter = thronesselection) 
specialconnection = Profile(path_filter = connectsToThese)

__all__ = ['default','editor', 
        'specials','thrones', 
        'onlythrones','startsthrones',
        'specialconnection']
