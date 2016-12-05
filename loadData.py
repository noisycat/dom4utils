import argparse, csv
from os import listdir, path
class gamedata:
    def __init__(self,_path):
        self.path = _path
        self.data = dict()

def getTokenByField(_dict,_care,field_to_search, field_to_get='id'):
    return list(k[field_to_get] for k in _dict if k[field_to_search]==_care)[0]
    

def getAllTokenByField(_dict,_care,field_to_search, field_to_get='id'):
    return list(k[field_to_get] for k in _dict if k[field_to_search]==_care)

class dom4inspector:
    def __init__(self,_path):
        self.gamedata = gamedata(path.join(_path,'gamedata'))
        self.BaseU = None

    def loadData(self):
        for csv_file in [path.join(self.gamedata.path,file) for file in listdir(self.gamedata.path) if (file[0] != '.' and path.isfile(path.join(self.gamedata.path,file)))]:
            csvfile = open(csv_file,'rb')
            self.gamedata.data[path.basename(csv_file)] = list(csv.DictReader(csvfile,delimiter='\t') )
            csvfile.close()
        # aliases
        self.BaseU = self.gamedata.data['BaseU.csv']

    def compareSpells(self,spell1,spell2):
        spells = self.gamedata.data['spells.csv']
        spell1_id = int(list(x['id'] for x in spells if x['name'] == spell1)[0])
        spell2_id = int(list(x['id'] for x in spells if x['name'] == spell2)[0])
        effects = self.gamedata.data['effects.csv']
        effect1_id = int(getTokenByField(effects, spells[spell1_id]['effect_record_id'], 'record_id', 'record_id'))-1
        effect2_id = int(getTokenByField(effects, spells[spell2_id]['effect_record_id'], 'record_id', 'record_id'))-1
        return (spell1_id, spell2_id)
        
    def optimalPretender(self,nation,bless):
        pretender_names = self.list_pretenders(nation)
        print pretender_names

    def list_pretenders(self,nation):
        nation_num = getTokenByField(self.gamedata.data['nations.csv'],nation,'file_name_base','id')
        tokens = getAllTokenByField(self.gamedata.data['pretender_types_by_nation.csv'],nation_num,'nation_number','monster_number')
        tokens.extend(getAllTokenByField(self.gamedata.data['unpretender_types_by_nation.csv'],nation_num,'nation_number','monster_number'))
        monsters = [ getAllTokenByField(self.gamedata.data['BaseU.csv'],monster_num,'id','name') for monster_num in tokens]
        return [monster[0] for monster in monsters]

    def summon_spell_strengths(self,**kwargs):
    	# effect number = 1 or 37 or 42
    	spells = self.gamedata.data['spells.csv']
    	summon_spells = filter(lambda x: x['effect_number'] in ['1','21','92','37','89','68'] and x['object_type']=='Spell',self.gamedata.data['effects.csv'])
# spell id, effects, gemcost  IFF its a summon spell
    	effect_count = map(lambda x: (x['id'],x['effects_count'],x['gemcost'],x['effect_record_id']), filter(lambda y: y['effect_record_id'] in map(lambda z: z['record_id'],summon_spells),spells))
    	summon_spells2 = map(lambda x: (x[0],x[1],x[2],filter(lambda y: x[3]==y['record_id'],self.gamedata.data['effects.csv'])[0]['raw_argument']), effect_count)
    	creatures = map(lambda z: z['name'], filter(lambda y: y['id'] in map(lambda x: x['raw_argument'],summon_spells),self.gamedata.data['BaseU.csv']))
    	return creatures, effect_count, summon_spells2



if __name__ == "__main__":
    DOM4INSPECTORPATH='../dom4inspector'
    main = dom4inspector(DOM4INSPECTORPATH)
    main.loadData()	

    #example inspection of a certain unit e.g. "Black Hawk"
    name_entrynum = map(lambda x: x["name"], main.gamedata.data['BaseU.csv']).index("Black Hawk")

    for z,y in [x for x in main.gamedata.data['BaseU.csv'][name_entrynum].iteritems() if x[1] != '']:
        print z,y

    print '------'

# cross reference with that unit's spell entry?
    entrynum = 636
    for z,y in [x for x in main.gamedata.data['spells.csv'][entrynum].iteritems() if x[1] != '']:
        print z,y

    print '------'
# and now for effect record
    entrynum = 1305
    for z,y in [x for x in main.gamedata.data['effects.csv'][entrynum].iteritems() if x[1] != '']:
        print z,y


    spells = main.gamedata.data['spells.csv']
    all_summoned_units_str = map(lambda x: (x['name'],int(x['str'])), filter(lambda x: x['from']=='Summon',main.gamedata.data['BaseU.csv']))

    test = main.compareSpells('Invulnerability','Mistform')
    main.optimalPretender("mid_sceleria","E4A9D9")

    v = main.summon_spell_strengths()
