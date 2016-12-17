import terrain

class Province:
    def __init__(self, idnum, value, nextid = None, center = None):
        self.idnum = int(idnum)
        self.value = int(value)
        self.center = center
        self.nextid = idnum if not nextid else nextid
        self.neighbours = list()
        # map text data
        self.land = None 
        self.setland = None 
        self.owner = None
        self.killfeatures = None
        self.population = None
        self.poptype = None
        self.knownfeature = list()
        self.feature = list()
        self.lab = None
        self.temple = None
        self.fort = None
        self.unrest = None
        self.defence = None
        self.population = None
        self.skybox = None
        self.batmap = None
        self.owner = None
        self.groundcol = None
        self.rockcol = None
        self.fogcol = None

    def Export(self, lines, **kwargs):
        outlist = list()
        if self.land: 
            outlist.append(lines['land'].format(province_nbr0=self.idnum, **kwargs))

        if self.setland: 
            outlist.append(lines['setland'].format(province_nbr0=self.idnum,**kwargs))

        if self.owner:
            outlist.append(lines['owner'].format(nation_nbr0=self.owner,**kwargs))

        if self.killfeatures:
            outlist.append(lines['killfeatures'].format(**kwargs))

        if self.poptype:
            outlist.append(lines['poptype'].format(poptype_nbr0=self.poptype,**kwargs))

        for feature in self.feature: 
            outlist.append(lines['feature'].format( entireline0=feature,**kwargs))

        for knownfeature in self.knownfeature:
            outlist.append(lines['knownfeature'].format(entireline0=knownfeature,**kwargs))

        if self.lab: outlist.append(lines['lab'].format(**kwargs))
        if self.temple: outlist.append(lines['temple'].format(**kwargs))
        if self.fort: outlist.append(lines['fort'].format( fort_nbr0=self.fort,**kwargs) )
        if self.unrest: outlist.append(lines['unrest'].format( unrest_nbr0=self.unrest,**kwargs) )
        if self.defence: outlist.append(lines['defence'].format( defence_nbr0=self.defence,**kwargs) )
        if self.population: outlist.append(lines['population'].format( population_nbr0=self.population,**kwargs) )
        if self.skybox: outlist.append(lines['skybox'].format( entireline0=self.skybox,**kwargs) )
        if self.batmap: outlist.append(lines['batmap'].format( entireline0=self.batmap,**kwargs) )
        if self.groundcol: outlist.append(lines['groundcol'].format(
            color_nbr0=self.groundcol[0], color_nbr1=self.groundcol[1], color_nbr2=self.groundcol[2], **kwargs))
        if self.rockcol: outlist.append(lines['rockcol'].format(
            color_nbr0=self.rockcol[0], color_nbr1=self.rockcol[1], color_nbr2=self.rockcol[2], **kwargs))
        if self.fogcol: outlist.append(lines['fogcol'].format(
            color_nbr0=self.fogcol[0], color_nbr1=self.fogcol[1], color_nbr2=self.fogcol[2], **kwargs))


        return outlist

    def __str__(self):
        return "Province {:d}".format(self.idnum)

    def __repr__(self):
        return "Province {:d}".format(self.idnum)

    def getFlags(self):
        return terrain.TextFromValue(self.value)

    def getMask(self):
        return terrain.MaskFromValue(self.value)

    def addNeighbor(self, neighbour, connection_type):
        self.neighbours.update(neighbour=connection_type)

    def getNeighbors(self):
        return self.neighbours
