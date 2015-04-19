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

import sys, os, re

# Uses beautifulsoup to scrape
from bs4 import BeautifulSoup, SoupStrainer

# Uses requests to access pages
import requests


def pkmn(base_url = "http://serebii.net/pokedex-xy/"):
	# Store the pokedex as a list of dictionaries
	pokedex = []
	
	# Get each Pokemon
	for i in range(1, 722):
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
		# Types
		typelist = soup.find("td", { "class" : "cen" })
		count = 1
		for child in typelist.findAll("img"):
			typen = "type" + str(count)
			pokemon[typen] = str(child)[38:-7]
			count += 1
		# Moves and abilities
		pokemon['abilities'] = []
		pokemon['moves'] = []
		for link in BeautifulSoup( data, parse_only = SoupStrainer('a') ).findAll('a'):
			# Moves
			if link.has_attr('href'):
				move = link.renderContents()
				if '/attackdex-xy/' in link['href'] and 'img' not in move and 'Attackdex XY' not in move and move not in pokemon['moves']:
					pokemon['moves'].append( link.renderContents() )
			# Abilities
			if link.has_attr('href'):
				if '/abilitydex/' in link['href'] and len(link['href']) > 12:
					for child in link.children:
						if child.renderContents() not in pokemon['abilities']:
							pokemon['abilities'].append( child.renderContents() )
		# Stats
		pokemon['base'] = []
		for x in soup.find(text = re.compile(r'Base Stats')).parent.parent.parent.findAll("tr")[2].findAll('td'):
			try:
				pokemon['base'].append( int(x.renderContents()) )
			except:
				print "Not an actual stat"
		
		# Add another entry if this Pokemon has a Mega-Evolution
		if soup.findAll(text = re.compile(r'Mega Evolution X$') ):
			# print "mega X & Y"
			# X Mega Evolution
			pokemon_x = {}
			pokemon_x['name'] = "Mega " + pokemon['name'] + " X"
			pokemon_x['id'] = pokemon['id']
			
			pokemon_x['moves'] = pokemon['moves']
			
			# Types may change
			typelist_x = soup.find(text = re.compile(r'Mega Evolution X$') ).parent.parent.parent.parent.parent.find("td", { "class" : "cen" })
			count = 1
			for child in typelist_x.findAll("img"):
				typen = "type" + str(count)
				pokemon_x[typen] = str(child)[38:-7]
				count += 1
			
			# Abilities may change
			pokemon_x['abilities'] = [ pokemon['abilities'].pop(-2) ]
			
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
			
			pokemon_y['moves'] = pokemon['moves']
						
			# Types may change
			typelist_y = soup.find(text = re.compile(r'Mega Evolution Y$') ).parent.parent.parent.parent.parent.find("td", { "class" : "cen" })
			count = 1
			for child in typelist_y.findAll("img"):
				typen = "type" + str(count)
				pokemon_y[typen] = str(child)[38:-7]
				count += 1
			
			# Abilities may change
			pokemon_y['abilities'] = [pokemon['abilities'].pop()]
			
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
			
		elif soup.findAll(text = re.compile(r'Mega Evolution$') ):
			pokemon_mega = {}
			pokemon_mega['name'] = "Mega " + pokemon['name']
			pokemon_mega['id'] = pokemon['id']
			
			pokemon_mega['moves'] = pokemon['moves']
			
			# Types may change
			
			
			# Abilities may change
			pokemon_mega['abilities'] = [pokemon['abilities'].pop()]
			
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
		
		# Manually input primal reversion, since there are only 2
		elif pokemon['id'] == 382: # Kyogre
			pokemon_primal = {}
			pokemon_primal['name'] = "Primal Kyogre"
			pokemon_primal['id'] = pokemon['id']
			
			pokemon_primal['moves'] = pokemon['moves']
			
			pokemon_primal['type1'] = pokemon['type1']
			
			pokemon_primal['abilities'] = [pokemon['abilities'].pop()]
			
			pokemon_primal['base'] = [100, 100, 90, 150, 140, 90]
			
			print pokemon_primal
			# Add to list
			pokedex.append(pokemon_primal)
		
		elif pokemon['id'] == 383: # Groudon
			pokemon_primal = {}
			pokemon_primal['name'] = "Primal Groudon"
			pokemon_primal['id'] = pokemon['id']
			
			pokemon_primal['moves'] = pokemon['moves']
			
			pokemon_primal['type1'] = pokemon['type1']
			pokemon_primal['type2'] = 'fire'
			
			pokemon_primal['abilities'] = [pokemon['abilities'].pop()]
			
			pokemon_primal['base'] = [100, 180, 160, 150, 90, 90]
			
			print pokemon_primal
			# Add to list
			pokedex.append(pokemon_primal)
			
		else:
			pass
		
		print pokemon
		# Add original to list
		pokedex.append(pokemon)
		
	# Output the finished Pokedex
	return pokedex