import json

battle = {}
p1a = Player()		
p2a = Player()
turn = ""

#p1cur
#p2cur

class Player:
	def __init__(self)
		self.name = ""
		self.pokemon = {}
		
class Pokemon:
	def __init__(self, pkname):
		self.name = pkname
		self.nickname = ""
		self.item = ""
		self.ability = ""
		self.move = []
		
		
#This is the parsing function		
def parse_line(input):
	#Take the input
	#Split it up
	#switch/If it into proper function
	data = input.split("|")
		
	
def tier(input)
	bataleData["tier"] = input[2]

#input the players into the data table
def player(input):
	if(input[2] == "p1"):
		p1a.name = input[3]
	else:
		p2a.name = input[3]

#|poke|p1|Togekiss, F
def pokemon(input):
	if(input[2] == "p1")
		p1a.pokemon[input[3]] = Pokemon(input[3])
	else:
		p2a.pokemon[input[3]] = Pokemon(input[3])

#|switch|p2a: LCS is on rn|Dialga|243\/404
#|drag|p1a: Vaporeon|Vaporeon, F|379\/463
def switch(input):
	nick = input[2].split(":")
	name = input[3].split("-") #done so megas keep same dictonary entry
	if("p1a:" in input[2]):
		p1cur = p1a.pokemon[name]
		p1cur.nickname = nick[1].lstrip()

	else:
		p2cur = p2a.pokemon[name]
		p2cur.nickname = nick[1]

#|-ability|p2a: LCS is on rn|Pressure		
def ability(input):
	if("p1a:" in input[2]):
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
	if("p1a:" in input[2]):
		if(input[3] not in p1cur.move):
			p1cur.move.append(input[3])
	else:
		if(input[3] not in p2cur.move):
			p2cur.move.append(input[3])


#|-heal|p1a: Pokemon|###\/###|[from] drain|[of] p2a: Pokemon
#|-heal|p1a: Pokemon|###\/###|[from] item: Leftovers
def heal(input):
	nick = input[2].split(":")
	if("p1a" in nick[0]):
		
	else:
		
#|-enditem|p2a: Umbreon|Red Card|[of] p1a: Lopunny
#|-enditem|p2a: Zell|Normal Gem|[from] gem|[move] Quick Attack
def item(input):
	

def resisted(input):

def faint(input):
# |turn|1
def turn(input):
	turn = input[3]

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
		