#!/usr/bin/env python
__author__="Charles Lena"
''' Currently in design based on needs of community balanced with ease of implementation '''

from __builtin__ import open as fopen
import os, copy, re

VERSION = '0.1.0'

# constants
PeriodicNone = 0
PeriodicNS = 1
PeriodicEW = 2
PeriodicAll = PeriodicNS + PeriodicEW

class _defaultsObj(object):
    def __init__(self):
        self.header="""-- 
-- Map file for Dominions 4
-- 
-- Illwinter Game Design
-- www.illwinter.com
-- 
-- Textinfo Generated with dom4utils
"""
        self.title="newMap"
        self.domversion=350

debug_var = 0
_defaults = _defaultsObj()

import terrain
from Province import Province

# registers all the various patterns used by the manual to describe the text style
# these can be templated by entry: e.g. bitmask_nbr: bitmask_nbr0, bitmask_nbr1,...
_var_patterns = {'terrainID':'[0-9]+',
        'connectionType':'[124]',
        'bitmask_nbr':'[0-9]+',
        'entireline':'.*?',
        'nation_nbr':'[0-9]+',
        'province_nbr':'[0-9]+',
        'victory_nbr':'[1-7]',
        'unrest_nbr' : '[1-4]?[0-9]?[0-9]',
        'population_nbr' : '[1-5]?[0-9]+',
        'string' : '".*?"',
        'cin':'(',
        'cout':')'}


# these don't change per entry
_static_patterns = {
        'sep':r'\s+',
        'firstchar':r'^',
        'lastchar':r'$',
        'BLE':r'\s*?'}

_output_patterns = {'cin':'', 'cout':'',
        'cin0':'', 'cout0':'',
        'cin1':'', 'cout1':'',
        'cin2':'', 'cout2':'',
        'sep':' ',
        'firstchar':'\n',
        'lastchar':'',
        'BLE':''}

# every line that can be a valid map line will go in here
_valid_lines = {'comment':'{firstchar}--{cin0}{comment}{cout0}{BLE}{lastchar}',
'empty':'{firstchar}{BLE}{lastchar}',
'domversion':'{firstchar}#domversion{sep}{cin0}{domversion}{cout0}{BLE}{lastchar}',
'dom2title':'{firstchar}#dom2title{sep}{cin0}{dom2title}{cout0}{BLE}{lastchar}',
'imagefile':'{firstchar}#imagefile{sep}{cin0}{imagefile}{cout0}{BLE}{lastchar}',
'description':'{firstchar}#description{sep}{cin0}{description}{cout0}{BLE}{lastchar}'}

# every line that modifies the currently active province goes in here
_special_lines = dict()

def _template_line(command,*types):
    retval = '{firstchar}#%s' % (command)
    count = dict()
    for i in range(len(types)):
        retval = retval + '{sep}{cin%d}{%s%d}{cout%d}' % (i,types[i],count.get(types[i],0),i)
        count[types[i]] = count.get(types[i],0)+1
    retval = retval +'{BLE}{lastchar}'
    return retval

for tag in ['scenario',
        'wraparound',
        'horwrap',
        'vertwrap',
        'nohomelandnames',
        'nonamefilter']:
    _valid_lines[tag] = _template_line(tag)

for tag in [('allowedplayer','nation_nbr'),
        ('start','province_nbr'),
        ('nostart','province_nbr'),
        ('cannotwin','nation_nbr')]:
    _valid_lines[tag[0]] = _template_line(tag[0],tag[1])

for tag in [('landname','province_nbr','string'),
        ('terrain','province_nbr','bitmask_nbr'),
        ('victorypoints','province_nbr','victory_nbr'),
        ('neighbour','province_nbr','province_nbr'),
        ('neighbourspec','province_nbr','province_nbr','connectionType'),
            ('victorycondition','victory_condition_nbr','victory_attribute'),
            ('allies','nation_nbr','nation_nbr'),
            ('specstart','nation_nbr','province_nbr'),
            ('computerplayer','nation_nbr','difficulty_nbr')]:
    _valid_lines[tag[0]] = _template_line(tag[0],*tuple(tag[1:]))

