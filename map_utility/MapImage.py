#!/usr/bin/env python
from PIL import Image, ImageFont, ImageChops

def new():
    pass

def open():
    pass

class MapImage():
    def __init__(self,im):
        self.im = im
        size = self.im.getbbox()
        # this failed because the attributes are already set in a later version of pillow
        try:
            self.im.width = size[2]
            self.im.height = size[3]
        except:
            pass

        self.convert = im.convert

    def getCenters(self):
        self.whites_xy = [(x,y) for y in reversed(range(0,self.im.height)) for x in range(0,self.im.width) if data.getpixel((x,y)) == (255,255,255,255) or data.getpixel((x,y)) == (255,255,255)]
        self.whites_xy.sort(key=lambda x, y: (self.im.width - x) + y * self.im.width)
        return self.whites_xy

    def resize(widthin, heightin):
        ''' resizes the map, keeping the white centers pure white. Errors on accidental reordering. e.g. pt (30,865)'''
        pass

    def save(filename, mode=None):
        pass

    
