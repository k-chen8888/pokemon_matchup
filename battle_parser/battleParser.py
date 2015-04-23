#Use json to output the battle into
import json
#use REs for indexing
import re


# Uses beautifulsoup to scrape
from bs4 import BeautifulSoup, SoupStrainer

# Uses requests to access pages
import requests

# for reading the log
import StringIO

#sys.setdefaultencoding('utf-8')


def theParser(webpage):
	
	#scrape the data from the webpage url
	r = requests.get(webpage)
	page_source = r.text
	
	#feed the source into beautiful soup
	soup = BeautifulSoup(page_source)
	soup.prettify()
	
	log = soup.find("script", {"class" : "log"})
	
	blog = StringIO.StringIO(log)
	line = blog.readline()
	while line is not "":
		print line
		parse_line(line)
		line = blog.readline()
		
	
	#create a jSon
	toJson()
	print "done"
	
'''
These functions work on the following basis:
	Above each parse function is a comment with examples
	of the data that we expect to read in that function
	the list input is passed in after the original string
	is split with "|" as the delimiter
	counting starts from 0, however, there is nothing before
	the first "|" so counting words starts from 1
'''

weather = { "RainDance":0, "PrimordialSea":0, "SunnyDay":0, "DesolateLand":0, "Sandstorm":0, "Hail":0, "DeltaStream":0, "none":1}




class Player:
	def __init__(self):
		self.cur = None
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

tier = ""
win = ""
p1a = Player()		
p2a = Player()
turn = ""
	
def tierf(input):
	tier = input[2]

#|win|Anzle
def winf(input):
	win = input[2]

#|player|p1|pansexual skitty|100
def player(input):
	if len(input) > 3:
		if "p1" in input[2]:
			p1a.name = input[3]
		else:
			p2a.name = input[3]

		
'''Pokemon name keys are inserted as the pokemon's name with
	no extra markings for the time being. ie. "Togekiss, F" goes in as
	""Togekiss" this is done because names will change as pokemon
	forms change and I want an easy way to index the pokemon out
	HOWEVER the name field of the pokemon will keep
	the Pokemon's full name. ie. "Togekiss, F" '''
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
	name = re.split("\W", input[3]) #<--- using only "Vaporeon" to switch
	if "p1a:" in input[2]:
		p1a.cur = p1a.pokemon[name[0]]
		p1a.cur.nickname = nick[1].lstrip()

	else:
		p2a.cur = p2a.pokemon[name[0]]
		p2a.cur.nickname = nick[1].lstrip()

#|-ability|p2a: LCS is on rn|Pressure		
def ability(input):
	if "p1a:" in input[2]:
		p1a.cur.ability = input[3]
	else:
		p2a.cur.ability = input[3]

'''This can be inproved to catch items'''
#|detailschange|p1a: i built that.|Kyogre-Primal
def transformation(input):
	nick = input[2]
	if "p1a:" in input[2]:
		p1a.cur.name = input[3]
	else:
		p2a.cur.name = input[3]

#|-mega|p2a: steeljackal<3|Sableye|Sablenite
def mega(input):
	if "p1a:" in input[2]:
		p1a.cur.item = input[4]
	else:
		p2a.cur.item = input[4]
		
#|move|p1a: Lopunny|Fake Out|p2a: Umbreon
def move(input):
	if "p1a:" in input[2]:
		if(input[3] not in p1a.cur.move):
			p1a.cur.move.append(input[3])
	else:
		if(input[3] not in p2a.cur.move):
			p2a.cur.move.append(input[3])


#|-heal|p1a: Pokemon|###\/###|[from] drain|[of] p2a: Pokemon
#|-heal|p1a: Pokemon|###\/###|[from] item: Leftovers
def heal(input):
	
	nick = input[2].split(":")
	if "p1a" in nick[0]:
		p1a.heals = p1a.heals + 1
		if len(input) > 4 and "item" in input[4]:
			item = input[4].split(":")
			p1a.cur.item = item[1].lstrip()
	else:
		p2a.heals = p2a.heals + 1
		if len(input) > 4 and "item" in input[4]:
			item = input[4].split(":")
			p2a.cur.item = item[1].lstrip()
		
#|-enditem|p2a: Umbreon|Red Card|[of] p1a: Lopunny
#|-enditem|p2a: Zell|Normal Gem|[from] gem|[move] Quick Attack
def item(input):
	if "p1a:" in input[2]:
		p1a.cur.item = input[3]
	else:
		p2a.cur.item = input[3]

#|-boost|p2a: Genesect-Burn|spa|1|[from] ability: Download
def boost(input):
	if len(input) > 5:
		if "p1a" in input[2]:
			if "ability" in input[5]:
				p1a.cur.ability = input[5].split(":")[1].lstrip
		else:
			if "ability" in input[5]:
				p2a.cur.ability = input[5].split(":")[1].lstrip
	#else: could get stat boosts			
			
