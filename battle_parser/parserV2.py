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

#Arceus's Plates
plate = {"Bug":"Insect Plate", "Dark":"Dread Plate", "Dragon":"Draco Plate", "Electric":"Zap Plate", "Fairy":"Pixie Plate" ,"Fighting":"Fist Plate", "Fire":"Flame Plate", "Flying":"Sky Plate", "Ghost":"Spooky Plate", "Grass":"Meadow Plate", "Ground":"Earth Plate", "Ice":"Icicle Plate", "Poison":"Toxic Plate", "Psychic":"Mind Plate", "Rock":"Stone Plate", "Steel":"Iron Plate", "Water":"Splash Plate", }

#Genesect's Drives
drive = {"Shock":"Shock Drive", "Burn":"Burn Drive", "Chill":"Chill Drive", "Douse":"Douse Drive"}

#Primal Reversion Stones
primal = ["Blue Orb", "Red Orb"]
    
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
  
  #print p2.name
  #print p2.pokemon
  
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
     
    if 'Arceus' in pokemon[k].name:
      t = pokemon[k].name.split('-')
      if len(t) > 1:
        poke['item'] = plate[t[1]]
    elif 'Genesect' in pokemon[k].name:
      t = pokemon[k].name.split('-')
      if len(t) > 1:
        poke['item'] = drive[t[1]]
    else:    
      poke['item'] = pokemon[k].item
    
    poke['moves'] = pokemon[k].moves
    team1.append(deepcopy(poke))

  #fill in team 2
  #used name Pikachu because why not?
  pikachu = p2.pokemon
  for k in pikachu:
    poke = {}
    poke['name'] = pikachu[k].name
    poke['item'] = pikachu[k].item
    poke['moves'] = pikachu[k].moves
    team2.append(deepcopy(poke))
  
  #print team2
 
  #Craft the Dictionary
  battleDic = {'team1' : team1, 'team2' : team2, 'winner' : victor}
#  print battleDic
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
  if 'Arceus' in name:
    type = name.split('-')
    if len(type) > 1:
      plyr.cur.item = plate[type[1]]

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
    plyr.cur.item = line[4].split(':')[1].lstrip()
  
#|-damage|p1a: Foxheart|244\/271|[from] item: Life Orb
def dmgitem(plyr, line):
  if len(line) > 4 and 'item' in line[4]:
    plyr.cur.item = line[4].split(':')[1].lstrip()
  
#if the name has a -SOMETHING at the end. Move it to the front
#if it is Keldo or Meloetta, just return their base name  
def nameSwap(name):
  parts = name.split('-')
  if len(parts) < 2:
    return name
    
  #move the mega to the front
  elif 'Mega' in parts[1]:
    #Charizard and Mewtwo
    if len(parts) > 2: 
      return parts[1] + ' ' + parts[2] + ' ' + parts[0]
    else:
      return parts[1] + ' ' + parts[0]  
  
  #Groudon and Kyogre
  elif 'Primal' in parts[1]:
    return parts[1] + ' ' + parts[0]
  
    #Pokemon Specific Cases
  elif 'Nidoran' in parts[0]:
    return name
  elif 'Porygon' in parts[0]:
    return name
  elif 'Castform' in parts[0]:
    return parts[0] + ' ' + parts[1] + ' ' + 'Form'
  elif 'Deoxys' in parts[0]:
    return parts[0] + ' ' + parts[1] + ' ' + 'Form'
  
  #Gen IV Exceptions 
  elif 'Rotom' in parts[0]:
    return parts[1] + ' ' + parts[0]
  elif 'Giratina' in parts[0]:
    return parts[0] + ' ' + parts[1]
  elif 'Shaymin' in parts[0]:
    return parts[0] + ' ' + parts[1] + 'Form'
  elif 'Arceus' in parts[0]:
    return parts[0]
  
  #Gen V Exceptions
  elif 'Darmanitan' in parts[0]:
    return parts[1] + ' ' + parts[0]
  elif 'Therian' in parts[1]:
    return parts[0] + ' ' + parts[1] + ' ' + 'Form'
  elif 'Keldeo' in parts[0]:
    return parts[0]
  elif 'Kyurem' in parts[0]:
    return parts[1] + ' ' + parts[0]
  elif 'Meloetta' in parts[0] :
    print 'Using: ' + name
    return parts[0]
  elif 'Genesect' in parts[0]:
    return parts[0]
  
  #Gen VI Exceptions
  elif 'Floette' in parts[0]:
    return parts[0]
  elif 'Meowstic' in parts[0]:
    return parts[0] + ' ' + parts[1]
  elif 'Aegislash' in parts[0]:
    return parts[0] + ' ' + parts[1] + ' ' + 'Form'
  elif 'Pumpkaboo' in parts[0]:
    return parts[0] + ' ' + parts[1]
  elif 'Gourgeist' in parts[0]:
    return parts[0] + ' ' + parts[1]