# system modules
import re, math, os, platform, itertools, argparse, io

# specialty system modules
# Need numpy array
from numpy import array

# Need Pillow
from PIL import Image, ImageDraw, ImageFont, ImageChops
from PIL import VERSION as PIL_VERSION, PILLOW_VERSION as PIL_PILLOW_VERSION

# Need Wand
import wand.image
from wand.version import VERSION as WAND_VERSION


# required version numbers

# PIL
print '1.1.7' >= PIL_VERSION

# pillow
print "3.1.0" >= PIL_PILLOW_VERSION

# wand
print "0.4.2" >= WAND_VERSION

# local modules
import defaults
from terrain import rebuildMask, breakdown, interpretMask, getBit, setType, flipType, checkType, getConnections, checkPeriodicNS, checkPeriodicEW

parser = argparse.ArgumentParser(description='Dominions 4 Map Analyzer')
parser.add_argument('mappath',type=str)
parser.add_argument('--dom4mapspath',type=str)
parser.add_argument('--installpath',type=str,default=defaults.dom4.installpath[platform.system()],help='overrides the install path for dominions 4')
parser.add_argument('--userpath',type=str,default=defaults.dom4.userpath[platform.system()],help='overrides the default userpath for dominions 4')
parser.add_argument('--noshow',action="store_true",default=False,help='does not display the generated image')
parser.add_argument('--saveas',type=str,default='default_image_name',help='path/name to save the resulting image file')
parser.add_argument('--offset-x',default=0,type=int,help='offset amount in the x-axis for wrapped images')
parser.add_argument('--offset-y',default=0,type=int,help='offset amount in the y-axis for wrapped images')
parser.add_argument('--connection-types', default='all')
parser.add_argument('--image-reduce',type=int, default=1, help='contraction of the output image (makes the resulting image smaller)')
parser.add_argument('--fontsize-province-number', type=int, default=0,help='fontsize choice for province number')
parser.add_argument('--color-province-number', default=defaults.colors.black,help='color choice for province number')
parser.add_argument('--color-mountain-path', nargs=4, type=int, default=defaults.colors.mountain, help='color choice for mountain paths', choices=range(256))
parser.add_argument('--color-river-path', nargs=4, type=int, default=defaults.colors.river, help='color choice for river paths',choices=range(256))
parser.add_argument('--color-aquatic-path', nargs=4, type=int, default=defaults.colors.aquatic, help='color choice for aquatic paths',choices=range(256))
parser.add_argument('--color-amphibious-path', nargs=4, type=int, default=defaults.colors.amphibious, help='color choice for amphibious paths',choices=range(256))
parser.add_argument('--color-normal-path', nargs=4, type=int, default=defaults.colors.normal, help='color choice for normal paths',choices=range(256))
args = parser.parse_args()

# these can be replaced with an Action at some point - but I'm not interested in doing that right now
args.color_mountain_path = tuple(args.color_mountain_path)
args.color_river_path = tuple(args.color_river_path)
args.color_normal_path = tuple(args.color_normal_path)
args.color_amphibious_path = tuple(args.color_amphibious_path)
args.color_aquatic_path = tuple(args.color_aquatic_path)
print args

# suck in map file
user_maps=os.path.join(args.userpath,'maps')
dominions_maps=os.path.join(args.installpath,'maps')
maplocalfolder=os.path.dirname(args.mappath)
mapname = os.path.basename(args.mappath)
with open(os.path.join(maplocalfolder,mapname)) as mapfile:
    mapfiledata = mapfile.read()

# suck in map image
mapfiledata = re.sub(r'#dom2title (.+)$',r'#dom2title "\1 Competitive"$',mapfiledata)
mapimagefilename = re.findall(r'#imagefile (\S+)$',mapfiledata,re.M)[0]
try:
    mapimagepath = os.path.join(maplocalfolder,mapimagefilename)
    os.stat(mapimagepath)

# not in the local folder, maybe image is in...
except OSError as e:
    # the user folder
    try:
	mapimagepath = os.path.join(user_maps,mapimagefilename)
	os.stat(mapimagepath)

    except OSError as e2:
	# the official folder
	try:
	    mapimagepath = os.path.join(dominions_maps,mapimagefilename)
	    os.stat(mapimagepath)
	except OSError as e3:
	    raise Exception('OSError',"Can't find the required image file in any of the directories:{0:s}:{1:s}:{2:s}".format(maplocalfolder, user_maps, dominions_maps))

print "Map Image: ",mapimagepath

try:
    im = Image.open(os.path.join(maplocalfolder,mapimagefilename))

except ValueError as e:
    print "PIL:",e
    print "Using Wand to get around this crap"
    tmpim = wand.image.Image(filename=os.path.join(mapfolder,mapimagefilename))
    im = Image.open(io.BytesIO(tmpim.make_blob('TGA')))

except IOError:
    print "PIL:",e
    print "...looking in dominions install"
    try:
        im = Image.open(os.path.join(dominions_install,mapimagefilename))
    except ValueError:
        print "PIL:",e
        print "Using Wand to get around this crap"
        tmpim = wand.image.Image(filename=os.path.join(mapfolder,mapimagefilename))
        im = Image.open(io.BytesIO(tmpim.make_blob('TGA')))

