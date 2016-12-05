#!/usr/bin/env python
import re, sys, argparse
''' analyze dom4 log file '''

def analyze_log(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-s','--spell',help="spell name to search for")
	parser.add_argument('filename',help="file name to analyze")
	parser.add_argument('--debug',help="turn on debug mode",action='store_true')
	parsed = parser.parse_args(args)
	''' currently works for Master Enslave, because that's what I'm interested in '''

	if parsed.debug: print parsed

	filedata = open(parsed.filename,'r')
	filetext = filedata.read()
	filedata.close()
	results = re.search(r"^castspell:\s*\S+\s+\S+\s+\(%s\)(.*?)\s+castspell done$" % (parsed.spell),filetext,re.DOTALL+re.MULTILINE)
	victory = filter(lambda x: not re.search("friendly negated",x), re.split("affectvic",results.group(1))[1:])
	converts = re.search(r"^castspell:\s*\S+\s+\S+\s+\(%s\).*?\s+castspell done\s*(.*?)turn " % (parsed.spell),filetext,re.DOTALL+re.MULTILINE)
	precursor = re.findall("^\S+ striking with .*?$",converts.group(1),re.MULTILINE)
	num_converts = len(re.findall("^Create squad .*?$",converts.group(1),re.MULTILINE))
	return num_converts

if __name__ == "__main__":
	print analyze_log(sys.argv)
