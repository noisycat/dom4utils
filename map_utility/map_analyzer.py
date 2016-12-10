__author__ = "Charles Lena"
# system modules
import re, math, os, platform, itertools, argparse, io, sys

# local modules
## I should have done local defaults years ago
import defaults

## Provides some terrain control functions
from terrain import ValueFromMask, MaskFromValue, TextFromMask, getBitIndex, setType, flipType, checkType, getConnections, checkPeriodicNS, checkPeriodicEW, provinceValue, TextFromValue, terrainText

## Provides some example profiles for doing different types of edits
import profiles

parser = argparse.ArgumentParser(description='Dominions 4 Map Analyzer',
        epilog="""Lots of customizeability in analyzing and editing assist for maps. 
The quickest way to make paths disappear is setting their alpha channel to 0, e.g.:

python -i ./map_analyzer --color-normal-path 255 255 255 0 ~/dominion4/maps/hexawyr.map

You can also edit the profiles.py and add in a custom profile for selection of which province numbers to print (see: province_filter), their colors (see: color_scale_transform ), and which specific paths to print (see: path_filter ), should you so desire. Feel free to try and hail me on Steam if you have ideas or requests. I'd really like to add in a graphics window that allows for selection of the whites_xy dots that determine the files, and allow you to do graphical insertion and removal, as well as radial auto connections. Commandline insertions are pretty easy to do, if those are good enough for now""")
parser.add_argument('mappath',type=str,help='path/filename to the mapfile')
parser.add_argument('--debug',action="store_true",default=False, help='enables some debug printing')
parser.add_argument('--installpath',type=str,default=defaults.dom4.installpath[platform.system()],help='overrides the install path for dominions 4')
parser.add_argument('--userpath',type=str,default=defaults.dom4.userpath[platform.system()],help='overrides the default userpath for dominions 4')
parser.add_argument('--noshow',action="store_true",default=False,help='does not display the generated image')
parser.add_argument('--saveas',type=str,default=defaults.outfile, help='path/name to save the resulting image file')
parser.add_argument('--offset-x',default=0,type=int,help='offset amount in the x-axis for wrapped images')
parser.add_argument('--offset-y',default=0,type=int,help='offset amount in the y-axis for wrapped images')
parser.add_argument('--connection-types', default='all',choices = ['all','aquatic','normal','mountain','amphibious','river','info-only','passable'])
parser.add_argument('--image-reduce',type=int, default=1, help='contraction of the output image (makes the resulting image smaller)')
parser.add_argument('--fontface', type=str, default=defaults.font[platform.system()],help = 'fontface choice for labels')
parser.add_argument('--fontsize-province-number', type=int, default=0, help='fontsize choice for province number')
parser.add_argument('--profile', default='default', help='''sets a series of formatting choices to emphasize certain aspects of a map''',
choices=profiles.__all__)
parser.add_argument('--color-province-number', nargs=4, type=int, default=defaults.colors.black, help='color choice for province number', choices=range(256), metavar='0 .. 255')
parser.add_argument('--color-mountain-path', nargs=4, type=int, default=defaults.colors.mountain, help='color choice for mountain paths', choices=range(256), metavar='0 .. 255')
parser.add_argument('--color-river-path', nargs=4, type=int, default=defaults.colors.river, help='color choice for river paths',choices=range(256), metavar='0 .. 255')
parser.add_argument('--color-aquatic-path', nargs=4, type=int, default=defaults.colors.aquatic, help='color choice for aquatic paths',choices=range(256), metavar='0 .. 255')
parser.add_argument('--color-amphibious-path', nargs=4, type=int, default=defaults.colors.amphibious, help='color choice for amphibious paths',choices=range(256), metavar='0 .. 255')
parser.add_argument('--color-normal-path', nargs=4, type=int, default=defaults.colors.normal, help='color choice for normal paths',choices=range(256), metavar='0 .. 255')
parser.add_argument('--color-info-only-path', nargs=4, type=int, default=defaults.colors.info_only, help='color choice for info_only paths',choices=range(256), metavar='0 .. 255')
args = parser.parse_args()
# these can be replaced with an Action at some point - but I'm not interested in doing that right now
args.color_mountain_path = tuple(args.color_mountain_path)
args.color_river_path = tuple(args.color_river_path)
args.color_normal_path = tuple(args.color_normal_path)
args.color_amphibious_path = tuple(args.color_amphibious_path)
args.color_aquatic_path = tuple(args.color_aquatic_path)
args.color_info_only_path = tuple(args.color_info_only_path)
print("")
if args.debug: print(args)
# specialty system modules
# Need numpy array
from numpy import array, sum

