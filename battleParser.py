battleData = {"tier":"-", "winner":"-", "turns":0}

p1a = Player()		
p2a =Player()

#p1cur
#p2cur

class Player:
	def __init__(self)
		self.name = ""
		#self.weather = 0
		self.formchange = 0
		self.status = 0
		self.resisted = 0
		self.supereffective = 0
		self.heal = 0
		self.pokemon = {}
		self.hazard = 0
		
class Pokemon:
	def __init__(self, pkname):
		self.name = pkname
			self.nickname = ""
		self.move = []
		self.ability = ""
		
#This is the parsing function		
def parse_line(input):
	data = input.split("|")
		
	
def tier(input)
	bataleData["tier"] = input[2]

#input the players into the data table
def player(input):
	if(input[2] == "p1"):
		p1a.name = input[3]
	else:
		p2a.name = input[3]
	
def pokemon(input):
	if(input[2] == "p1")
		p1a.pokemon[input[3]] = Pokemon(input[3])
	else:
		p2a.pokemon[input[3]] = Pokemon(input[3])

def switch(input):
	nick = input[2].split()
	if("p1a:" in nick[0]):
		p1cur = p1a.pokemon[input[3]]
		p1cur.nickname = nick[1]

	else:
		p2cur = p2a.pokemon[input[3]]
		p2cur.nickname = nick[1]

def ability(input):
	nick = input[2].split()
	if("p1a:" in nick[0]):
		p1cur.ability = input[3]
	else:
		p2cur.ability = input[3]

#def weather(input)
	
def transformation(input):
	nick = input[2].split()
	if "p1a:" in nick[0]:
		p1a.formchange += 1
	else:
		p2a.formchange += 1
	
def move(input):
	nick = input[2].split()
	if("p1a:" in nick[0]):
		if(input[3] not in p1cur.move):
			p1cur.move.append(input[3])
	else:
		if(input[3] not in p2cur.move):
			p2cur.move.append(input[3])

def entryhazard(input):
	
	
def status(input):

def heal(input):

def resisted(input):

def super_eff(input):

def faint(input):

def turn(input):