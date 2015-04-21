'''
Scrapes Pokemon out of Serebii.net's online Pokedex

URL structure: http://serebii.net/pokedex-xy/<dex_entry_number>.shtml
	Dex goes from 001-721

Get the following information:
	Name
	Type(s)
	Base stats (Normal and Mega, if applicable)
	Ability pool (Name only)
	Move pool (Name only)
'''

import sys, os, re, copy

# Uses beautifulsoup to scrape
from bs4 import BeautifulSoup, SoupStrainer

# Uses requests to access pages
import requests


def pkmn(base_url = "http://serebii.net/pokedex-xy/"):
	# Store the pokedex as a list of dictionaries
	pokedex = []
	
	# Get each Pokemon (there are 721, but Hoopa and Volcanion are not yet released)
	for i in range(1, 720):
		page = str(i)
		
		# Fix the length of the page
		while len(page) < 3:
			page = "0" + page
		
		# Fix formatting of page
		page = base_url + page + ".shtml"
		
		# Access the page, take the text, and feed it to BeautifulSoup
		r = requests.get(page)
		data = r.text
		soup = BeautifulSoup(data)
		soup.prettify()
		
		# Dictionary to store Pokemon data
		pokemon = {}
		
		# Get all the data
		summary = soup.findAll("td", { "class" : "fooinfo" })
		# ID
		pokemon['id'] = i
		# Name
		pokemon['name'] = summary[1].renderContents().strip()
		if i == 29: # Nidoran-F
			pokemon['name'] = "Nidoran-F"
		elif i == 32:
			pokemon['name'] = "Nidoran-M"
		else:
			pass
		pokemon['mega'] = False
		# Types
		pokemon['type'] = []
		typelist = soup.find("td", { "class" : "cen" })
		for child in typelist.findAll("img"):
			pokemon['type'].append( str(child)[38:-7] )
		# Moves and abilities
		pokemon['abilities'] = []
		pokemon['moves'] = []
		for link in BeautifulSoup( data, parse_only = SoupStrainer('a') ).findAll('a'):
			# Moves
			if link.has_attr('href'):
				move = link.renderContents().strip()

				if '/attackdex-xy/' in link['href'] and 'img' not in move and 'Attackdex XY' not in move and move not in pokemon['moves']:
					# Handle some really weird parsing exceptions
					tags = re.compile(r'<.*?>')
					if '<br/>' in move:
						move = move[0:move.index('<br/>')]
					move = tags.sub('', move)
					
					# Fix dash capitalization
					# Get list of dash locations
					locs = [ i.start() for i in re.finditer('-', move) ]
					fixcase = ""
					current = 0
					for l in locs:
						fixcase += move[current:l+1] + move[l+1].upper()
						current = l + 2
					fixcase += move[current:len(move)]
					# Special name exceptions
					if fixcase == "Trick-Or-Treat":
						fixcase = "Trick-or-Treat"
					elif fixcase == "U-Turn":
						fixcase = "U-turn"
					elif fixcase == "V-Create":
						fixcase = "V-create"
					else:
						pass
					
					if len(move) > 0 or len(fixcase) > 0:
						pokemon['moves'].append( fixcase )
			# Abilities
			if link.has_attr('href'):
				if '/abilitydex/' in link['href'] and len(link['href']) > 12:
					for child in link.children:
						try:
							if child.renderContents().strip() not in pokemon['abilities']:
								pokemon['abilities'].append( child.renderContents().strip() )
						except:
							pass
		# Stats
		pokemon['base'] = []
		for x in soup.find(text = re.compile(r'Base Stats')).parent.parent.parent.findAll("tr")[2].findAll('td'):
			try:
				pokemon['base'].append( int(x.renderContents()) )
			except:
				print "Not an actual stat"
		
		# Certain special exceptions for certain Pokemon, by id value
		if pokemon['id'] == 351: # Castform
			sunny = copy.deepcopy(pokemon)
			sunny['name'] = pokemon['name'] + " Sunny Form"
			sunny['type'] = ['fire']
			# Add sunny form
			pokedex.append(sunny)
			
			rainy = copy.deepcopy(pokemon)
			rainy['name'] = pokemon['name'] + " Rainy Form"
			rainy['type'] = ['water']
			# Add rainy form
			pokedex.append(rainy)
			
			snowy = copy.deepcopy(pokemon)
			snowy['name'] = pokemon['name'] + " Snowy Form"
			snowy['type'] = ['ice']
			# Add snowy form
			pokedex.append(snowy)
		
		elif pokemon['id'] == 386: # Deoxys
			pokemon['base'] = [50, 150, 50, 150, 50, 150]
			
			attack = copy.deepcopy(pokemon)
			attack['name'] = pokemon['name'] + " Attack Form"
			attack['base'] = [50, 180, 20, 180, 20, 150]
			# Add attack form
			pokedex.append(attack)
			
			defense = copy.deepcopy(pokemon)
			defense['name'] = pokemon['name'] + " Defense Form"
			defense['base'] = [50, 180, 20, 180, 20, 150]
			# Add defense form
			pokedex.append(defense)
			
			speed = copy.deepcopy(pokemon)
			speed['name'] = pokemon['name'] + " Speed Form"
			speed['base'] = [50, 180, 20, 180, 20, 150]
			# Add speed form
			pokedex.append(speed)
		
		elif pokemon['id'] == 479: # Rotom
			# Exclusive elemental moves
			elem_moves = ['Blizzard', 'Overheat', 'Leaf Storm', 'Air Slash', 'Hydro Pump']
			for e in elem_moves:
				pokemon['moves'].remove(e)
			
			# New base stats
			new_base = [50, 65, 107, 105, 107, 86]
			
			frost = copy.deepcopy(pokemon)
			frost['name'] = "Frost " + pokemon['name']
			frost['type'][1] = 'ice'
			frost['moves'].append( elem_moves[0] )
			frost['base'] = new_base
			# Add Frost form
			pokedex.append(frost)
			
			heat = copy.deepcopy(pokemon)
			heat['name'] = "Heat " + pokemon['name']
			heat['type'][1] = 'fire'
			heat['moves'].append( elem_moves[1] )
			heat['base'] = new_base
			# Add Heat form
			pokedex.append(heat)
			
			mow = copy.deepcopy(pokemon)
			mow['name'] = "Mow " + pokemon['name']
			mow['type'][1] = 'grass'
			mow['moves'].append( elem_moves[2] )
			mow['base'] = new_base
			# Add Mow form
			pokedex.append(mow)
			
			fan = copy.deepcopy(pokemon)
			fan['name'] = "Fan " + pokemon['name']
			fan['type'][1] = 'flying'
			fan['moves'].append( elem_moves[3] )
			fan['base'] = new_base
			# Add Fan form
			pokedex.append(fan)
			
			wash = copy.deepcopy(pokemon)
			wash['name'] = "Wash " + pokemon['name']
			wash['type'][1] = 'water'
			wash['moves'].append( elem_moves[4] )
			wash['base'] = new_base
			# Add Wash form
			pokedex.append(wash)
		
		elif pokemon['id'] == 487: # Giratina
			print "hi"
			origin = copy.deepcopy(pokemon)
			origin['name'] = pokemon['name'] + " Origin Form"
			origin['base'] = [150, 120, 100, 120, 100, 90]
			# Add Origin Form
			pokedex.append(origin)
		
		elif pokemon['id'] == 555: # Darmanitan
			zen = copy.deepcopy(pokemon)
			zen['name'] = "Zen " + pokemon['name']
			zen['type'].append( 'psychic' )
			zen['base'] = [105, 30, 105, 140, 105, 55]
			# Add Zen mode
			pokedex.append(zen)
		
		elif pokemon['id'] == 641: # Tornadus
			# Remove exclusive ability
			pokemon['abilities'].remove("Regenerator")
			
			therian_641 = copy.deepcopy(pokemon)
			therian_641['name'] = pokemon['name'] + "Therian Form"
			therian_641['base'] = [79, 100, 80, 110, 90, 121]
			therian_641['abilities'] = ["Regenerator"]
			# Add Therian Form
			pokedex.append(therian_641)
		
		elif pokemon['id'] == 642: # Thundurus
			# Remove exclusive ability
			pokemon['abilities'].remove("Volt Absorb")
			
			therian_642 = copy.deepcopy(pokemon)
			therian_642['name'] = pokemon['name'] + "Therian Form"
			therian_642['base'] = [79, 105, 70, 145, 80, 101]
			therian_642['abilities'] = ["Volt Absorb"]
			# Add Therian Form
			pokedex.append(therian_642)
		
		elif pokemon['id'] == 645: # Landorus
			# Remove exclusive ability
			pokemon['abilities'].remove("Intimidate")
			
			therian_645 = copy.deepcopy(pokemon)
			therian_645['name'] = pokemon['name'] + "Therian Form"
			therian_645['base'] = [89, 145, 90, 105, 80, 91]
			therian_645['abilities'] = ["Intimidate"]
			# Add Therian Form
			pokedex.append(therian_645)
		
		elif pokemon['id'] == 646: # Kyurem
			# Remove exclusive abilities
			pokemon['abilities'].remove("Teravolt")
			pokemon['abilities'].remove("Turboblaze")
			
			# Sort moves by the version that has them
			plain_moves = ["Scary Face", "Glaciate"]
			black_moves = ["Fusion Flare", "Ice Burn"]
			for bm in black_moves:
				pokemon['moves'].remove(bm)
			white_moves = ["Fusion Bolt", "Freeze Shock"]
			for wm in white_moves:
				pokemon['moves'].remove(wm)
			
			black = copy.deepcopy(pokemon)
			black['name'] = "Black " + pokemon['name']
			black['abilities'] = ["Teravolt"]
			black['base'] = [125, 170, 100, 120, 90, 95]
			for pm in plain_moves:
				black['moves'].remove(pm)
			for bm in black_moves:
				black['moves'].append(bm)
			# Add black form
			pokedex.append(black)
			
			white = copy.deepcopy(pokemon)
			white['name'] = "White " + pokemon['name']
			white['abilities'] = ["Turboblaze"]
			white['base'] = [125, 120, 90, 170, 100, 95]
			for pm in plain_moves:
				white['moves'].remove(pm)
			for wm in white_moves:
				white['moves'].append(wm)
			# Add white form
			pokedex.append(white)
		
		elif pokemon['id'] == 669: # Flabebe
			pokemon['name'] = "Flabebe"
		
		elif pokemon['id'] == 678: # Meowstic
			# Remove female's abilities and moves
			female_moves = ["Stored Power", "Me First", "Magical Leaf", "Extrasensory", "Future Sight"]
			for fm in female_moves:
				pokemon['moves'].remove(fm)
			pokemon['abilities'].remove("Competitive")
			
			female = copy.deepcopy(pokemon)
			female['name'] = pokemon['name'] + " F"
			for fm in female_moves:
				female['moves'].append(fm)
			female['abilities'].remove("Prankster")
			female['abilities'].append("Competitive")
			# Add female version
			pokedex.append(female)
		
		elif pokemon['id'] == 681: # Aegislash
			blade = copy.deepcopy(pokemon)
			blade['name'] = pokemon['name'] + " Blade Form"
			blade['base'] = [60, 150, 50, 150, 50, 60]
			# Add Blade Form
			pokedex.append(blade)
		
		else:
			pass
		
		# Add another entry if this Pokemon has a Mega-Evolution
		if soup.findAll(text = re.compile(r'Mega Evolution X$') ):
			# print "mega X & Y"
			# X Mega Evolution
			pokemon_x = {}
			pokemon_x['name'] = "Mega " + pokemon['name'] + " X"
			pokemon_x['id'] = pokemon['id']
			pokemon_x['mega'] = True
			
			pokemon_x['moves'] = pokemon['moves']
			
			# Types may change
			pokemon_x['type'] = []
			typelist_x = soup.find(text = re.compile(r'Mega Evolution X$') ).parent.parent.parent.parent.parent.find("td", { "class" : "cen" })
			for child in typelist_x.findAll("img"):
				pokemon_x['type'].append( str(child)[38:-7] )
			
			# Abilities may change
			if len(pokemon['abilities']) > 1:
				pokemon_x['abilities'] = [pokemon['abilities'].pop()]
			else:
				pokemon_x['abilities'] = copy.deepcopy( pokemon['abilities'] )
			
			# Stats may change
			pokemon_x['base'] = []
			for x in soup.findAll(text = re.compile(r'Base Stats'))[1].parent.parent.parent.findAll("tr")[2].findAll('td'):
				try:
					pokemon_x['base'].append( int(x.renderContents()) )
				except:
					print "Not an actual stat"
			
			print pokemon_x
			# Add to list
			pokedex.append(pokemon_x)
			
			##########
			
			# Y Mega Evolution
			pokemon_y = {}
			pokemon_y['name'] = "Mega " + pokemon['name'] + " Y"
			pokemon_y['id'] = pokemon['id']
			pokemon_y['mega'] =  True
			
			pokemon_y['moves'] = pokemon['moves']
						
			# Types may change
			pokemon_y['type'] = []
			typelist_y = soup.find(text = re.compile(r'Mega Evolution Y$') ).parent.parent.parent.parent.parent.find("td", { "class" : "cen" })
			for child in typelist_y.findAll("img"):
				pokemon_y['type'].append( str(child)[38:-7] )
			
			# Abilities may change
			if len(pokemon['abilities']) > 1:
				pokemon_y['abilities'] = [pokemon['abilities'].pop()]
			else:
				pokemon_y['abilities'] = copy.deepcopy( pokemon['abilities'] )
			
			# Stats may change
			pokemon_y['base'] = []
			for x in soup.findAll(text = re.compile(r'Base Stats'))[2].parent.parent.parent.findAll("tr")[2].findAll('td'):
				try:
					pokemon_y['base'].append( int(x.renderContents()) )
				except:
					print "Not an actual stat"
			
			print pokemon_y
			# Add to list
			pokedex.append(pokemon_y)
		
		# Manually input primal reversion, since there are only 2
		elif pokemon['id'] == 382: # Kyogre
			pokemon_primal = {}
			pokemon_primal['name'] = "Primal Kyogre"
			pokemon_primal['id'] = pokemon['id']
			# You can have a primal and a mega on the same team
			pokemon_primal['mega'] = False
			
			pokemon_primal['moves'] = copy.deepcopy( pokemon['moves'] )
			
			pokemon_primal['type'] = copy.deepcopy( pokemon['type'] )
			
			pokemon_primal['abilities'] = [pokemon['abilities'].pop()]
			
			pokemon_primal['base'] = [100, 100, 90, 150, 140, 90]
			
			print pokemon_primal
			# Add to list
			pokedex.append(pokemon_primal)
		
		elif pokemon['id'] == 383: # Groudon
			pokemon_primal = {}
			pokemon_primal['name'] = "Primal Groudon"
			pokemon_primal['id'] = pokemon['id']
			# You can have a primal and a mega on the same team
			pokemon_primal['mega'] = False
			
			pokemon_primal['moves'] = copy.deepcopy( pokemon['moves'] )
			
			pokemon_primal['type'] = copy.deepcopy( pokemon['type'] )
			pokemon_primal['type'].append( 'fire' )
			
			pokemon_primal['abilities'] = [pokemon['abilities'].pop()]
			
			pokemon_primal['base'] = [100, 180, 160, 150, 90, 90]
			
			print pokemon_primal
			# Add to list
			pokedex.append(pokemon_primal)
		
		elif soup.findAll(text = re.compile(r'Mega Evolution$') ):
			pokemon_mega = {}
			pokemon_mega['name'] = "Mega " + pokemon['name']
			pokemon_mega['id'] = pokemon['id']
			pokemon_mega['mega'] = True
			
			pokemon_mega['moves'] = pokemon['moves']
			
			# Types may change
			pokemon_mega['type'] = []
			typelist_mega = soup.find(text = re.compile(r'Mega Evolution$') ).parent.parent.parent.parent.parent.find("td", { "class" : "cen" })
			for child in typelist_mega.findAll("img"):
				pokemon_mega['type'].append( str(child)[38:-7] )
			
			# Abilities may change
			if len(pokemon['abilities']) > 1:
				pokemon_mega['abilities'] = [pokemon['abilities'].pop()]
			else:
				pokemon_mega['abilities'] = copy.deepcopy( pokemon['abilities'] )
			
			# Stats may change
			pokemon_mega['base'] = []
			for x in soup.findAll(text = re.compile(r'Base Stats'))[1].parent.parent.parent.findAll("tr")[2].findAll('td'):
				try:
					pokemon_mega['base'].append( int(x.renderContents()) )
				except:
					print "Not an actual stat"
			
			print pokemon_mega
			# Add to list
			pokedex.append(pokemon_mega)
		
		else:
			pass
		
		print pokemon
		# Add original to list
		pokedex.append(pokemon)
		
	# Output the finished Pokedex
	return pokedex