# Need Pillow 3 with SGI_ support
try:
	from PIL import Image, ImageDraw, ImageFont, ImageChops
except ImportError as e:
	sys.stderr.write("python-pillow is required for this: https://github.com/python-pillow")
	raise e

try:
	from PIL import VERSION as PIL_VERSION, PILLOW_VERSION as PIL_PILLOW_VERSION

except ImportError as e:
	sys.stderr.write(str(e)+'\n')
	sys.stderr.write("Couldn't import the VERSION numbers for PIL - you likely have a very old version installed\nTrying to go ahead without it")
	PIL_VERSION='1.0.0'
	PIL_PILLOW_VERSION='2.0.0'

# Need Wand
import wand.image
from wand.version import VERSION as WAND_VERSION

'''
# required version numbers
# PIL
print '1.1.7' >= PIL_VERSION

# pillow
print "3.1.0" >= PIL_PILLOW_VERSION

# wand
print "0.4.2" >= WAND_VERSION
'''

# test font out - its been giving trouble
try:
    fnt = ImageFont.truetype(args.fontface,40)
except Exception as e:
    print("Bad font given ( {0:s} )- try a different font (give a full file name if you have to)".format(args.fontface))
    raise e


# suck in map file
user_maps=os.path.join(args.userpath,'maps')
dominions_maps=os.path.join(args.installpath,'maps')
maplocalfolder=os.path.dirname(args.mappath)
mapname = os.path.basename(args.mappath)
with open(os.path.join(maplocalfolder,mapname)) as mapfile:
    mapfiledata = mapfile.read()

# suck in map image
mapimagefilename = re.findall(r'#imagefile (\S+)\s*$',mapfiledata,re.M)[0]
try:
    mapimagepath = os.path.join(maplocalfolder,mapimagefilename)
    stat = os.stat(mapimagepath)

# not in the local folder, maybe image is in...
except OSError as e:
    # the user folder
    try:
	mapimagepath = os.path.join(user_maps,mapimagefilename)
	stat = os.stat(mapimagepath)

    except OSError as e2:
	# the official folder
	try:
	    mapimagepath = os.path.join(dominions_maps,mapimagefilename)
	    stat = os.stat(mapimagepath)
	except OSError as e3:
	    raise Exception('OSError',"Can't find the required image file in any of the directories:{0:s}:{1:s}:{2:s}".format(maplocalfolder, user_maps, dominions_maps))

if args.debug: print "Map Image: ",mapimagepath

try:
    im = Image.open(os.path.join(maplocalfolder,mapimagefilename)).convert('RGBA')

except ValueError as e:
    print "PIL:",e
    print "Using Wand to get around this crap"
    tmpim = wand.image.Image(filename=os.path.join(mapfolder,mapimagefilename))
    im = Image.open(io.BytesIO(tmpim.make_blob('TGA'))).convert('RGBA')

except IOError:
    print "PIL:",e
    print "...looking in dominions install"
    try:
        im = Image.open(os.path.join(dominions_install,mapimagefilename)).convert('RGBA')
    except ValueError:
        print "PIL:",e
        print "Using Wand to get around this crap"
        tmpim = wand.image.Image(filename=os.path.join(mapfolder,mapimagefilename))
        im = Image.open(io.BytesIO(tmpim.make_blob('TGA'))).convert('RGBA')

