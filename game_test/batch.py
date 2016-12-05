#!/usr/bin/env python
import re, os, sys, argparse
import subprocess as sp
import shutil, itertools
import numpy as np
from analyze_log import *

calculatedvalues = {-14:1.102, -13:1.344, -12:1.894, -11:2.405, -10:3.475, -9:4.574, -8:6.151, -7:8.1, -6:10.885, -5:14.289, -4:18.326, -3:23.479, -2:30.265, -1:37.684, 0:45.748, 1:54.118, 2:62.526, 3:69.888, 4:76.141, 5:81.813, 6:85.876, 7:89.219, 8:91.823, 9:93.833, 10:95.347, 11:96.5, 12:97.37, 13:98.139, 14:98.563}
def DRNback(percent):
	minkey = 200
	minvalue = 200
	for key,value in calculatedvalues.iteritems():
		newval = abs(percent-value)
		if newval < minvalue:
			minvalue = newval
			minkey = key
	return minkey

CONST_DOMINION_TURN_TIME=120.0 # timeout for a dominions turn
CONST_DOMINION_TURN_GREP_TIME=10.0 # timeout for a grep of a dominions turn

def shcmd(command):
	return sp.Popen(command,shell=True).wait()

def resultcmd(analysisfilename):
	return analyze_log(['--spell',"Master Enslave", analysisfilename])

if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-t','--threads',help="number of processes in the pool",type=int,default=10)
	parser.add_argument('--debug',help="turn on debug mode",action='store_true')
	parser.add_argument('--only-analyze',help="turn on debug mode",action='store_true')
	parser.add_argument('-N',help="number of tests to run",type=int,default=13)
	parser.add_argument('gamefolder',help="gamefolder or glob of gamefolders",type=str,nargs='+')
	parser.add_argument('--domgame',help="gamefolder or glob of gamefolders",type=str,default='~/.steam/steam/steamapps/common/Dominions4/dom4.sh')
	parsed = parser.parse_args()

	if parsed.debug: print parsed

	command = list()
	analysisfile = list()
	for basegamename in parsed.gamefolder:
		for i in range(parsed.N):
			gamename = re.sub("_base$","_%02d" % (i),basegamename)
			if not parsed.only_analyze: 
				shutil.rmtree(gamename,ignore_errors=True)
				shutil.copytree(basegamename,gamename)
				command.append(parsed.domgame+' --textonly --host -dddd '+gamename+' > '+os.path.join(gamename,'analysis.txt'))
			analysisfile.append(os.path.join(gamename,'analysis.txt'))

	import multiprocessing as mp

	pool = mp.Pool(processes=parsed.threads)
	if not parsed.only_analyze:
		res = pool.map_async(shcmd,command,1)
		res.wait(timeout=len(command)*CONST_DOMINION_TURN_TIME/parsed.threads)

	res = pool.map_async(resultcmd,analysisfile,parsed.N)
	answers = res.get(timeout=len(analysisfile)*CONST_DOMINION_TURN_GREP_TIME/parsed.threads)
	results = dict()
	for key, result in zip(analysisfile,answers):
		keyname = re.sub("_[0-9]+$","",os.path.dirname(key))
		try:
			results[keyname].append(result)
		except:
			results[keyname] = [result]

	for key,result in results.iteritems():
		results[key] = {'data':result,
				'mean':np.mean(result),
				'median':np.median(result),
				'max':np.max(result),
				'min':np.min(result),
				'std':np.std(result)}

	iprinter = itertools.imap(lambda x, y: (x,y['mean']/10,y['std']/10), results.keys(), results.values())

	from operator import itemgetter

	printer = sorted(list(iprinter),key=itemgetter(1))
	print "%-15s %15s %8s   %5s" %("scenario","mean % enslaved","est. DRN","std %")
	for l in printer:
		print "%-15s     %5.2f      %+3d      %5.2f" % (l[0],l[1],DRNback(l[1]),l[2])

