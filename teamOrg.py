#!/usr/bin/env python
import re,csv, numpy, itertools, datetime, math
file = open('Round 4_ FFA.csv','r')
data = list(csv.DictReader(file))
file.close()

def norm_choice(list_of_arrays): return numpy.round(numpy.sum(numpy.array(list_of_arrays)**2),0)
def averageChoice(x):
    try:
        return numpy.average(x)
    except:
        counts = sorted([[l,x.count(l)] for l in x],key= lambda x: x[1])
        return counts[0][0]

def allValuesByName(data,name,*args):
    tmp = lambda n: n if len(args)==0 else args[0]+n
    def conversion(field,fallback):
        if 'Top 5 ' in field: return int
        if 'Skill Rankings ' in field: return float
        if 'Teamwork ' in field: return float
        if 'Starting Positions? ' in field: return lambda x:'Totally Random'
        return fallback

    return [conversion(tmp(name),lambda x:x)(_dict[tmp(name)]) for _dict in data if name not in _dict['Who are you?']]

# process names
#
names = [datum['Who are you?'] for datum in  data]
names_nation = [key[6:] for key in data[0].keys() if key[0:6]=='Top 5 ']
name_ptr_names_nation = {key1:key2 for key1 in names for key2 in names_nation if key1 in key2}
preambles = ['Top 5 ','Skill Rankings ','Teamwork ']

# purge unavailable players from dataset
print names


# buff dataset for nonanswer players to the average
average_player_rankings = sorted([[player,numpy.average(allValuesByName(data, name_ptr_names_nation[player],'Top 5 '))] for player in names],key=lambda x: x[1])
print average_player_rankings
print 'adjusted:'
adj_average_player_rankings = {average_player_rankings[i][0]:i+1 for i in range(0,len(average_player_rankings))}
preamble_function = {'Top 5 ':lambda x: adj_average_player_rankings[x], 'Skill Rankings ':lambda x: averageChoice(allValuesByName(data,name_ptr_names_nation[x],'Skill Rankings ')), 'Teamwork ':lambda x: averageChoice(allValuesByName(data,name_ptr_names_nation[x],'Teamwork '))}
print 
for name in set(names_nation).difference([name_ptr_names_nation[datum['Who are you?']] for datum in data]):
	print "missing ",name
	new = {key: averageChoice(allValuesByName(data,key)) for key in data[0].keys()}
	new['Timestamp']=datetime.datetime.now().isoformat(sep=' ')
	new['Who are you?']=re.findall(r"\[(.*)\(",name)[0].strip()
	print "generated:",new
	data.append(new)

names = [datum['Who are you?'] for datum in  data]
names_nation = [key[6:] for key in data[0].keys() if key[0:6]=='Top 5 ']
name_ptr_names_nation = {key1:key2 for key1 in names for key2 in names_nation if key1 in key2}
print names

def happiness(player,team,preamble = 'Top 5 '):
    try:
        conversion = {'Top 5 ': int, 'Skill Rankings ': float, 'Teamwork ': float}
        return [conversion.get(preamble,lambda x:x)(datum[preamble+name_ptr_names_nation[player]]) for datum in data for teammember in team if datum['Who are you?']==teammember and player != teammember]
    except:
        print player, teammember, datum['Who are you?']
        raise

def teamhappiness(team):
    return norm_choice([happiness(player,team) for player in set(team)])

print 'Happiness Evaluation'
preamble = preambles[1]
happiness_database = [list(itertools.chain.from_iterable([[set(team)],[norm_choice([happiness(player,team,preamble) for player in set(team)]) for preamble in preambles],[set(names).difference(team)],[norm_choice([happiness(player,team,preamble) for player in set(names).difference(team)]) for preamble in preambles]])) for team in itertools.combinations(names,int(math.floor(len(names)/2.0)))]

#trim out flips
for row in happiness_database:
	try: happiness_database.remove([row[2],row[3],row[0],row[1]])
	except: pass

print '=====best======'
happiness_database.sort(key=lambda x: min(x[1],x[5]))
for l in happiness_database[0:10]: print l
print '=====worst======'
happiness_database.sort(key=lambda x: max(x[1],x[5]),reverse=True)
for l in happiness_database[0:10]: print l

print '=====balanced==========='
happiness_database.sort(key=lambda x: abs(x[1]-x[5])+min(x[1],x[5]))
for l in happiness_database[0:10]: print l
print '=====most imbalanced======'
happiness_database.sort(key=lambda x: abs(x[1]-x[5])+min(x[1],x[5]),reverse=True)
for l in happiness_database[0:10]: print l

print 'Global Valuation'
#global_database = [[set(team),norm_choice([allValuesByName(data,name_ptr_names_nation[player],preamble) for player in team]),set(names).difference(team),norm_choice([allValuesByName(data,name_ptr_names_nation[player],preamble) for player in tuple(set(names).difference(team))])] for team in itertools.combinations(names,int(math.floor(len(names)/2.0)))]
def teamStats(team):
    ans = [norm_choice([happiness(player,team) for player in set(team)]),
            norm_choice([allValuesByName(data,name_ptr_names_nation[player],'Skill Rankings ') for player in team]),
            norm_choice([allValuesByName(data,name_ptr_names_nation[player],'Teamwork ') for player in team])]
    return ans

#mixed database
global_database = [list(itertools.chain.from_iterable([[set(team)],teamStats(team),[set(names).difference(team)],teamStats(tuple(set(names).difference(team)))])) for team in itertools.combinations(names,int(math.floor(len(names)/2.0)))]

# trim out flips
for row in global_database:
	try: global_database.remove(list(itertools.chain.from_iterable([row[4:],row[0:4]]))) 
	except: pass
print '=====best======'
global_database.sort(key=lambda x: min(x[1],x[5]))
for l in global_database[0:10]: print l
print '=====worst======'
for i in range(3):
    global_database.sort(key=lambda x: max(x[i+1],x[i+5]),reverse=True)
    print i+1
    for l in global_database[0:3]: print l

print '=====balanced==========='
global_database.sort(key=lambda x: numpy.sum(numpy.abs(numpy.array(x[1:4])-numpy.array(x[5:8]))**2))
#global_database.sort(key=lambda x: numpy.sum((numpy.array(x[1:4])-numpy.array(x[5:8]))**2))
#global_database.sort(key=lambda x: numpy.sum((numpy.array(x[2:4])-numpy.array(x[6:8]))**2))
for l in global_database[0:10]: print l
print '=====most imbalanced======'
global_database.sort(key=lambda x: abs(x[1]-x[5]),reverse=True)
for l in global_database[0:10]: print l
