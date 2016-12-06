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
    def __init__(self, filename = None, allowoverwrite=False, maptextdata=''):
            # path/filename to the .map file (should be statable) 
        self.filename = filename

        # no saving or exporting, file data comes from something else
        self.allowoverwrite = False

        # number of total provinces
        self.terrain = list()

        # current text state of the map data
        self.maptextdata = maptextdata
        self.newmaptextdata = maptextdata


    def parseTerrains(self):
        terrain_data = sorted(re.findall('#terrain (\S+) (\S+)',self.maptextdata,re.MULTILINE+re.DOTALL),key=lambda x: int(x[0]))
        i = 1
        for province, value in terrain_data:
            assert(i == province)
            self.terrain.push_back(value)
            i = i+1
            
    def parseConnections(self):
        connection_data = set([(int(s[0]),int(s[1])) for s in re.findall('#neighbour (\S+) (\S+)',self.mapfiledata)])
        connection_types = re.findall('#neighbourspec (\S+) (\S+) ([124])',self.mapfiledata)

    def parse(self):
        self.parseTerrain()
        self.parseConnections()

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
    return len(self.terrain)

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
