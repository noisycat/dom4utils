# dom4utils

##WHAT:

An ever expanding set of pythonic utilities for Dominions 4.

---

### teamOrg.py

Provides a function by which to sort and match various team combination rankings. Not too complicated.

### image_util.py

Perhaps my most useful function, this allows you to load a dominions4 .map file and its corresponding image and run various types of analysis on it, as well as print off types of connections graphically. This is great when designing maps or for providing global overlays for team discussions.

### loadData.py

Allows you to have access to all the data in the dom4modinspector through python interfaces and methods. There's a lot of hardcoded stuff in that project that hasn't been and may not be replicated here - but if you're looking to comb through CSV files as dictionaries, this will help you out with that! Useful for trying to min/max various unit comparisons.

---

##INSTALLATION REQUIREMENTS

Still very manual approach - to use this without installing it, just prepend PYTHONPATH with this directory location, as well as the location of dom4inspector

You'll still need PIL, numpy, and others.
