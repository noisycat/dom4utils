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
-- Textinfo Modified with @noisycat/dom4utils
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
        'nbr':'[0-9]+',
        'color_nbr':'[1-2]?[0-9]?[0-9]',
        'color_norm_nbr':'[0-9\.]+',
        'bitmask_nbr':'[0-9]+',
        'entireline':'.*?',
        'paragraph':'".*?"',
        'nation_nbr':'[0-9]+',
        'province_nbr':'[0-9]+',
        'victory_nbr':'[1-7]',
        'victory_condition_nbr':'[1-7]',
        'victory_attribute':'[1-7]',
        'level_nbr':'[1-9][0]?',
        'unrest_nbr' : '[1-4]?[0-9]?[0-9]',
        'population_nbr' : '[1-5]?[0-9]+',
        'poptype_nbr' : '[1-5]?[0-9]+',
        'defence_nbr':'[0-9]+',
        'rich_nbr':'[0-9]+',
        'difficulty_nbr':'[0-9]+',
        'fort_nbr':'[0-9]{1,2}',
        'string' : '"?.*?"?',
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
        'cin3':'', 'cout3':'',
        'sep':' ',
        'firstchar':'\n',
        'lastchar':'',
        'BLE':''}

# every line that can be a valid map line will go in here
def landnameImport(matchObj,mapDataObj,curObj):
    try:
        setattr(mapDataObj.provinces[int(matchObj.group(1))-1],'landname',matchObj.group(2))
    except:
        mapDataObj.provinces.append(Province(matchObj.group(1), 0))
        setattr(mapDataObj.provinces[int(matchObj.group(1))-1],'landname',matchObj.group(2))

def terrainImport(matchObj,mapDataObj,curObj):
    try:
        setattr(mapDataObj.provinces[int(matchObj.group(1))-1],'value', matchObj.group(2))
    except:
        mapDataObj.provinces.append(Province(matchObj.group(1), matchObj.group(2)))

def neighbourspecImport(matchObj,mapDataObj,curObj):
    old = (int(matchObj.group(2)),0)
    new = (int(matchObj.group(2)),matchObj.group(3))
    mapDataObj.provinces[int(matchObj.group(1))-1].neighbours[mapDataObj.provinces[int(matchObj.group(1))-1].neighbours.index(old)] = new

def _alwaysTrue(*args):
    return True

def doNothing(*args):
    return None

focus_functions = dict()
import_functions = dict()
_valid_lines = dict()

# every line that modifies the currently active province goes in here
_special_lines = dict()

def _template_line(command, args, importfxn=None, focusfxn=None, validator=None, specialcommand=False):
    global import_functions, focus_functions
    importfxn = importfxn or doNothing
    import_functions[command] = importfxn
    focusfxn = focusfxn or doNothing 
    focus_functions[command] = focusfxn
    validator = validator or _alwaysTrue
    retval = '{firstchar}#%s' % (command) if not specialcommand else '{firstchar}%s' % (command)
    count = dict()
    for i in range(len(args)):
        retval = retval + '{sep}{cin%d}{%s%d}{cout%d}' % (i,args[i],count.get(args[i],0),i)
        count[args[i]] = count.get(args[i],0)+1
    retval = retval +'{BLE}{lastchar}'
    return retval

for tag in [
        ('',(),lambda x,y,z: y.emptylines.append(y.curlinenum), None, None),
        ('--',('entireline',),lambda x,y,z: y.comments.append((y.curlinenum,x.group(1))),None,None)]:
    _valid_lines[tag[0]] = _template_line(tag[0],tag[1],tag[2],tag[3],tag[4],specialcommand=True).replace('{sep}','')