data = im.getdata()
# does this have an alpha channel?

# find the white xy
whites_xy = [(x,y) for y in reversed(range(0,im.height)) for x in range(0,im.width) if data.getpixel((x,y)) == (255,255,255,255) or data.getpixel((x,y)) == (255,255,255)]

# whites_xy[k] is the k province xy

isPeriodicNS = checkPeriodicNS(mapfiledata)
isPeriodicEW = checkPeriodicEW(mapfiledata)
connections = getConnections(mapfiledata)

def periodic_translate(s,a1,a2,i,j):
    return tuple(s + array(a1) * i + array(a2) * j)

s = lambda t,i_s1,i_s2: tuple(array(array(i_s1,dtype=int) + t * (array(i_s2,dtype=int) - array(i_s1,dtype=int)),dtype=int))

def periodic(_s1,_s2,image_dimensions,isPeriodicNS=True,isPeriodicEW=True):
    width = im.width
    height = im.height
    s1 = array(_s1)
    s2 = array(_s2)


    I = array([[width, 0],[0,height]])
    if 2*(s1[0]-s2[0]) > width and 2*(s1[1]-s2[1]) > height:
        print 1
        return periodic(_s2,_s1,image_dimensions,isPeriodicNS,isPeriodicEW)

    elif 2*(s1[0]-s2[0]) < -width and 2*(s1[1]-s2[1]) >  height:
        s2m = periodic_translate(_s2,I[:,0],I[:,1],-1,1)
        s1m = periodic_translate(_s1,I[:,0],I[:,1],1,-1)
        tx = (0.0-s1[0])/(s2m[0]-s1[0])
        ty = (0.0-s1m[1])/(s2[1]-s1m[1])
        print tx,s(tx,s1,s2m),ty,s(ty,s1m,s2)
        stx_o = periodic_translate(s(tx,s1,s2m),I[:,0],I[:,1],0,-1)
        sty_o = periodic_translate(s(ty,s1m,s2),I[:,0],I[:,1],-1,0)
        out = [[_s1,s(tx,s1,s2m)],[stx_o,sty_o],[periodic_translate(stx_o,I[:,0],I[:,1],1,0),_s2]]
        print 2, tx,ty, out
        return out


    elif 2*(s1[0]-s2[0]) >  width and 2*(s1[1]-s2[1]) < -height:
        print 3
        return periodic(_s2,_s1,image_dimensions,isPeriodicNS,isPeriodicEW)

    elif 2*(s1[0]-s2[0]) < -width and 2*(s1[1]-s2[1]) < -height:
        s2m = periodic_translate(_s2,I[:,0],I[:,1],-1,-1)
        tx = (0.0-s1[0])/(s2m[0]-s1[0])
        ty = (0.0-s1[1])/(s2m[1]-s1[1])
        print tx,s(tx,s1,s2m),ty,s(ty,s1,s2m)
        stx_o = periodic_translate(s(tx,s1,s2m),I[:,0],I[:,1],1,0)
        sty_o = periodic_translate(s(ty,s1,s2m),I[:,0],I[:,1],1,0)
        out = [[_s1,s(tx,s1,s2m)],[stx_o,sty_o],[periodic_translate(sty_o,I[:,0],I[:,1],0,1),_s2]]
        print 4, tx,ty,s2m, out
        return out

    elif 2*(s1[0]-s2[0]) > width:
        return periodic(_s2,_s1,image_dimensions,isPeriodicNS,isPeriodicEW)

    elif 2*(_s1[0]-_s2[0]) < -width:
        s2m = periodic_translate(_s2,I[:,0],I[:,1],-1,0)
        tx = (0.0-_s1[0])/(s2m[0]-_s1[0])
        out = [[_s1,s(tx,_s1,s2m)],[periodic_translate(s(tx,_s1,s2m),I[:,0],I[:,1],1,0),_s2]]
        return out

    elif 2*(_s1[1]-_s2[1]) >  height:
        return periodic(_s2,_s1,image_dimensions,isPeriodicNS,isPeriodicEW)

    elif 2*(_s1[1]-_s2[1]) < -height:
        s2m = periodic_translate(_s2,I[:,0],I[:,1],0,-1)
        ty = (0.0-_s1[1])/(s2m[1]-_s1[1])
        out = [[_s1,s(ty,_s1,s2m)],[periodic_translate(s(ty,_s1,s2m),I[:,0],I[:,1],0,1),_s2]]
        return out 

    else:
        return [[_s1,_s2],]


def line(ij,j=0):
    try:              return (whites_xy[ij-1],whites_xy[j-1])
    except TypeError: return (whites_xy[ij[0]-1],whites_xy[ij[1]-1])

draw = ImageDraw.Draw(im)

# custom colors for rendering
color = dict()
color['mountain'] = args.color_mountain_path
color['river'] = args.color_river_path
color['aquatic'] = args.color_aquatic_path
color['amphibious'] = args.color_amphibious_path
color['normal'] = args.color_normal_path

