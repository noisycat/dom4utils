import re, math, os, itertools, argparse, io
# Need Pillow
from PIL import Image, ImageDraw, ImageFont, ImageChops
# Need Wand
import wand.image

parser = argparse.ArgumentParser(description='Dominions 4 Map Analyzer')
parser.add_argument('mappath',type=str)
parser.add_argument('--dom4mapspath',type=str)
parser.add_argument('--noshow',nargs='?',const=True,default=False,type=bool)
args = parser.parse_args()
# suck in map file
dominions_install=r"/Users/charles/Library/Application Support/Steam/SteamApps/common/Dominions4/maps/"

mapfolder= os.path.dirname(args.mappath)
mapname = os.path.basename(args.mappath)
mapfile = open(os.path.join(mapfolder,mapname))
mapfiledata = mapfile.read()

# suck in map image
mapfiledata = re.sub(r'#dom2title (.+)$',r'#dom2title "\1 Competitive"$',mapfiledata)
mapimagefilename = re.findall(r'#imagefile (\S+)$',mapfiledata,re.M)[0]
print mapfolder, mapimagefilename
try:
				im = Image.open(os.path.join(mapfolder,mapimagefilename))

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

# check periodicity
isPeriodicNS = True if re.search('#vwraparound',mapfiledata) or re.search('#wraparound',mapfiledata) else False
isPeriodicEW = True if re.search('#hwraparound',mapfiledata) or re.search('#wraparound',mapfiledata) else False
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

def setType(terrainNum,terrainKey,val):
				results = re.findall("#terrain {0} (\S+)".format(terrainNum),mapfiledata)
				mask = breakdown(int(results[0]))
				mask[getBit(terrainKey)] = int(bool(val))
				results = re.sub("#terrain {0} (\S+)".format(terrainNum),"#terrain {0} {1}".format(terrainNum,rebuildMask(mask)),mapfiledata)
				return results

def flipType(terrainNum,terrainKey):
				results = re.findall("#terrain {0} (\S+)".format(terrainNum),mapfiledata)
				mask = breakdown(int(results[0]))
				mask[getBit(terrainKey)] = (mask[getBit(terrainKey)]+1) % 2
				results = re.sub("#terrain {0} (\S+)".format(terrainNum),"#terrain {0} {1}".format(terrainNum,rebuildMask(mask)),mapfiledata)
				return results

def checkType(terrainNum,terrainKey):
				results = re.findall("#terrain {0} (\S+)".format(terrainNum),mapfiledata)
				mask = breakdown(int(results[0]))
				return (terrainKey in interpretMask(mask))

# build connectivity by type
terrain_types = re.findall("#terrain (\S+) (\S+)",mapfiledata)
connections = dict()
connections['all'] = set([(int(s[0]),int(s[1])) for s in re.findall("#neighbour (\S+) (\S+)",mapfiledata)])
connections['river'] = set([(int(s[0]),int(s[1])) for s in re.findall("#neighbourspec (\S+) (\S+) 2",mapfiledata)])
connections['mountain'] = set([(int(s[0]),int(s[1])) for s in re.findall("#neighbourspec (\S+) (\S+) 1",mapfiledata)])
connections['land'] = filter(lambda x: x in connections['mountain'] or x in connections['river'], connections['all'])
connections['water-water']  = filter(lambda x: (checkType(x[0],'Sea') and checkType(x[1],'Sea')), connections['all'])
connections['water-land'] = filter(lambda x: (checkType(x[0],'Sea') or checkType(x[1],'Sea')), connections['all'].difference(connections['water-water']))
connections['normal'] = connections['all'].difference(connections['river'],connections['mountain']).difference(connections['water-water']).difference(connections['water-land'])

import numpy

def periodic_translate(s,a1,a2,i,j):
				return tuple(s + numpy.array(a1) * i + numpy.array(a2) * j)

s = lambda t,i_s1,i_s2: tuple(numpy.array(numpy.array(i_s1,dtype=int) + t * (numpy.array(i_s2,dtype=int) - numpy.array(i_s1,dtype=int)),dtype=int))

