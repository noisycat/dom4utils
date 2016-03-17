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


if __name__ == "__main__":
				DOM4INSPECTORPATH='../dom4inspector'
				main = dom4inspector(DOM4INSPECTORPATH)
				main.loadData()	

				#example inspection of a certain unit e.g. "Black Hawk"
				entrynum = map(lambda x: x["name"], main.gamedata.data['BaseU.csv']).index("Black Hawk")

				for z,y in [x for x in main.gamedata.data['BaseU.csv'][entrynum].iteritems() if x[1] != '']:
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

				test = main.compareSpells('Invulnerability','Mistform')
				main.optimalPretender("mid_sceleria","E4A9D9")