for tag in [('scenario',(),lambda x,y,z: setattr(y,'isScenario',True),None,None),
        ('wraparound',(), lambda x,y,z: setattr(y,'periodic',PeriodicAll),None,None),
        ('horwrap',(), lambda x,y,z: setattr(y,'periodic',PeriodicEW),None,None),
        ('vertwrap',(), lambda x,y,z: setattr(y,'periodic',PeriodicNS),None,None),
        ('nohomelandnames',(), lambda x,y,z: setattr(y,'nohomelandnames',True),None,None),
        ('nonamefilter',(), lambda x,y,z: setattr(y,'nonamefilter',True),None,None),
        ('domversion',('nbr',),lambda x,y,z: setattr(y,'domversion', x.group(1)), None,None),
        ('dom2title',('entireline',), lambda x,y,z: setattr(y,'dom2title',x.group(1)),None,None),
        ('imagefile',('string',), lambda x,y,z: setattr(y,'imagefile',x.group(1)),None,None),
        ('description',('paragraph',), lambda x,y,z: setattr(y,'description',x.group(1)),None,None),
        ('allowedplayer',('nation_nbr',), lambda x,y,z: y.allowedplayer.append(x.group(1)), None,None),
        ('start',('province_nbr',), lambda x,y,z: y.adhoc_starts.append(x.group(1)), None,None),
        ('nostart',('province_nbr',), lambda x,y,z: y.adhoc_nostart.append(x.group(1)), None,None),
        ('cannotwin',('nation_nbr',), lambda x,y,z: y.cannotwin.append(x.group(1)), None,None),
        ('landname',('province_nbr','string'), landnameImport, None, None),
        ('terrain',('province_nbr','bitmask_nbr'), terrainImport, None, None),
        ('victorypoints',('province_nbr','victory_nbr'), lambda x,y,z: setattr(y,'victorypoints',x.groups()),None,None),
        ('neighbour',('province_nbr','province_nbr'), lambda x,y,z: y.provinces[int(x.group(1))-1].neighbours.append((int(x.group(2)), 0)), None, None),
        ('neighbourspec',('province_nbr','province_nbr','connectionType'), neighbourspecImport, None, None),
        ('victorycondition',('victory_condition_nbr','victory_attribute'), None,None,None),
        ('allies',('nation_nbr','nation_nbr'), lambda x,y,z: y.allies.append(x.groups()), None,None),
        ('specstart',('nation_nbr','province_nbr'), lambda x,y,z: y.specstart.append(x.groups()), None,None),
        ('computerplayer',('nation_nbr','difficulty_nbr'), lambda x,y,z: y.computerplayer.append(x.groups()), None,None),
        ('maptextcol',tuple(4*('color_norm_nbr',),), lambda x,y,z: setattr(y,'maptextcol',x.groups()),None,None)]:
    _valid_lines[tag[0]] = _template_line(tag[0],tag[1],tag[2],tag[3],tag[4])

for tag in [
        ]:
    _valid_lines[tag[0]] =  _template_line(tag[0],tag[1],tag[2],tag[3],tag[4])
    _special_lines[tag[0]] = _valid_lines[tag[0]]

# province-special
for tag in [
        ('land',('province_nbr',),lambda x, y, z: setattr(y.provinces[int(x.group(1))-1],'land',True), lambda x, y, z: y.provinces[int(x.group(1))-1],None),
        ('setland',('province_nbr',),lambda x, y, z: setattr(y.provinces[int(x.group(1))-1],'setland',True), lambda x, y, z: y.provinces[int(x.group(1))-1],None),
        ('lab',(), lambda x,y,z: setattr(z,'lab',True), None, None),
        ('temple',(), lambda x,y,z: setattr(z,'temple',True), None,None),
        ('killfeatures',(), lambda x, y, z: setattr(z,'killfeatures',True),None,None),
        ('poptype',('poptype_nbr',), lambda x,y,z: setattr(z,'poptype',x.group(1)),None,None),
        ('feature',('entireline',), lambda x,y,z: setattr(z,'feature',x.group(1)),None,None),
        ('knownfeature',('entireline',), lambda x,y,z: z.knownfeature.append(x.group(1)),None,None),
        ('fort',('fort_nbr',), lambda x,y,z: setattr(z,'fort',x.group(1)),None,None),
        ('unrest',('unrest_nbr',), lambda x,y,z: setattr(z,'unrest',x.group(1)),None,None),
        ('defence',('defence_nbr',), lambda x,y,z: setattr(z,'defence',x.group(1)),None,None),
        ('population',('population_nbr',), lambda x,y,z: setattr(z,'population',x.group(1)),None,None),
        ('skybox',('entireline',), lambda x,y,z: setattr(z,'skybox',x.group(1)),None,None),
        ('batmap',('entireline',), lambda x,y,z: setattr(z,'batmap',x.group(1)),None,None),
        ('owner',('nation_nbr',),lambda x,y,z: setattr(z,'owner',x.group(1)),None,None),
        ('groundcol',tuple(3*('color_nbr',)), lambda x,y,z: setattr(z,'groundcol',x.groups()),None,None),
        ('rockcol',tuple(3*('color_nbr',)), lambda x,y,z: setattr(z,'rockcol',x.groups()),None,None),
        ('fogcol',tuple(3*('color_nbr',)), lambda x,y,z: setattr(z,'fogcol',x.groups()),None,None)]:
    _valid_lines[tag[0]] = _template_line(tag[0],tag[1],tag[2],tag[3],tag[4])
    _special_lines[tag[0]] = _valid_lines[tag[0]]

