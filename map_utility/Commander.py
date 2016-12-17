
class Commander:
    def __init__(self, comtype):
        self.commander = comtype
        self.clearmagic = None
        self.comname = None
        self.bodyguards = None
        self.units = None
        self.xp = None
        self.randomequip = None
        self.additem = None
        self.mag_fire = None
        self.mag_air = None
        self.mag_water = None
        self.mag_earth = None
        self.mag_astral = None
        self.mag_death = None
        self.mag_nature = None
        self.mag_blood = None
        self.mag_priest = None

    def Export(self, lines, **kwargs):
        if self.commander:
            outlist.append(lines['commander'].format( entireline0=self.commander,**kwargs))
        if self.clearmagic:
            outlist.append(lines['clearmagic'].format(**kwargs))
        if self.comname:
            outlist.append(lines['comname'].format( entireline0=self.comname,**kwargs))
        if self.bodyguards:
            outlist.append(lines['bodyguards'].format( nbr0=self.bodyguards[0],entireline0=self.bodyguards[1],**kwargs))
        for unit in self.units:
            outlist.append(lines['units'].format( nbr0=unit[0],entireline0=unit[1],**kwargs))
        if self.xp:
            outlist.append(lines['xp'].format( nbr0=self.xp,**kwargs))
        if self.randomequip:
            outlist.append(lines['randomequip'].format( rich_nbr0=self.randomequip,**kwargs))
        for item in  self.additem:
            outlist.append(lines['additem'].format( entireline0=item,**kwargs))
        if self.mag_fire:
            outlist.append(lines['mag_fire'].format( level_nbr0=self.mag_fire,**kwargs))
        if self.mag_air:
            outlist.append(lines['mag_air'].format( level_nbr0=self.mag_air,**kwargs))
        if self.mag_water:
            outlist.append(lines['mag_water'].format( level_nbr0=self.mag_water,**kwargs))
        if self.mag_earth:
            outlist.append(lines['mag_earth'].format( level_nbr0=self.mag_earth,**kwargs))
        if self.mag_astral:
            outlist.append(lines['mag_astral'].format( level_nbr0=self.mag_astral,**kwargs))
        if self.mag_death:
            outlist.append(lines['mag_death'].format( level_nbr0=self.mag_death,**kwargs))
        if self.mag_nature:
            outlist.append(lines['mag_nature'].format( level_nbr0=self.mag_nature,**kwargs))
        if self.mag_blood:
            outlist.append(lines['mag_blood'].format( level_nbr0=self.mag_blood,**kwargs))
        if self.mag_priest:
            outlist.append(lines['mag_priest'].format( level_nbr0=self.mag_priest,**kwargs))
        return outlist

    def __str__(self):
        return "Commander {:d}".format(self.idnum)

    def __repr__(self):
        return "Commander {:d}".format(self.idnum)

    def getFlags(self):
        return terrain.TextFromValue(self.value)

    def getMask(self):
        return terrain.MaskFromValue(self.value)

    def addNeighbor(self, neighbour, connection_type):
        self.neighbours.update(neighbour=connection_type)

    def getNeighbors(self):
        return self.neighbours
