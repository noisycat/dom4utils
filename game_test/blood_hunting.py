import argparse, random
from dice_roller import open_roll, drn, DRN
import loadData

class Province():
    def __init__(self, population, unrest = 0, provincal_defense = 0, admin_value = 0, growth = 0, seed = random.randint(1,2**64-1)):
        self.population = population
        self.unrest = unrest
        self.pd = provincal_defense
        self.admin = admin_value
        self.hunters = list()
        self.growth = growth
        self.slaves = 0
        self.patrolmurdered = 0
        self.patrollers = list()
        random.seed(seed)

    def __str__(self):
        return "{0} {1} {2} {3} {4}".format(self.population,self.unrest,self.pd,self.slaves,self.incomePercent())

    def addHunters(self,*args):
        self.hunters.extend(args)

    def proficiencyCheck(self,hunter):
        return hunter.proficiencyCheck()

    def unrestCheck(self,*args):
        return random.random() > self.unrest / 400.

    def populationCheck(self,*args):
        return random.random() < self.population / 5000.

    def incomePercent(self):
        return (1+self.admin/200.)/(1+.02*self.unrest)

    def patrolPurge(self):
        # destealth
        self.destealth = int(sum(map(lambda x: x.destealth,self.patrollers))) - min(unrest/2,50)+max(self.pd - 14,0)
        effectiveness = self.destealth + open_roll(1,25)+open_roll(1,25)-open_roll(1,25)-open_roll(1,25)

        patrol = self.pd / 10
        self.patrolmurdered += patrol
        self.unrest -= patrol
        return patrol 
    
    def addPatrollers(self,*args):
        self.patrollers.extend(args)
        for arg in args:
            destealth = (arg.precision + 30)/20. if arg.flying else (arg.precision + arg.AP)/20.


    def Turn(self):
        output = "POP({0:05}) UNREST({1:04}) ".format(self.population,self.unrest)
        # hunter checks
        results = list()
        for hunter in self.hunters: 
            if self.proficiencyCheck(hunter) and self.unrestCheck() and self.populationCheck():
                slaves, unrest = hunter.slavesUnrest()
                self.population -= slaves
                self.slaves += slaves
                self.unrest += unrest
                results.append((slaves,unrest))
            # blood hunt fails
            else:
                results.append((0, random.randint(1,6)-1))
                self.unrest += random.randint(1,6)-1

        for result in results: output += "({0:2},{1:2}) ".format(*result)

        # income
        output += "{:.2%} ".format(self.incomePercent())

        # murder through patrolling
        output += "{0:4} ".format(self.patrolPurge())

        # growth
        output += "UNR({1:4}) POP({0:05}) ".format(self.population,self.unrest)
        self.population = int(self.population * (1.0 + .002 * self.growth))
        output += "POP({0:05}) TOTAL({1})".format(self.population, self.slaves)
        return output

    def Destealth(self):
        sum(map(lambda x: x.destealth(), self.patrollers)) - min(self.unrest/2,50) + max(self.pd - 14,0)


class Patroller():
    def __init__(self, entry):
        self.ap = int(entry['ap'])
        self.prec = int(entry['prec'])
        self.flying = not entry['flying']==''
        self.patrolbonus = 0 if entry['patrolbonus']=='' else int(entry['patrolbonus'])

    def destealth(self):
        return self.patrolbonus + (30 + self.prec)/20. if self.flying else self.patrolbonus + (self.ap + self.prec) / 20. 

class Hunter():
    def __init__(self, level, natural_bonus, item_bonus):
        self.level = level
        self.natural_bonus = natural_bonus
        self.item_bonus = item_bonus
        self.bonus = self.natural_bonus + self.item_bonus

    def calcBonus(self):
        self.bonus = self.natural_bonus + self.item_bonus

    def proficiencyCheck(self):
        return random.random() < (.10 + (self.level+self.bonus) * .40)

    def slavesUnrest(self):
        slaves = self.slaveGenerate()
        unrest = self.unrestGenerate(slaves)
        return (slaves,unrest)

    def slaveGenerate(self):
        # apparently 30 is the cap value
        return min(drn()+self.bonus,30)

    def unrestGenerate(self,slaves):
        return open_roll(3 * slaves + 4)
    
if __name__ == '__main__':
    Wayz = Hunter(1,1,1)
    Home = Province(7000,growth=3)
    Home.addHunters(Wayz,Wayz,Wayz)
    for turn in range(10): print turn,Home.Turn()

    print " With patrol defense"
    Home = Province(7000,provincal_defense=10,growth=3)
    Home.addHunters(Wayz,Wayz,Wayz)
    for turn in range(10): print turn,Home.Turn()

    main = loadData.dom4inspector('../dom4inspector')
    main.loadData()
    print loadData.getTokenByField(main.BaseU,'Zotz Warrior','name')

    