# province-commander-special
for tag in [
        ('commander',('entireline',), lambda x, y, z: z.commanders.append(Commander(x.group(1))), lambda x, y, z: z.commanders[-1], None),
        ('clearmagic',(), lambda x,y,z: setattr(z,'clearmagic',True),None,None),
        ('comname',('entireline',), lambda x, y, z: setattr(z,'comname',x.group(1)),None,None),
        ('bodyguards',('nbr','entireline'), lambda x, y, z: z.bodyguards.append((x.group(1),x.group(2))), None,None),
        ('units',('nbr','entireline'), lambda x, y, z: z.units.append((x.group(1),x.group(2))), None, None),
        ('xp',('nbr',), lambda x, y, z: setattr(z,'xp',x.group(1)), None, None),
        ('randomequip',('rich_nbr',), lambda x,y,z: setattr(z,'randomequip',x.group(1)),None,None),
        ('additem',('entireline',), lambda x,y,z: z.additems.append(x.group(1)),None,None),
        ('mag_fire',('level_nbr',), lambda x,y,z: setattr(z,'mag_fire',x.group(1)),None,None),
        ('mag_air',('level_nbr',), lambda x,y,z: setattr(z,'mag_air',x.group(1)),None,None),
        ('mag_water',('level_nbr',), lambda x,y,z: setattr(z,'mag_water',x.group(1)),None,None),
        ('mag_earth',('level_nbr',), lambda x,y,z: setattr(z,'mag_earth',x.group(1)),None,None),
        ('mag_astral',('level_nbr',), lambda x,y,z: setattr(z,'mag_astral',x.group(1)),None,None),
        ('mag_death',('level_nbr',), lambda x,y,z: setattr(z,'mag_death',x.group(1)),None,None),
        ('mag_nature',('level_nbr',), lambda x,y,z: setattr(z,'mag_nature',x.group(1)),None,None),
        ('mag_blood',('level_nbr',), lambda x,y,z: setattr(z,'mag_blood',x.group(1)),None,None),
        ('mag_priest',('level_nbr',), lambda x,y,z: setattr(z,'mag_priest',x.group(1)),None,None)]:
    _valid_lines[tag[0]] = _template_line(tag[0],tag[1],tag[2],tag[3],tag[4])
    _special_lines[tag[0]] = _valid_lines[tag[0]]
# god-special


_standard_search_pattern = copy.deepcopy(_static_patterns)
_standard_search_pattern.update({pattern+str(num):_var_patterns[pattern] for num in range(4) for pattern in _var_patterns})

def new(pathObj, title, imagefile, allowoverwrite=True, domversion="400",
        description="Nondescript Map",
        header=_defaultsObj().header):
    retval = MapData(filename=pathObj, title=title, imagefile=imagefile, domversion=domversion,
            description=description, header=header)
    return retval

def fromstring(mapfiledata):
    retval = MapData(mapfiledata=mapfiledata)
    return retval

def open(path):
    retval = MapData(filename=path, status='old')
    return retval

