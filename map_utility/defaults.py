# LICENSE CHOICE
# dom4defaults - provides paths and dom4 specific information
import sys
try:
	import dom4defaults as dom4
except ImportError as e:
	sys.stderr.write("Error: Change the environment variable $PYTHONPATH and try again\nbash:\n\texport PYTHONPATH=$PWD/common_settings:$PWD/common_utility:$PYTHONPATH\n")
	raise e

import defaultcolors as colors

font = {'Darwin':'Arial.ttf',
'Windows':'Arial.ttf',
'Linux':'/usr/share/fonts/liberation/LiberationSans-Regular.ttf'} # maybe this works? maybe it doesn't. rage

outfile = "mapname+'_connections.png'"
