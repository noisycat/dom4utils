# LICENSE CHOICE
# dom4defaults - provides paths and dom4 specific information
try:
	import dom4defaults as dom4
except ImportError as e:
	print(str(e))
	print("Change the environment variable PYTHONPATH, didn't you? Do that and try again")
	raise e

import defaultcolors as colors

font = {'Darwin':'Ariel.ttf',
'Windows':'Ariel.ttf',
'Linux':'/usr/share/fonts/liberation/LiberationSans-Regular.ttf'} # maybe this works? maybe it doesn't. rage