data = im.getdata()
# does this have an alpha channel?

# find the white xy
size = im.getbbox()
try:
    im.width = size[2]
    im.height = size[3]
except:
    # this failed because the attributes are already set
    pass

whites_xy = [(x,y) for y in reversed(range(0,im.height)) for x in range(0,im.width) if data.getpixel((x,y)) == (255,255,255,255) or data.getpixel((x,y)) == (255,255,255)]

# whites_xy[k] is the k province xy

isPeriodicNS = checkPeriodicNS(mapfiledata)
isPeriodicEW = checkPeriodicEW(mapfiledata)
connections = getConnections(mapfiledata)

def periodic_translate(s,a1,a2,i,j):
    return tuple(s + array(a1) * i + array(a2) * j)

s = lambda t,i_s1,i_s2: tuple(array(array(i_s1,dtype=int) + t * (array(i_s2,dtype=int) - array(i_s1,dtype=int)),dtype=int))

def periodic(_s1,_s2,image_dimensions,isPeriodicNS=True,isPeriodicEW=True):
    width = image_dimensions[0]
    height = image_dimensions[1]
    s1 = array(_s1)
    s2 = array(_s2)


    I = array([[width, 0],[0,height]])
    if 2*(s1[0]-s2[0]) > width and 2*(s1[1]-s2[1]) > height:
        if args.debug: print 1
        return periodic(_s2,_s1,image_dimensions,isPeriodicNS,isPeriodicEW)

    elif 2*(s1[0]-s2[0]) < -width and 2*(s1[1]-s2[1]) >  height:
        s2m = periodic_translate(_s2,I[:,0],I[:,1],-1,1)
        s1m = periodic_translate(_s1,I[:,0],I[:,1],1,-1)
        tx = (0.0-s1[0])/(s2m[0]-s1[0])
        ty = (0.0-s1m[1])/(s2[1]-s1m[1])
        if args.debug: print tx,s(tx,s1,s2m),ty,s(ty,s1m,s2)
        stx_o = periodic_translate(s(tx,s1,s2m),I[:,0],I[:,1],0,-1)
        sty_o = periodic_translate(s(ty,s1m,s2),I[:,0],I[:,1],-1,0)
        out = [[_s1,s(tx,s1,s2m)],[stx_o,sty_o],[periodic_translate(stx_o,I[:,0],I[:,1],1,0),_s2]]
        if args.debug: print 2, tx,ty, out
        return out


    elif 2*(s1[0]-s2[0]) >  width and 2*(s1[1]-s2[1]) < -height:
        if args.debug: print 3
        return periodic(_s2,_s1,image_dimensions,isPeriodicNS,isPeriodicEW)

    elif 2*(s1[0]-s2[0]) < -width and 2*(s1[1]-s2[1]) < -height:
        s2m = periodic_translate(_s2,I[:,0],I[:,1],-1,-1)
        tx = (0.0-s1[0])/(s2m[0]-s1[0])
        ty = (0.0-s1[1])/(s2m[1]-s1[1])
        if args.debug: print tx,s(tx,s1,s2m),ty,s(ty,s1,s2m)
        stx_o = periodic_translate(s(tx,s1,s2m),I[:,0],I[:,1],1,0)
        sty_o = periodic_translate(s(ty,s1,s2m),I[:,0],I[:,1],1,0)
        out = [[_s1,s(tx,s1,s2m)],[stx_o,sty_o],[periodic_translate(sty_o,I[:,0],I[:,1],0,1),_s2]]
        if args.debug: print 4, tx,ty,s2m, out
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

tmpim = Image.new('RGBA',(im.width,im.height),(0,0,0,0))
draw = ImageDraw.Draw(tmpim,mode='RGBA')