_valid_lines['maptextcol'] = _template_line('maptextcol',*tuple(4*('color_norm_nbr',)))

# Specials
for tag in [('lab',tuple()),
        ('temple',tuple()),
        ('killfeatures',tuple())]:
    _valid_lines[tag[0]] = _template_line(tag[0],tag[1])
    _special_lines[tag[0]] = _valid_lines[tag[0]]

# province-special
for tag in [('land','province_nbr'),
        ('setland','province_nbr'),
        ('poptype','poptype_nbr'),
        ('feature','entireline'),
        ('knownfeature','entireline'),
        ('fort','fort_nbr'),
        ('unrest','unrest_nbr'),
        ('defence','defence_nbr'),
        ('population','population_nbr'),
        ('skybox','entireline'),
        ('batmap','entireline'),
        ('owner','nation_nbr')]:
    _valid_lines[tag[0]] = _template_line(tag[0],tag[1])
    _special_lines[tag[0]] = _valid_lines[tag[0]]

# province-commander-special
for tag in [('commander','entireline'),
        ('comname','entireline'),
        ('bodyguards','nbr','entireline'),
        ('units','nbr','entireline'),
        ('xp','nbr'),
        ('randomequip','rich_nbr'),
        ('additem','entireline'),
        ('clearmagic',()),
        ('mag_fire','level_nbr'),
        ('mag_air','level_nbr'),
        ('mag_water','level_nbr'),
        ('mag_earth','level_nbr'),
        ('mag_astral','level_nbr'),
        ('mag_death','level_nbr'),
        ('mag_nature','level_nbr'),
        ('mag_blood','level_nbr'),
        ('mag_priest','level_nbr')]:
    _valid_lines[tag[0]] = _template_line(tag[0],tag[1])
    _special_lines[tag[0]] = _valid_lines[tag[0]]
# god-special

_valid_lines['groundcol'] = _template_line('groundcol',*tuple(3*('color_nbr',)))
_valid_lines['rockcol'] = _template_line('rockcol',*tuple(3*('color_nbr',)))
_valid_lines['fogcol'] = _template_line('fogcol',*tuple(3*('color_nbr',)))
_special_lines['groundcol'] = _valid_lines['groundcol']
_special_lines['rockcol'] = _valid_lines['rockcol']
_special_lines['fogcol'] = _valid_lines['fogcol']

_standard_search_pattern = copy.deepcopy(_static_patterns)
_standard_search_pattern.update({pattern+str(num):_var_patterns[pattern] for num in range(4) for pattern in _var_patterns})

def new(pathObj, allowoverwrite, title, imagefile, domversion, description, header):
    retval = MapData(filename=pathObj, title=title, imagefile=imagefile, domversion=domversion,
    description=description, header="""\n--\n-- Map file for Dominions 4
--\n-- Illwinter Game Design\n-- www.illwinter.com\n--
-- Textinfo Generated with dom4utils\n""")
    return retval

def fromstring(mapfiledata):
    retval = MapData(mapfiledata=mapfiledata)
    return retval

def open(path):
    retval = MapData(filename=path,status='old')
    return retval

