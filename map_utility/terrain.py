import re, math
from operator import itemgetter
# needs to all be encapsulated to a Dom4Map class, but I ran out of time

# Terrain codes - plains doesn't set any bit?
# [BIT] [NUMBERVAL] [TEXTVAL]
terrainData = (\
('-',0,'Plains'), \
('0',1,'Small Province'), \
('1',2,'Large Province'), \
('2',4,'Sea'), \
('3',8,'Freshwater'), \
('4',16,'Mountain'), \
('5',32,'Swamp'), \
('6',64,'Waste'), \
('7',128,'Forest'), \
('8',256,'Farm'), \
('9',512,'Nostart'), \
('10',1024,'Many Sites'), \
('11',2048,'Deep Sea'), \
('12',4096,'Cave'), \
('13',8192,'Fire sites'), \
('14',16384,'Air sites'), \
('15',32768,'Water sites'), \
('16',65536,'Earth sites'), \
('17',131072,'Astral sites'), \
('18',262144,'Death sites'), \
('19',524288,'Nature sites'), \
('20',1048576,'Blood sites'), \
('21',2097152,'Holy sites'), \
('22',4194304,'Border Mountain'), \
('23',8388608,'Reserved for internal use'), \
('24',16777216,'Throne'), \
('25',33554432,'Start'))
terrainValues = list(map(itemgetter(1), terrainData))
terrainText = list(map(itemgetter(2), terrainData))
terrainBit = list(map(itemgetter(0), terrainData))

def terrainCode(flags):
    values = sum([terrainValues[I] for I in [terrainText.index(flag) for flag
        in flags]])

def ListTerrainCodes():
    for position, numvalue, textvalue in terrainData:
        print("{0:>2s} {1:>9d} {2:s}".format(position, numvalue, textvalue))

def rebuildMask(mask):
    number = 0
    i=0
    for k in mask[1::]:
        number = number + k * 2 ** i
        i = i+1
    return number

def breakdown(number):
    bitmask = [0 for x in range(27)]
    for i in range(25,-1,-1):
        try:
            if(i == int(math.log(number,2))):
                number = number - 2**i
                bitmask[i+1] = 1
        except:
            bitmask[0] = 0

    return bitmask
def interpretMask(mask):
    myvals = '''
-,0,Plains,
0,1,Small Province,
1,2,Large Province,
2,4,Sea,
3,8,Freshwater,
4,16,Mountain,
5,32,Swamp,
6,64,Waste,
7,128,Forest,
8,256,Farm,
9,512,Nostart,
10,1024,Many Sites,
11,2048,Deep Sea,
12,4096,Cave,
13,8192,Fire sites,
14,16384,Air sites,
15,32768,Water sites,
16,65536,Earth sites,
17,131072,Astral sites,
18,262144,Death sites,
19,524288,Nature sites,
20,1048576,Blood sites,
21,2097152,Holy sites,
22,4194304,Border Mountain,
23,8388608,Reserved for internal use,
24,16777216,Throne,
25,33554432,Start,'''.split(',')
    out = [myvals[3*i+2] for i in range(1,len(mask)) if mask[i]==1]
    return out

def getBit(key):
    myvals = '''
-,0,Plains,
0,1,Small Province,
1,2,Large Province,
2,4,Sea,
3,8,Freshwater,
4,16,Mountain,
5,32,Swamp,
6,64,Waste,
7,128,Forest,
8,256,Farm,
9,512,Nostart,
10,1024,Many Sites,
11,2048,Deep Sea,
12,4096,Cave,
13,8192,Fire sites,
14,16384,Air sites,
15,32768,Water sites,
16,65536,Earth sites,
17,131072,Astral sites,
18,262144,Death sites,
19,524288,Nature sites,
20,1048576,Blood sites,
21,2097152,Holy sites,
22,4194304,Border Mountain,
23,8388608,Reserved for internal use,
24,16777216,Throne,
25,33554432,Start,'''.split(',')
    return [myvals[3*i+2] for i in range(1,27)].index(key)+1

def setType(terrainNum,terrainKey,val,mapfiledata):
    results = re.findall("#terrain {0} (\S+)".format(terrainNum),mapfiledata)
    mask = breakdown(int(results[0]))
    mask[getBit(terrainKey)] = int(bool(val))
    results = re.sub("#terrain {0} (\S+)".format(terrainNum),"#terrain {0} {1}".format(terrainNum,rebuildMask(mask)),mapfiledata)
    return results

def flipType(terrainNum,terrainKey,mapfiledata):
    results = re.findall("#terrain {0} (\S+)".format(terrainNum),mapfiledata)
    mask = breakdown(int(results[0]))
    mask[getBit(terrainKey)] = (mask[getBit(terrainKey)]+1) % 2
    results = re.sub("#terrain {0} (\S+)".format(terrainNum),"#terrain {0} {1}".format(terrainNum,rebuildMask(mask)),mapfiledata)
    return results

def checkType(terrainNum,terrainKey,mapfiledata):
    results = re.findall("#terrain {0} (\S+)".format(terrainNum),mapfiledata)
    mask = breakdown(int(results[0]))
    return (terrainKey in interpretMask(mask))

# check periodicity
def checkPeriodicNS(mapfiledata): 
    return True if re.search('#vwraparound',mapfiledata) or re.search('#wraparound',mapfiledata) else False
def checkPeriodicEW(mapfiledata):
    return True if re.search('#hwraparound',mapfiledata) or re.search('#wraparound',mapfiledata) else False

def numProvinces(mapfiledata):
    return re.findall("#terrain (\S+) (\S+)",mapfiledata)

def getConnections(mapfiledata):
    # build connectivity by type
    # slower than it needs to be, could be done once and then sorted line by line?
    connections = dict()
    connections['all'] = set([(int(s[0]),int(s[1])) for s in re.findall("#neighbour (\S+) (\S+)",mapfiledata)])
    connections['river'] = set([(int(s[0]),int(s[1])) for s in re.findall("#neighbourspec (\S+) (\S+) 2",mapfiledata)])
    connections['mountain'] = set([(int(s[0]),int(s[1])) for s in re.findall("#neighbourspec (\S+) (\S+) 1",mapfiledata)])
    connections['info-only'] = set([(int(s[0]),int(s[1])) for s in re.findall("#neighbourspec (\S+) (\S+) 4",mapfiledata)])
    connections['land'] = filter(lambda x: x in connections['mountain'] or x in connections['river'], connections['all'])
    connections['aquatic']  = filter(lambda x: (checkType(x[0],'Sea',mapfiledata) and checkType(x[1],'Sea',mapfiledata)), connections['all'])
    connections['amphibious'] = filter(lambda x: (checkType(x[0],'Sea',mapfiledata) or checkType(x[1],'Sea',mapfiledata)), connections['all'].difference(connections['aquatic'],connections['info-only']))
    connections['normal'] = connections['all'].difference(connections['river'],connections['mountain'],connections['aquatic'],connections['amphibious'],connections['info-only'])
    return connections


__all__ = ["rebuildMask", "breakdown", "interpretMask", "getBit", "setType", "flipType", "checkType", "checkPeriodicNS", "checkPeriodicEW", "numProvinces", "getConnections"]
