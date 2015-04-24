import json, re, requests, StringIO
from bs4 import BeautifulSoup, SoupStrainer
from copy import deepcopy

##Class Battle: Hold the winner and the players?
class Battle:
  def __init__(self):
    self.winner = None
    self.players = {"p1a" : Player(), "p2a" : Player()}

##Class Player: Holds the player's name (team1 or team 2) and the pokemon the player has.
class Player:
  def __init__(self):
    self.name = None
    self.pokemon = {}
    self.cur = None

##Class Pokemon: holds the pokemon's name, item, and moveset.
class Pokemon:
  def __init__(self, name):
    self.name = name
    self.item = None
    self.moves = []

    
#Take the webpage and parse it into a Battle
def parse(webpage):    
  bat = Battle()
  
  print "Parsing: " + webpage
  #scrape the data from the webpage url
  r = requests.get(webpage)
  page_source = r.text
	
  #feed the source into beautiful soup
  soup = BeautifulSoup(page_source)
  soup.prettify()
	
  #get the raw battle data
  log = soup.find("script", {"class" : "log"})
	
  #read it line by line
  blog = StringIO.StringIO(log)
  line = blog.readline()
  while line is not "":
    parse_line(bat, line)
    line = blog.readline()
    
  #create a dictionary object from this battle
  battle = makedic(bat)
   
  return battle

def parse_line(bat, line):
  #remove the newline character
  if line[-1:] == '\n':
    line = line[:-1]
  
  #split up the raw line by '|' s
  raw = line.split('|')
  
  if len(raw) > 2:
    #set the player it if effecting
    if '1' in raw[2]:
      plyr = bat.players['p1a']
    else:
      plyr = bat.players['p2a']
    
    #use if-elif as a switch statement through the specific parse functions
    if 'move' in raw[1]:      move(plyr, raw)
    elif 'damage' in raw[1]:  dmgitem(plyr, raw)
    elif 'heal' in raw[1]:    healitem(plyr, raw)
    elif 'enditem' in raw[1]: enditem(plyr, raw)
    elif 'mega' in raw[1]:    megaStone(plyr, raw)
    elif 'switch' in raw[1]:  switch(plyr, raw)
    elif 'drag' in raw[1]:    switch(plyr, raw)
    elif 'change' in raw[1]:  transform(plyr, raw)
    elif 'poke' in raw[1]:    pokemon(plyr, raw)
    elif 'player' in raw[1]:  player(plyr, raw)
    elif 'win' in raw[1]:     winTeam(bat, raw)
    #else: do nothing

#Make the battle into a dictionary
def makedic(bat):    
  p1 = bat.players['p1a']
  p2 = bat.players['p2a']
  
  #declare which team won
  if p1.name == bat.winner:
    victor = "team1"
  else:
    victor = "team2"
  
  #lists for pokemon
  team1 = []
  team2 = []
  
  #fill in team 1
  pokemon = p1.pokemon
  for k in pokemon:
    poke = {}
    poke['name'] = pokemon[k].name
    poke['item'] = pokemon[k].item
    poke['moves'] = pokemon[k].moves
    team1.append(deepcopy(poke))
  
  #fill in team 2
  pokemon = p2.pokemon
  for k in pokemon:
    poke = {}
    poke['name'] = pokemon[k].name
    poke['item'] = pokemon[k].item
    poke['moves'] = pokemon[k].moves
    team1.append(deepcopy(poke))
    
  #Craft the Dictionary
  battleDic = {'team1' : team1, 'team2' : team2, 'winner' : victor}
  return battleDic
  
    
    
'''Below are the Parsing functions. Each function takes the player and the line that we
  have read in from the web page scrape '''  
#|win|Anzle    
def winTeam(bat, line):
  bat.winner = line[2]

#|player|p1|Anzle|100
def player(plyr, line):
  if len(line) > 3:
    plyr.name = line[3]

#|poke|p1|Togekiss, F
#|poke|p1|Arceus-*
def pokemon(plyr, line):
  name = line[3].split(',')[0] #remove the gender and shiny tags
  index = re.split("\W", name)[0] #use only the pokemon's name for the index, no '-', 'form' or 'type'
  pkmn = Pokemon(name)
  plyr.pokemon[index] = pkmn

#|drag|p1a: Vaporeon|Vaporeon, F|379\/463
#|switch|p1a: filthy APE|Arceus-Ghost|443\/443
def switch(plyr, line):
  name = line[3].split(',')[0]
  index = re.split("\W", name )[0]
  plyr.cur = plyr.pokemon[index]
  plyr.cur.name = name #set in the event of a form change or added typing

#|move|p1a: Lopunny|Fake Out|p2a: Umbreon
def move(plyr, line):
  if(line[3] not in plyr.cur.moves):
    plyr.cur.moves.append(line[3])

#|detailschange|p1a: i built that.|Kyogre-Primal
def transform(plyr, line):
  name = line[3]
  plyr.cur.name = name

#|-mega|p2a: steeljackal<3|Sableye|Sablenite
def megaStone(plyr, line):
  plyr.cur.item = line[4]
      
#|-enditem|p2a: Zell|Normal Gem|[from] gem|[move] Quick Attack
def enditem(plyr, line):
  plyr.cur.item = line[3]

#|-heal|p1a: Pokemon|###\/###|[from] item: Leftovers
def healitem(plyr, line):
  if len(line) > 4 and 'item' in line[4]:
    plyr.cur.item = line[4].split(':')[0].lstrip()
  
#|-damage|p1a: Foxheart|244\/271|[from] item: Life Orb
def dmgitem(plyr, line):
  if len(line) > 4 and 'item' in line[4]:
    plyr.cur.item = line[4].split(':')[0].lstrip()
  

  
  