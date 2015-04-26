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
    self.hazards = {"Spikes":0, "Stealth Rock":0, "Sticky Web":0, "Toxic Spikes":0, "Tailwind":0, "Light Screen":0, "Reflect":0}
    self.weather = { "RainDance":0, "PrimordialSea":0, "SunnyDay":0, "DesolateLand":0, "Sandstorm":0, "Hail":0, "DeltaStream":0, "none":1}

##Class Pokemon: holds the pokemon's name, item, and moveset.
class Pokemon:
  def __init__(self, name):
    self.name = name
    self.item = None
    self.moves = []
    self.boosts = {"hp":0, "atk":0, "def":0, "spa":0, "spd":0,"spe":0, "evasion":0}
    self.unboosts = {"hp":0, "atk":0, "def":0, "spa":0, "spd":0,"spe":0, "evasion":0}
    self.status = {"brn":0, "par":0, "slp":0, "frz":0, "psn":0, "tox":0, "confusion":0, "trapped":0, "typechange":0, "Substitute":0}
    self.faint = 0
    self.form = 0
		

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
    print line
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
    if 'p1' in raw[2]:
      plyr = bat.players['p1a']
    else:
      plyr = bat.players['p2a']
    
    #use if-elif as a switch statement through the specific parse functions
    if 'move' in raw[1]:      move(plyr, raw)
    elif 'damage' in raw[1]:  dmgitem(plyr, raw)
    elif 'heal' in raw[1]:    healitem(plyr, raw)
    elif 'enditem' in raw[1]: enditem(plyr, raw)
    elif 'unboost' in raw[1]: unboost(plyr, raw)
    elif 'boost' in raw[1]:   boost(plyr, raw)
    elif 'mega' in raw[1]:    megaStone(plyr, raw)
    elif 'switch' in raw[1]:  switch(plyr, raw)
    elif 'drag' in raw[1]:    switch(plyr, raw)
    elif 'faint' in raw[1]:   fainted(plyr, raw)
    elif 'status' in raw[1]:  stus(plyr, raw)
    elif '-start' in raw[1]:  stus(plyr, raw)
    elif 'detailschange' in raw[1]:  transform(plyr, raw)
    elif 'formchange' in raw[1]:  formchange(plyr, raw)
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
  team1extra = {}
  team2 = []
  team2extra = {}
  
  #fill in team 1
  pokemon = p1.pokemon
  
  #add extra components
  team1extra['weather'] = p1.weather
  team1extra['hazards'] = p1.hazards
  
  for k in pokemon:
    poke = {}
      
    poke['name'] = nameSwap(pokemon[k].name)
     
    #Set items for Arceus and Genesect
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
    
    #extra information
    extras = {}
    extras['boosts'] = pokemon[k].boosts
    extras['unboosts'] = pokemon[k].unboosts
    extras['status'] = pokemon[k].status
    extras['fainted'] = pokemon[k].faint
    poke['extra'] = extras
    
    team1.append(deepcopy(poke))
    
  team1.append(team1extra)
    
    
  #add in extra information
  team2extra['weather'] = p2.weather
  team2extra['hazards'] = p2.hazards 
  #fill in team 2
  #used name Pikachu because why not?
  pikachu = p2.pokemon
  for k in pikachu:
    poke = {}
    poke['name'] = nameSwap(pikachu[k].name)
    
    #Set items for Arceus and Genesect
    if 'Arceus' in pikachu[k].name:
      t = pikachu[k].name.split('-')
      if len(t) > 1:
        poke['item'] = plate[t[1]]
    elif 'Genesect' in pikachu[k].name:
      t = pikachu[k].name.split('-')
      if len(t) > 1:
        poke['item'] = drive[t[1]]
    else:    
      poke['item'] = pikachu[k].item
      
    poke['moves'] = pikachu[k].moves
    
    #extra information
    extras = {}
    extras['boosts'] = pikachu[k].boosts
    extras['unboosts'] = pikachu[k].unboosts
    extras['status'] = pikachu[k].status
    extras['fainted'] = pikachu[k].faint
    
    poke['extra'] = extras
    
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

#|move|p1a: Lopunny|Fake Out|p2a: Umbreon
def move(plyr, line):
  if(line[3] not in plyr.cur.moves):
    plyr.cur.moves.append(line[3])
    
    #gather entry hazards, protect and lightscreen
    if line[3] in plyr.hazards:
      temp = plyr.hazards[line[3]]
      temp += 1
      plyr.hazards[line[3]] = temp
    
    #gather weather effects
    elif line[3] in plyr.weather:
      temp = plyr.weather[line[3]]
      temp += 1
      plyr.weather[line[3]] = temp

#|detailschange|p1a: i built that.|Kyogre-Primal
def transform(plyr, line):
  name = line[3].split(',')[0] #remove the gender and shiny tags
  if 'Kyogre' in name:    
    plyr.cur.item = primal[0]
    temp = plyr.weather["PrimordialSea"]
    temp += 1
    plyr.weather["PrimordialSea"] = temp
  elif 'Groudon' in name:
    plyr.cur.item = primal[1]
    temp = plyr.weather["DesolateLand"]
    temp += 1
    plyr.weather["DesolateLand"] = temp
    
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

#|faint|p2a: Kangaskhan
def fainted(plyr, line):
  plyr.cur.faint = 1
  
#|-status|p1a: Foxheart|slp
#|-start|p2a: Aegislash|confusion
#|-start|p1a: 420|ability: Flash Fire
def stus(plyr, line):
  if "Taunt" not in line[3] and "Heal Block" not in line[3]:
    if "Flash Fire" in line[3]:
      plyr.cur.ability = "Flash Fire"
    else:  
      t = plyr.cur.status[line[3]]
      t += 1
      plyr.cur.status[line[3]] = t #increment
  
#|-formechange|p2a: Aegislash|Aegislash-Blade
def formchange(plyr, line):
  plyr.cur.form += 1 # just increment the number of times it happened

#|-boost|p2a: Genesect-Burn|spa|1|[from] ability: Download
def boost(plyr, line):
  temp = plyr.cur.boosts[line[3]]
  temp += int(line[4])
  plyr.cur.boosts[line[3]] = temp
  #check if it is from an ability
  if len(line) > 5:
    if 'ability' in line[5]:
      plyr.cur.ability = line[5].split(':')[1].lstrip()

#|-unboost|p2a: Aegislash|spe|1
def unboost(plyr, line):
  temp = plyr.cur.unboosts[line[3]]
  temp += int(line[4])
  plyr.cur.unboosts[line[3]] = temp
  #is it from a ability
  if len(line) > 5:
    if 'ability' in line[5]:
      plyr.cur.ability = line[5].split(':')[1].lstrip()










  
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
    
#End Of File