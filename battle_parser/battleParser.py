import json
import re

battle = {}
p1a = Player()		
p2a = Player()
turn = ""
weather = { "RainDance":0, "PrimordialSea":0, "SunnyDay":0, "DesolateLand":0, "Sandstorm":0, "Hail":0, "DeltaStream":0, "none":1}

#p1cur
#p2cur


class Player:
	def __init__(self)
		self.name = ""
		self.pokemon = {}
		self.heals = 0
		self.hazards = {"Spikes":0, "Stealth Rock":0, "Sticky Web":0, "Toxic Spikes":0, "Tailwind":0}
		
class Pokemon:
	def __init__(self, pkname):
		self.name = pkname
		self.nickname = ""
		self.item = ""
		self.ability = ""
		self.move = []
		self.status = {"brn":0, "par":0, "slp":0, "frz":0, "psn":0, "tox":0, "confusion":0, "trapped":0}
		self.crit = 0
		
		
		
#This is the parsing function		
def parse_line(input):
	#Take the input
	#Split it up
	#switch/If it into proper function
	data = input.split("|")
		
	
def tier(input)
	batale["tier"] = input[2]

#input the players into the data table
def player(input):
	if "p1" in input[2]:
		p1a.name = input[3]
	else:
		p2a.name = input[3]

#|poke|p1|Togekiss, F
#|poke|p1|Arceus-*
def pokemon(input):
	#Use name alphasnums for indexing
	name = re.split("\W", input[3]) 
	if "p1" in input[2]:
		p1a.pokemon[name[0]] = Pokemon(input[3])
	else:
		p2a.pokemon[name[0]] = Pokemon(input[3])

#|switch|p2a: LCS is on rn|Dialga|243\/404
#|drag|p1a: Vaporeon|Vaporeon, F|379\/463
#|switch|p1a: filthy APE|Arceus-Ghost|443\/443
def switch(input):
	nick = input[2].split(":")
	name = re.split("\W", input[3])
	if "p1a:" in input[2]:
		p1cur = p1a.pokemon[name[0]]
		p1cur.nickname = nick[1].lstrip()

	else:
		p2cur = p2a.pokemon[name[0]]
		p2cur.nickname = nick[1].lstrip()

#|-ability|p2a: LCS is on rn|Pressure		
def ability(input):
	if "p1a:" in input[2]:
		p1cur.ability = input[3]
	else:
		p2cur.ability = input[3]

#|detailschange|p1a: i built that.|Kyogre-Primal
#|-mega|p2a: steeljackal<3|Sableye|Sablenite
def transformation(input):
	nick = input[2]
	if "p1a:" in input[2]:
		p1cur.name = input[3]
	else:
		p2cur.name = input[3]

#|move|p1a: Lopunny|Fake Out|p2a: Umbreon
def move(input):
	if "p1a:" in input[2]:
		if(input[3] not in p1cur.move):
			p1cur.move.append(input[3])
	else:
		if(input[3] not in p2cur.move):
			p2cur.move.append(input[3])


#|-heal|p1a: Pokemon|###\/###|[from] drain|[of] p2a: Pokemon
#|-heal|p1a: Pokemon|###\/###|[from] item: Leftovers
def heal(input):
	nick = input[2].split(":")
	if "p1a" in nick[0]:
		p1a.heals = p1a.heals + 1
		if "item" in input[4]:
			item = input[4].split(":")
			p1cur.item = item[1].lstrip
	else:
		p2a.heals = p2a.heals + 1
		if "item" in input[4]:
			item = input[4].split(":")
			p2cur.item = item[1].lstrip
		
#|-enditem|p2a: Umbreon|Red Card|[of] p1a: Lopunny
#|-enditem|p2a: Zell|Normal Gem|[from] gem|[move] Quick Attack
def item(input):
	if "p1a:" in input[2]:
		p1cur.item = input[3]
	else:
		p2cur.item = input[3]

#|-boost|p2a: Genesect-Burn|spa|1|[from] ability: Download
def boost(input):
	if len(input) < 6:
		if "p1a" in input[2]:
			if "ability" in input[5]:
				p1cur.ability = input[5].split(":").lstrip
		else:
			if "ability" in input[5]:
				p2cur.ability = input[5].split(":").lstrip
	#else: could get stat boosts			
			
#|-damage|p1a: Foxheart|244\/271|[from] item: Life Orb
#|-damage|p1a: Foxheart|184\/271 slp|[from] ability: Bad Dreams	
def damage(input):
	if "p1a" in input[2]:
		if "item" in input[4]:
			p1cur.item = input[4].split(":").lstrip()
		elif "ability" in input[4]:
			p1cur.ability = input[4].split(":").lstrip()
	else:
		if "item" in input[4]:
			p2cur.item = input[4].split(":").lstrip()
		elif "ability" in input[4]:
			p2cur.ability = input[4].split(":").lstrip()
			
#|-weather|RainDance
def weather(input):
	turns = weather[input[2]]
	turns = times + 1
	weather[input[2]] = turns
	
# |turn|1
def turn(input):
	turn = input[3]
	
#|-status|p1a: i built that.|tox
#|-status
#|brn, par, slp, frz, psn, tox, 

def status(input):	
	if "p1a:" in input[2]:
		stus = p1cur.status[input[3]]
		stus += 1
		p1cur.status[input[3]] = stus
	else:
		stus = p2cur.status[input[3]]
		stus += 1
		p2cur.status[input[3]] = stus

#|-activate
#|confusion, trapped
		
		
#|-crit|p2a: LCS is on rn
def crit(input):
	if "p1a:" in input[2]:
		p2cur.crit += 1
	else:
		p1cur.crit += 1

#|-sidestart|p2: Jibaku|move: Stealth Rock
def inhaz(input):
	if "p1" in input[2]:
		p1a.hazards[input[3].split(":").lstrip()] = 1;
	else:
		p1a.hazards[input[3].split(":").lstrip()] = 1;


#Battle{
#	Player1 :
#		Name: 
#		Pokemon1 : {
#			Item : 
#			Ability : 
#			Move1 : 
#			Move2 :
#			Move3 :
#			Move4 :
#			}
#		Pokemon2 : 
#	Player2 :
#	Winner : 0/1
#}
		