class MapData:
    def __init__(self, filename = None, status = 'unknown', imagefile = None, title = None,
            domversion = 428, description = None, maptextdata = None, header = None, debug=False):
        self.__inits = (not filename, not imagefile, not title, not description, not maptextdata, not header)
        self.debug = debug

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
        self.scenario = None
        self.maptextcol = None

        self.emptylines = list()
        self.comments = list()
        self.allowedplayer = list()
        self.specstart = list()
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
        ''' Import file line by line '''
        curObject = None
        with fopen(path,'r') as infile:
            self.maptextdata = infile.read()

        formatter = dict(_static_patterns)
        for var, pattern in _var_patterns.viewitems():
            for num in range(4): 
                formatter[var+'{0:d}'.format(num)] = pattern

        self.lines = re.split('\n', self.maptextdata)
        self.match = list()
        lineCache = ''
        for linenum, line in zip(range(len(self.lines)),self.lines):
            self.curlinenum = linenum
            lineCache = line if lineCache=='' else lineCache+'\n'+line
            matched = False
            tag = re.search('^#?(\S*)',lineCache).group(1)
            if self.debug: print("{0:d}".format(linenum)+":"+lineCache+":"+_valid_lines[tag]+":")
            try:
                match = re.match(_valid_lines[tag].format(**formatter), lineCache, re.MULTILINE+re.DOTALL)
            except Exception as e:
                print tag, lineCache, partial 
                raise(e)
            if match: 
                self.match.append((linenum,tag,match.groups()))
                matched = True
                lineCache = ''
            elif ((not matched) and (tag=='description')): 
                continue
            else:
                partial = _valid_lines[tag]
                for term in formatter:
                    partial = partial.replace('{'+term+'}',formatter[term])
                print("{0:d}".format(linenum)+":"+lineCache+":"+partial+":"+_valid_lines[tag]+":")
                raise Exception("InvalidLine",'Line {0:d} ::{1:s}:: matched no pattern for ::{2:s}::'.format(linenum,line,tag))
            import_functions.get(tag).__call__(match,self,curObject)
            curObject = focus_functions.get(tag).__call__(match,self,curObject) or curObject
        return tag, match

    def Export(self,filelike,new=True):
        # header
        _loc_output_patterns = copy.deepcopy(_output_patterns)
        _loc_output_patterns['firstchar'] = ''
        _loc_output_patterns['lastchar'] = ''
        if new:
            filelike.write(self.header)
            filelike.write("""\n-- Title and image file""")
            filelike.write(_valid_lines['dom2title'].format(
                entireline0=self.dom2title,**_loc_output_patterns)
                )
            filelike.write(_valid_lines['imagefile'].format(string0=self.imagefile,**_loc_output_patterns))
            filelike.write(_valid_lines['domversion'].format(nbr0=self.domversion,**_loc_output_patterns))
            if self.periodic == PeriodicNS: 
                filelike.write(_valid_lines['vertwrap'].format(**_loc_output_patterns))

            elif self.periodic == PeriodicEW: 
                filelike.write(_valid_lines['horwrap'].format(**_loc_output_patterns))

            elif self.periodic == PeriodicAll: 
                filelike.write(_valid_lines['wraparound'].format(**_loc_output_patterns))

            filelike.write(_valid_lines['description'].format(paragraph0=self.description,**_loc_output_patterns))

            filelike.write("""\n\n-- Province names/terrains""")
            for province in self.provinces:
                filelike.write(_valid_lines['landnum'].format(province_nbr0=province.idnum,string0=province.landname, **_loc_output_patterns))
                filelike.write(_valid_lines['terrain'].format(province_nbr0=province.idnum,bitmask_nbr0=province.value, **_loc_output_patterns))

            filelike.write("""\n\n-- Province neighbours""")
            keys = sorted(self.connection_data.keys(), key=lambda x: int(x[0])*len(self.provinces)+int(x[1]))
            for connection in keys:
                filelike.write(_valid_lines['neighbour'].format(province_nbr0=connection[0],province_nbr1=connection[1],**_loc_output_patterns))
                if self.connection_data[connection] != 0: 
                    filelike.write(_valid_lines['neighbourspec'].format(province_nbr0=connection[0],province_nbr1=connection[1],connectionType0=self.connection_data[connection],**_loc_output_patterns))

            filelike.write("""\n\n-- Special per province commands""")
            # link the specials to the main map
            # link the prov_specials to the territory number since that's how they're processed
            filelike.write("""\n\n--""")
        else:
            lineCount = 0
            #commentsandstuff = dict(list(map(lambda x: (x[0], '--'+x[1]), self.comments))+list(map(lambda x: (x,''), self.emptylines)), key=lambda x: x[0])
            lines = list()
            lines.append(self.header)
            lines.append("""\n-- Title and image file""")
            lines.append(_valid_lines['dom2title'].format(
                entireline0=self.dom2title,**_loc_output_patterns)
                )
            lines.append(_valid_lines['imagefile'].format(
                string0=self.imagefile,**_loc_output_patterns)
                )
            lines.append(_valid_lines['domversion'].format(
                nbr0=self.domversion,**_loc_output_patterns)
                )

            if   self.periodic == PeriodicNS: lines.append(_valid_lines['vertwrap'].format(**_loc_output_patterns))
            elif self.periodic == PeriodicEW: lines.append(_valid_lines['horwrap'].format(**_loc_output_patterns))
            elif self.periodic == PeriodicAll: lines.append(_valid_lines['wraparound'].format(**_loc_output_patterns))

            if self.scenario:
                lines.append(_valid_lines['scenario'].format(**_loc_output_patterns))

            if self.maptextcol:
                lines.append(_valid_lines['maptextcol'].format(
                    color_norm_nbr0=self.maptextcol[0],
                    color_norm_nbr1=self.maptextcol[1],
                    color_norm_nbr2=self.maptextcol[2],
                    color_norm_nbr3=self.maptextcol[3],
                    **_loc_output_patterns)
                    )


            self.descr = _valid_lines['description'].format(paragraph0=self.description,**_loc_output_patterns).split('\n')
            lines.extend(self.descr)

            lines.append("""\n\n-- Province names/terrains""")
            for province in self.provinces:
                if province.landname:
                    lines.append(_valid_lines['landname'].format(province_nbr0=province.idnum,string0=province.landname, **_loc_output_patterns))
                lines.append(_valid_lines['terrain'].format(province_nbr0=province.idnum,bitmask_nbr0=province.value, **_loc_output_patterns))

            lines.append("""\n\n-- Province neighbours""")
            for province in self.provinces:
                for connection in province.neighbours:
                    lines.append(_valid_lines['neighbour'].format(province_nbr0=province.idnum,province_nbr1=connection[0],**_loc_output_patterns))
                    if connection[1] != 0: 
                        lines.append(_valid_lines['neighbourspec'].format(province_nbr0=province.idnum,province_nbr1=connection[0],connectionType0=connection[1],**_loc_output_patterns))

            lines.append("""\n\n-- Special per province commands""")
            for allowedplayer in self.allowedplayer:
                lines.append(_valid_lines['allowedplayer'].format(
                    nation_nbr0=allowedplayer,
                    **_loc_output_patterns)
                    )

            lines.append("""\n""")
            for specstart in self.specstart:
                lines.append(_valid_lines['specstart'].format(
                    nation_nbr0=specstart[0],
                    province_nbr0=specstart[1],
                    **_loc_output_patterns)
                    )
            lines.append("""\n""")
            for province in self.provinces:
                lines.extend(province.Export(_special_lines,**_loc_output_patterns))


            for linenum in range(len(lines)):
                #try:
                    #content = commentsandstuff.get(linenum)+'\n'
                #except:
                content = lines.pop(0)+'\n'
                sys.stdout.write(content)

            self.outlines = lines

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

    def parse(self):
        pass

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
    TEST_OPEN=False 
    TEST_NEEDS_OPEN=False
    TEST_OVERWRITING_SAVE=False
    TEST_NEW_SAVE=False
    TEST_REMOVE_PROVINCE=False

    if TEST_OPEN or TEST_NEEDS_OPEN:
        print("Testing open")
        M = open(os.path.expanduser('~/dominions4/maps/hexawyr.map'))

    if TEST_OVERWRITING_SAVE:
        print("Testing overwriting save")
        with fopen(os.path.expanduser('~/dominions4/maps/hexawyr_copy.map'),'w') as outfile:
            M.Export(outfile,new=False)

    if TEST_NEW_SAVE:
        print("Testing new save")
        with fopen(os.path.expanduser('~/dominions4/maps/hexawyr_copy2.map'),'w') as outfile:
            M.Export(outfile)

    if TEST_REMOVE_PROVINCE:
        print("Testing remove province")
        M.removeProvince(Province(10,-1))
        with fopen(os.path.expanduser('~/dominions4/maps/hexawyr_no10.map'),'w') as outfile:
            M.Export(outfile,new=False)

    print("Testing Import")
    Tester = new('example.map','Example Map','example.tga')
    Tester.Import(os.path.expanduser('~/Library/Application Support/Steam/SteamApps/common/Dominions4/maps/dawn.map'))
    import sys
    Tester.Export(sys.stdout,new=False)

    '''
    txt = M.maptextdata
    k = M.update('province_nbr',10,11)
    txt_change = M.maptextdata
    k = M.update('province_nbr',11,10)
    txt2 = M.maptextdata
    __txtdiff(txt.split('\n'),txt2.split('\n'))
    __txtdiff(txt.split('\n'),txt_change.split('\n'))
    '''