def periodic(_s1,_s2,image_dimensions,isPeriodicNS=True,isPeriodicEW=True):
				width = im.width
				height = im.height
				s1 = numpy.array(_s1)
				s2 = numpy.array(_s2)


				I = numpy.array([[width, 0],[0,height]])
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
color['mountain'] = (200,130,0,255)
color['river'] = (0,0,255,255)
color['water-water'] = (0,130,255,255)
color['water-land'] = (130,255,130,255)
color['normal'] = (0,0,0,255)

color['purple'] = (255,0,255,255)
color['black'] = (0,0,0,255)
color['red'] = (255,0,0,255)
color['white'] = (255,255,255,255)
color['gold'] = (255,140,0,255)
color['brightgreen'] = (0,140,0,255)

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
fontsize = 40
fnt = ImageFont.truetype('Arial.ttf',fontsize)

import random
# NO MORE RANDOM NUMBERS PAST THIS 
random.seed(2718)

if 0:
				#changes to map data
				for k in range(1,len(whites_xy)+1):
								#if checkType(k,'Throne'): mapfiledata = flipType(k,'Throne')

								#new caves
								if (k in [6, 149, 151]): mapfiledata = setType(k,'Cave',True)

								# new manual thrones
								if (k in [114,92,63,32,88]) or (k in [124,85,39,23,123]): mapfiledata = setType(k,'Start',True)

								# turning off these thrones
								if (k in [1,77,93,37,3]): mapfiledata = setType(k,'Throne',False)

#select out territories
def numLandConnections(k,connectors): return len(filter(lambda xx: k in xx, connectors))
def checkNeighbors(k,flag,connectors): 
				return any([checkType(x,flag) for x in itertools.chain.from_iterable(filter(lambda xx: k in xx, connectors))])
ratios = map(lambda x: 1 if 4 <= numLandConnections(x,connections['normal'].union(connections['river'],connections['mountain'])) and not checkType(x,'Nostart') else 0, range(1,len(terrain_types)+1))
#ratios = map(lambda x: 1 if 4 <= numLandConnections(x,connections['normal'].union(connections['river'],connections['mountain'])) and not checkType(x,'Nostart') and not checkNeighbors(x,'Throne',connections['normal'].union(connections['river'],connections['mountain'])) else 0, range(1,len(terrain_types)+1))

# draw connections
for key in ('normal','mountain','river','water-water','water-land'):
				for x in connections[key]:
								#if checkType(x[0],'Start') or checkType(x[1],'Start'): 
												segs = periodic(line(x)[0],line(x)[1],(im.width,im.height))
												drawConnection(draw,segs,color[key])
# label all points
for k,xy in zip(range(1,len(whites_xy)+1),whites_xy):
				xymod = (xy[0] - fontsize * (xy[0] > im.width - fontsize),xy[1] - fontsize * (xy[1] > im.height-fontsize))
				if checkType(k,'Throne'): 
								draw.text(xymod,str(k),font=fnt,fill=color['gold'])
								print "Throne ",k

				if checkType(k,'Large Province') and checkType(k,'Farm'):
								draw.text(xymod,str(k),font=fnt,fill=color['red'])
								pass

				if checkType(k,'Waste'):
								draw.text(xymod,str(k),font=fnt,fill=color['purple'])
								pass

				#elif checkNeighbors(k,'Throne',connections['all']):
				#				pass

				else:
								scaled_color = tuple(itertools.chain.from_iterable((numpy.array(numpy.array(color['red'])*ratios[k-1],dtype=int)[0:3],(255,))))
								draw.text(xymod,str(k),font=fnt,fill=tuple(scaled_color))

offset = ImageChops.offset(im,im.width/2+50,-im.height/2)
if not args.noshow: offset.show()
test = im.resize((im.width/2,im.height/2),Image.NEAREST)
test.save(mapname+'_connections.png')
offset = offset.resize((im.width/2,im.height/2),Image.NEAREST)
offset.save(mapname+'_ours.png')
print [(key,[checkType(k,key) for k in range(1,len(whites_xy)+1)].count(True)) for key in interpretMask(tuple((1,)*27))]
print [k for k in range(1,len(whites_xy)+1) if checkType(k,'Mountain') ]
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
