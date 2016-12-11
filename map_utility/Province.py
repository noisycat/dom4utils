import terrain

class Province:
    def __init__(self, idnum, value, nextid = None, center = None):
        self.idnum = idnum
        self.value = int(value)
        self.center = center
        self.nextid = idnum if not nextid else nextid
        # duplicate, takes up a lot of memory
        self.neighbours = list()

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