def drawConnection(drawObj, segs, color, width=6):
    if len(segs)==1: 
        drawObj.line(segs[0],fill=color,width=6)
    if len(segs)==2: 
        drawObj.line(segs[0],fill=color,width=6)
        drawObj.line(segs[1],fill=color,width=6)
    if len(segs)==3: 
        drawObj.line(segs[0],fill=color,width=6)
        drawObj.line(segs[1],fill=color,width=6)
        drawObj.line(segs[2],fill=color,width=6)

'''
# test section
x = (84, 164)
lx = line(x)
draw.line(lx,fill=(25,255,0,255),width=6)
imdata = periodic(lx[0],lx[1],(im.width,im.height))
draw.line(imdata[0],fill=(255,0,0,255),width=6)
draw.line(imdata[1],fill=(255,0,255,255),width=6)
'''

# load a font
fontsize = max(im.width,im.height)/75 if args.fontsize_province_number <= 0 else args.fontsize_province_number
fnt = ImageFont.truetype('Arial.ttf',fontsize)

import random
# NO MORE RANDOM NUMBERS PAST THIS 
random.seed(2718)

if 0:
    #changes to map data
    for k in range(1,len(whites_xy)+1):
        #if checkType(k,'Throne',mapfiledata): mapfiledata = flipType(k,'Throne',mapfiledata)

        #new caves
        if (k in [6, 149, 151]): mapfiledata = setType(k,'Cave',True)

        # new manual thrones
        if (k in [114,92,63,32,88]) or (k in [124,85,39,23,123]): mapfiledata = setType(k,'Start',True)

        # turning off these thrones
        if (k in [1,77,93,37,3]): mapfiledata = setType(k,'Throne',False)

#select out territories
def numLandConnections(k,connectors): return len(filter(lambda xx: k in xx, connectors))
def checkNeighbors(k,flag,connectors,mapfiledata): 
    return any([checkType(x,flag,mapfiledata) for x in itertools.chain.from_iterable(filter(lambda xx: k in xx, connectors))])

ratios = map(lambda x: 1 if 4 <= numLandConnections(x,connections['normal'].union(connections['river'],connections['mountain'])) and not checkType(x,'Nostart',mapfiledata) else 0, range(1,len(whites_xy)+1))
#ratios = map(lambda x: 1 if 4 <= numLandConnections(x,connections['normal'].union(connections['river'],connections['mountain'])) and not checkType(x,'Nostart',mapfiledata) and not checkNeighbors(x,'Throne',connections['normal'].union(connections['river'],connections['mountain'])) else 0, range(1,len(terrain_types)+1))

# draw connections
for key in ('normal','mountain','river','aquatic','amphibious'):
    for x in connections[key]:
        #if checkType(x[0],'Start',mapfiledata) or checkType(x[1],'Start',mapfiledata): 
            segs = periodic(line(x)[0],line(x)[1],(im.width,im.height))
            drawConnection(draw,segs,color[key])

# label all points
for k,xy in zip(range(1,len(whites_xy)+1),whites_xy):
    xymod = (xy[0] - fontsize * (xy[0] > im.width - fontsize),xy[1] - fontsize * (xy[1] > im.height-fontsize))
    if checkType(k,'Throne',mapfiledata): 
        draw.text(xymod,str(k),font=fnt,fill=defaults.colors.gold)
        print "Throne ",k

    if checkType(k,'Large Province',mapfiledata):
        draw.text(xymod,str(k),font=fnt,fill=defaults.colors.gold)
        pass

    #elif checkNeighbors(k,'Throne',connections['all'],mapfiledata):
    #    pass

    else:
        scaled_color = tuple(itertools.chain.from_iterable((array(array(defaults.colors.red)*ratios[k-1],dtype=int)[0:3],(255,))))
        draw.text(xymod,str(k),font=fnt,fill=tuple(scaled_color))

# form export image
offset = ImageChops.offset(im,args.offset_x,args.offset_y)
if not args.noshow: offset.show()
test = im.resize((im.width/args.image_reduce,im.height/args.image_reduce),Image.NEAREST)
test.save(mapname+'_connections.png')
offset = offset.resize((im.width/args.image_reduce,im.height/args.image_reduce),Image.NEAREST)
offset.save(mapname+'_ours.png')
print [(key,[checkType(k,key,mapfiledata) for k in range(1,len(whites_xy)+1)].count(True)) for key in interpretMask(tuple((1,)*27))]
print [k for k in range(1,len(whites_xy)+1) if checkType(k,'Mountain',mapfiledata) ]
'''
-- Special per province commands
-- atlantis
#specstart 87 88
-- mictlan 
#specstart 41 63
-- ashdod
#specstart 55 32
-- xibalba
#specstart 58 114
-- machaka 
#specstart 43 92

-- oceania
#specstart 90 123
-- pangea
#specstart 48 39
-- jotunheim
#specstart 51 85
-- asphodel
#specstart 49 124
-- agartha
#specstart 44 23
--
'''