# custom colors for rendering
color = dict()
color['mountain'] = args.color_mountain_path
color['river'] = args.color_river_path
color['aquatic'] = args.color_aquatic_path
color['amphibious'] = args.color_amphibious_path
color['normal'] = args.color_normal_path
color['info-only'] = args.color_info_only_path

def drawConnection(drawObj, segs, color,width=6):
    if len(segs)==1: 
        drawObj.line(segs[0],fill=color,width=6)
    if len(segs)==2: 
        drawObj.line(segs[0],fill=color,width=6)
        drawObj.line(segs[1],fill=color,width=6)
    if len(segs)==3: 
        drawObj.line(segs[0],fill=color,width=6)
        drawObj.line(segs[1],fill=color,width=6)
        drawObj.line(segs[2],fill=color,width=6)

# load a font
fontsize = max(im.width,im.height)/75 if args.fontsize_province_number <= 0 else args.fontsize_province_number

fnt = ImageFont.truetype(args.fontface,fontsize)

import random
# NO MORE RANDOM NUMBERS PAST THIS 
random.seed(2718)

""" Example section of taking a map, turning off some throne locations, turning
on some caves, turning off the thrones that were already on"""
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

# draw connections based on input
if args.connection_types == 'all':
    keys = ('normal','mountain','river','aquatic','amphibious','info-only')
elif args.connection_types == 'passable':
    keys = ('normal','mountain','river','aquatic','amphibious')
else:
    keys = [args.connection_types]

for key in keys:
    for x in connections[key]:
        decision_inputs = (x,line(x),(im.width,im.height),isPeriodicNS,isPeriodicEW)
        displayThisPath = eval("profiles."+args.profile).path_filter(*decision_inputs)
        if displayThisPath: 
            segs = periodic(line(x)[0],line(x)[1],(im.width,im.height),isPeriodicNS,isPeriodicEW)
            # for seg in segs: print sum((array(seg[0])-array(seg[1]))**2)
            # the above will allow for separate line behavior based on segment length
            # unfortunately a custom line style will need to be made, and thats not 
            # happening yet
            drawConnection(draw,segs,color[key])

# label all points
for k,xy in zip(range(1,len(whites_xy)+1),whites_xy):
    xymod = (xy[0] - fontsize * (xy[0] > im.width - fontsize),xy[1] - fontsize * (xy[1] > im.height-fontsize))
    decision_inputs = (args.color_province_number, k, provinceValue(k,mapfiledata), xy)
    displayThisLabel = eval("profiles."+args.profile).province_filter(*decision_inputs)
    if displayThisLabel:
        useFill = eval("profiles."+args.profile).color_scale_transform(*decision_inputs)
        draw.text(xymod,str(k),font=fnt,fill=useFill)


# form export images

# offset is the original image with appropriate offsets
composite = Image.alpha_composite(im,tmpim)
offset = ImageChops.offset(composite,args.offset_x,args.offset_y)

# test is reduced image 
test = offset.resize((im.width/args.image_reduce,im.height/args.image_reduce),Image.NEAREST)
if not args.noshow: offset.show()
if args.saveas == defaults.outfile:
    test.save(eval(defaults.outfile))
else:
    test.save(args.saveas)

# textual analysis 
final_province_types = [MaskFromValue(provinceValue(prov,mapfiledata)) for prov in range(1,len(whites_xy)+1)]
results = sum(array(final_province_types),axis=0)
results[0] = list(sum(array(final_province_types),axis=1)).count(0)
numsea = results[terrainText.index('Sea')]
numland = len(whites_xy)-numsea

print("\n========= Stats ({0:3d} / {1:3d})=========".format(numland,numsea))
print("{1:>4s} {2:>5s}   {0:s}".format('Type', '#', '%'))
print("====================================")
for key, result in zip(terrainText, results):
    print("{1:4d} {2:5.2f}% {0:s}".format(key, result, result*100.0/len(whites_xy)))