class MapData:
    def __init__(self, filename = None, status = 'unknown', imagefile = None, title = None,
            domversion = 428, description = None, maptextdata = None, header = None):
        self.__inits = (not filename, not imagefile, not title, not description, not maptextdata, not header)

        self.filename = 'newMap.map' if not filename else filename
        self.status = status
        self.maptextdata = maptextdata
        self.header = _defaults.header if not header else header
        self.periodic = PeriodicNone

        # these values are required for valid map - even the Null Map
        self.dom2title = title
        self.imagefile = imagefile
        self.Image = None
        self.domversion = domversion
        self.description = description

        # raw data storage
        self.provinces = list()
        self.connections = list()
        self.connection_data = dict()
        self.connection_types = dict()
        self.specials = list()

        if self.__inits == (False, True, True, True, True, True):
            if self.status == 'old':
                with fopen(self.filename,'r') as filehandle:
                    self.maptextdata = filehandle.read()
                    self.maptextdata_lines = self.maptextdata.split('\n')
                self.parse()

            if self.status == 'new':
                # It's a little bit of file safety
                try:
                    stat = os.stat(filename)

                except:
                    # Must not be there
                    if status=='new':
                        stat = None

                if not stat:
                    e = Exception('IOError','{filename} declared as new, should not exist'.format(filename=filename))
                    raise e

            if (self.status == 'new' or self.status == 'unknown'):
                # new, unknown - init maptextdata, wait for fill
                self.maptextdata = ''


        if self.__inits == (True, True, True, True, False, True):
            # assign default filename, parse mapfiledata
            self.maptextdata = maptextdata
            self.maptextdata_lines = self.maptextdata.split('\n')
            self.parse()

        # current text state of the map data
        self.newmaptextdata = maptextdata

    def load_mapdata(self):
        pass

    def load_image(self):
        pass

    def Import(self, path):
        pass

    def Export(self,filelike,new=True):
        # header
        if new:
            filelike.write(self.header)
            filelike.write("""\n-- Title and image file""")
            filelike.write(_valid_lines['dom2title'].format(dom2title=self.dom2title,**_output_patterns))
            filelike.write(_valid_lines['imagefile'].format(imagefile=self.imagefile,**_output_patterns))
            filelike.write(_valid_lines['domversion'].format(domversion=self.domversion,**_output_patterns))
            if self.periodic == PeriodicNS: 
                filelike.write(_valid_lines['vertwrap'].format(**_output_patterns))

            elif self.periodic == PeriodicEW: 
                filelike.write(_valid_lines['horwrap'].format(**_output_patterns))

            elif self.periodic == PeriodicAll: 
                filelike.write(_valid_lines['wraparound'].format(**_output_patterns))

            filelike.write(_valid_lines['description'].format(description=self.description,**_output_patterns))

            filelike.write("""\n\n-- Province names/terrains""")
            for province in self.provinces:
                filelike.write(_valid_lines['terrain'].format(province_nbr0=province.idnum,bitmask_nbr0=province.value, **_output_patterns))

            filelike.write("""\n\n-- Province neighbours""")
            keys = sorted(self.connection_data.keys(), key=lambda x: int(x[0])*len(self.provinces)+int(x[1]))
            for connection in keys:
                filelike.write(_valid_lines['neighbour'].format(province_nbr0=connection[0],province_nbr1=connection[1],**_output_patterns))
                if self.connection_data[connection] != 0: 
                    filelike.write(_valid_lines['neighbourspec'].format(province_nbr0=connection[0],province_nbr1=connection[1],connectionType0=self.connection_data[connection],**_output_patterns))

            filelike.write("""\n\n-- Special per province commands""")
            # link the specials to the main map
            # link the prov_specials to the territory number since that's how they're processed
            filelike.write("""\n\n--""")
        else:
            filelike.write(self.maptextdata)

    def seeCenters(self):
        for province in self.province:
            yield province.center

    def insertProvince(self,iProv):
        self.provinces.insert(iProv.idnum,iProv)
        for province in reversed(self.provinces[iProv.idnum-1:]):
            province.nextid = province.idnum+1
            self.update('province_nbr',province.idnum,province.nextid)
        formatter = copy.deepcopy(_standard_search_pattern)
        del formatter['province_nbr0']
        def repl_fxn(matchobj):
            l = matchobj.group(0)
            l = l+_valid_lines['terrain'].format(province_nbr0=iProv.idnum,bitmask_nbr0=iProv.value,**_output_patterns)
            return l
        search = _valid_lines['terrain'].format(province_nbr0=iProv.idnum-1,**formatter)
        self.maptextdata = re.sub(search, repl_fxn, 
                self.maptextdata, count=0, flags=re.M+re.DOTALL)

        # reparsing every step to make sure we're not doing something dumb in memory reference - also we haven't checked against
        # scenario stuff yet
        self.parse()

    def removeProvince(self,iProv):
        self.provinces.pop(iProv.idnum-1)
        self.update('province_nbr',iProv.idnum, -1, delete_records=True)

        for province in self.provinces[iProv.idnum-1:]:
            province.nextid = province.idnum-1
            self.update('province_nbr',province.idnum,province.nextid)

        # reparsing every step to make sure we're not doing something dumb in memory reference - also we haven't checked against
        # scenario stuff yet
        self.parse()



    def isValid(self):
        # has dom2title
        # has imagefile
        # has domversion 
        # has description
        return False

    def updateProvinceID(self):
        pass

    def parseOther(self):
        formatter = copy.deepcopy(_var_patterns)
        formatter.update(_static_patterns)
        captures = {'cin0':_var_patterns['cin'],'cout0':_var_patterns['cout']}
        formatter.update(captures)
        search = _valid_lines['dom2title'].format(dom2title=_var_patterns['entireline'],**formatter)
        self.dom2title = re.findall(search,self.maptextdata,re.DOTALL+re.MULTILINE)[0]

        search = _valid_lines['imagefile'].format(imagefile=_var_patterns['entireline'],**formatter)
        self.imagefile = re.findall(search,self.maptextdata,re.DOTALL+re.MULTILINE)[0]

        search = _valid_lines['domversion'].format(domversion=_var_patterns['entireline'],**formatter)
        self.domversion = re.findall(search,self.maptextdata,re.DOTALL+re.MULTILINE)[0]

        self.periodic = PeriodicNone
        search = _valid_lines['horwrap'].format(**formatter)
        self.periodic = PeriodicEW if re.search(search,self.maptextdata,re.DOTALL+re.MULTILINE) else self.periodic

        search = _valid_lines['vertwrap'].format(**formatter)
        self.periodic = PeriodicNS if re.search(search,self.maptextdata,re.DOTALL+re.MULTILINE) else self.periodic

        search = _valid_lines['wraparound'].format(**formatter)
        self.periodic = PeriodicAll if re.search(search,self.maptextdata,re.DOTALL+re.MULTILINE) else self.periodic

        search = _valid_lines['description'].format(description=_var_patterns['entireline'],**formatter)
        self.description = re.findall(search,self.maptextdata,re.DOTALL+re.MULTILINE)[0]

    def parseProvinces(self):
        formatter = copy.deepcopy(_var_patterns)
        formatter.update({'cin0':'(', 'cout0':')', 'province_nbr0':_var_patterns['province_nbr'],
                'cin1':'(', 'cout1':')', 'bitmask_nbr0':_var_patterns['bitmask_nbr']})
        formatter.update(_static_patterns)
        search = _valid_lines['terrain'].format(**formatter)
        find_data = re.findall(search,self.maptextdata,re.MULTILINE+re.DOTALL)
        terrain_data = [(int(y[0]),int(y[1])) for y in sorted(find_data,key=lambda x: int(x[0]))]
        i = 1
        for province, value in terrain_data:
            if i < 15: print i, province, value
            try:
                assert(i == int(province))
            except Exception as e:
                print("Should have had all terrain present - missing terrain")
                raise e
            i = i+1

        self.provinces = [Province(province,value) for province,value in terrain_data]

    def parseConnections(self):
        formatter = copy.deepcopy(_static_patterns)
        formatter.update({'cin0':'(', 'cout0':')', 'province_nbr0':_var_patterns['terrainID'], 
                'cin1':'(', 'cout1':')', 'province_nbr1':_var_patterns['terrainID'],
                'cin2':'(', 'cout2':')', 'connectionType0':_var_patterns['connectionType']})
        search = _valid_lines['neighbour'].format(**formatter)
        self.connection_data = {(int(s[0]),int(s[1])):0 for s in re.findall(search,self.maptextdata,re.DOTALL+re.MULTILINE)}
        search = _valid_lines['neighbourspec'].format(**formatter)
        self.connection_types = {(int(s[0]),int(s[1])):int(s[2]) for s in re.findall(search,self.maptextdata,re.DOTALL+re.MULTILINE)}
        self.connection_data.update(self.connection_types)

    def parse(self):
        self.parseOther()
        self.parseProvinces()
        self.parseConnections() 

    def update(self,attribute,oldvalue,newvalue,delete_records=False):
        ''' enables finding attributes and updating their values across the entirety of the self.maptextdata '''
        keys = list()
        for key,line in _valid_lines.viewitems():
            m = re.findall('{('+attribute+')([0-9]+)}',line,re.M+re.DOTALL)
            if m: keys.append((key,m))

        formatter = copy.deepcopy(_standard_search_pattern)
        for num in range(4): 
            formatter['cin{0:d}'.format(num)] = ''
            formatter['cout{0:d}'.format(num)] = ''
        formatter['firstchar'] = "("+formatter['firstchar']
        formatter['lastchar'] = formatter['lastchar']+")"
        baseline_formatter = copy.deepcopy(formatter)
        formatter = copy.deepcopy(baseline_formatter)
        finds = list()
        for key in keys:
            for searchterm, num in key[1]:
                formatter.update({pattern+num:")(" for pattern in _var_patterns if pattern == 'cin' or pattern=='cout'})
                #print "st",searchterm
                _mod_line = _valid_lines[key[0]].replace('{'+searchterm+num+'}',str(oldvalue))
                #print _mod_line
                search = _mod_line.format(**formatter)
                #print search
                def repl_fxn(matchobj):
                    if delete_records:
                        return ''
                    else:
                        l = matchobj.expand("\g<1>{newval}\g<3>")
                        return l.format(newval=newvalue)

                self.maptextdata = re.sub(search, repl_fxn, self.maptextdata, count=0,flags=re.M+re.DOTALL)
                finds.append(search)
                # turn it off
                formatter.update({pattern+num:"" for pattern in _var_patterns if pattern == 'cin' or pattern=='cout'})

        return finds

    def save(self):
        pass

    def isPeriodic(self):
        return (self.periodic != PeriodicNone)

    def isPeriodicNS(self):
        return (self.periodic == PeriodicNS)

    def isPeriodicEW(self):
        return (self.periodic == PeriodicEW)

    def checkPeriodic(self):
        return self.periodic

    def getConnections(self):
        self.connections = terrain.getConnections(self.maptextdata)
        return self.connections

    def numProvinces(self):
        return len(self.provinces)

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

def __txtdiff(lines1,lines2):
    i = 0
    for l1,l2 in zip(lines1,lines2):
        m = re.sub(l1,'',l2,count=0,flags=re.M+re.DOTALL)
        if m != '': print i,l1,l2,m
        i = i+1

if __name__ == '__main__':
    print("Testing MapData.py")
    M = open(os.path.expanduser('~/dominions4/maps/hexawyr.map'))
    with fopen(os.path.expanduser('~/dominions4/maps/hexawyr_copy.map'),'w') as outfile:
        M.Export(outfile,new=False)
    with fopen(os.path.expanduser('~/dominions4/maps/hexawyr_copy2.map'),'w') as outfile:
        M.Export(outfile)
    M.removeProvince(Province(10,-1))
    with fopen(os.path.expanduser('~/dominions4/maps/hexawyr_no10.map'),'w') as outfile:
        M.Export(outfile,new=False)

    '''
    txt = M.maptextdata
    k = M.update('province_nbr',10,11)
    txt_change = M.maptextdata
    k = M.update('province_nbr',11,10)
    txt2 = M.maptextdata
    __txtdiff(txt.split('\n'),txt2.split('\n'))
    __txtdiff(txt.split('\n'),txt_change.split('\n'))
    '''