#|-damage|p1a: Foxheart|244\/271|[from] item: Life Orb
#|-damage|p1a: Foxheart|184\/271 slp|[from] ability: Bad Dreams	
def damage(input):
	if len(input) >	4:
		if "p1a" in input[2]:
			if "item" in input[4]:
				p1a.cur.item = input[4].split(":")[1].lstrip()
			elif "ability" in input[4]:
				p1a.cur.ability = input[4].split(":")[1].lstrip()
		else:
			if "item" in input[4]:
				p2a.cur.item = input[4].split(":")[1].lstrip()
			elif "ability" in input[4]:
				p2a.cur.ability = input[4].split(":")[1].lstrip()
			
#|-weather|RainDance
def weatherf(input):
        if input[2][-1] == '\n':
                index = input[2][:-1]
        else:
                index = input[2]
        wea = weather[index]
        wea += 1
        weather[index] = wea
	
# |turn|1
def turnf(input):
	turn = input[2]
	
#|-status|p1a: i built that.|tox
#|-status
#|brn, par, slp, frz, psn, tox, 
def status(input):	
	if "p1a:" in input[2]:
		stus = p1a.cur.status[input[3][:-1]]
		stus += 1
		p1a.cur.status[input[3][:-1]] = stus
	else:
		stus = p2a.cur.status[input[3][:-1]]
		stus += 1
		p2a.cur.status[input[3][:-1]] = stus


#|confusion, trapped
#|-activate|p2a: Aegislash|confusion
def activate(input):
	if "confusion" in input[3]:
		if "p1a" in input[2]:
			conf = p1a.cur.status[input[3][:-1]]
			conf += 1
			p1a.cur.status[input[3][:-1]] = conf
		else:
			conf = p2a.cur.status[input[3][:-1]]
			conf += 1
			p2a.cur.status[input[3][:-1]] = conf
		
		
		
#|-crit|p2a: LCS is on rn
def crit(input):
	if "p1a:" in input[2]:
		p2a.cur.crit += 1
	else:
		p1a.cur.crit += 1

#|-sidestart|p2: Jibaku|move: Stealth Rock
def inhaz(input):
	if "p1" in input[2]:
		p1a.hazards[input[3].split(":")[1].lstrip()] = 1;
	else:
		p1a.hazards[input[3].split(":")[1].lstrip()] = 1;


#This is the parsing function		
def parse_line(input):
	#Take the input
	#Split it up
	#switch/If it into proper function
	
	data = input.split("|")
	if data[1] == "move":	move(data)
	elif data[1] == "-damage": 	damage(data)
	elif data[1] == "turn":	turnf(data)
	elif data[1] == "-sidestart":	inhaz(data)
	elif data[1] == "switch" or data[1] == "drag":	switch(data)
	elif data[1] == "-heal": heal(data)
	elif data[1] == "-status": status(data)
	elif data[1] == "-activate": activate(data)
	elif data[1] == "-weather":	 weatherf(data)
	elif data[1] == "-boost": boost(data)
	elif data[1] == "detailschange": transformation(data)
	elif data[1] == "-mega":	mega(data)
	elif data[1] == "-ability":	ability(data)
	elif data[1] == "-enditem":	item(data)
	elif data[1] == "-crit": crit(data)
	elif data[1] == "poke":	pokemon(data)
	elif data[1] == "player": player(data)
	elif data[1] == "tier":	tierf(data)
	elif data[1] == "win":	winf(data)
		

	
def toJson():
	match = {}
	'''For each player, build their dictionary
		filling in their name, the entry hazards they used
		the pokemon they used and the number of heals they did'''
	player1 = {}
	player1["name"] = p1a.name #str
	player1["hazards"] = p1a.hazards #dict
	player1["heals"] = p1a.heals #int

	i = 1
	'''for each pokemon the player has, 
		create a dictionary with the pokemon's information, 
		then pass that dictionary to the player dictionary'''
	pokemon = p1a.pokemon
	for k in pokemon :
		poke = {}
		poke["name"] = pokemon[k].name #str
		poke["item"] = pokemon[k].item #str
		poke["ability"] = pokemon[k].ability #str
		poke["moves"] = pokemon[k].move #this is a list
		poke["status"] = pokemon[k].status #this is a dict
		poke["critical"] = pokemon[k].crit #int
		player1["pokemon"+str(i)] = poke
		i += 1

	'''Do this for player 2'''
	
	player2 = {}
	player2["name"] = p2a.name #str
	player2["hazards"] = p2a.hazards #dict
	player2["heals"] = p2a.heals #int	

	i=1
	pokemon = p2a.pokemon
	for k in pokemon :
		poke = {}
		poke["name"] = pokemon[k].name #str
		poke["item"] = pokemon[k].item #str
		poke["ability"] = pokemon[k].ability #str
		poke["moves"] = pokemon[k].move #this is a list
		poke["status"] = pokemon[k].status #this is a dict
		poke["critical"] = pokemon[k].crit #int
		player2["pokemon"+str(i)] = poke
		i += 1
		
	match["player1"] = player1
	match["player2"] = player2
	match["winner"] = win
	match["tier"] = tier
	match["weather"] = weather
	
	name = player1["name"]
	name2 = player2["name"]
	#print match
	filename = tier + "2" + name + "VS" + name2 + ".txt"
	file = open(filename, 'w')
	son = json.dumps(match, indent=2)
	file.write(son)
	#file.write(str(match))
	file.close
	






theParser("http://replay.pokemonshowdown.com/smogtours-ou-34915")






		
