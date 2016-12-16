# dom4utils

suite of Tools for working with Dominions 4.

##WHAT:

An ever expanding set of pythonic utilities for Dominions 4.

---

### teamOrg.py

Provides a function by which to sort and match various team combination rankings. Not too complicated.

### map_analyzer.py

Perhaps my most useful function, this allows you to load a dominions4 .map file and its corresponding image and run various types of analysis on it, as well as print off types of connections graphically. This is great when designing maps or for providing global overlays for team discussions.

### loadData.py

Allows you to have access to all the data in the dom4modinspector through python interfaces and methods. There's a lot of hardcoded stuff in that project that hasn't been and may not be replicated here - but if you're looking to comb through CSV files as dictionaries, this will help you out with that! Useful for trying to min/max various unit comparisons.

---

##INSTALLATION REQUIREMENTS

###Goal: Crossplatform support for Windows, Linux, Mac OS X

###Dependencies:

1) Python >= 2.6 (https://www.python.org/)
2) ImageMagick (https://www.imagemagick.org/)
3) pillow (https://www.python-pillow.org/)
4) wand (http://docs.wand-py.org/)
5) Dominions 4 csv data - see https://github.com/larzm42/dominions-tools or the modinspector. This requirement is likely to change

###Use:

Still very manual approach - to use this without installing it, just prepend PYTHONPATH with this directory location, as well as the location of dom4inspector

You'll still need PIL, numpy, and others.
