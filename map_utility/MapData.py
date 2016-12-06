#!/usr/bin/env python
''' Currently in design based on needs of community balanced with ease of implementation '''

VERSION = '0.1.0'

# constants
PeriodicNone = 0

PeriodicNS = 1

PeriodicEW = 2

PeriodicAll = PeriodicNS + PeriodicEW

import terrain

class MapData:
    def __init__(self, filename = None, allowoverwrite=False):
    # path/filename to the .map file (should be statable) 
    self.filename = filename

    # no saving or exporting, file data comes from something else
    self.allowoverwrite = False

    # number of total provinces
    self.numProvinces = -1

    # current text state of the map data
    self.maptextdata = ''

    def parse(self):
	pass 

    def update(self):
	pass

    def save(self):
	pass

    def isPeriodicNS(self):
	return terrain.checkPeriodicNS(self.maptextdata)

    def isPeriodicEW(self):
	return terrain.checkPeriodicEW(self.maptextdata)

    def checkPeriodic(self):
	return PeriodicNS * self.checkPeriodicNS() + PeriodicEW * self.checkPeriodicEW()

    def getConnections(self):
	self.connections = terrain.getConnections(mapfiledata)
	return self.connections

    def numProvinces(self):
	return self.numProvinces

    def getEncodedType(self, province_number):
	try:
	    retval = re.search('#terrain\s+{0:d}\s+(\S+)'.format(province_number), self.mapfiledata).groups(0)
	except:
	    e = Exception('Terrain unspecified')
	    print(e)
	    raise e
	return retval

    def isType(self, province_number, terrainKey):
	foundKey = re.search('#terrain\s+{0:d}\s+(\S+)'.format(province_number),self.mapfiledata).group(1)
	if type(terrainKey)==type(int):
	    cmpTerrainKey = terrainKey
	elif type(terrainKey)==type(str):
	    cmpTerrainKey = terrain.getBit(terrainKey)
