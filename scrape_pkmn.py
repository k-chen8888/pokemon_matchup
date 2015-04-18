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
		
		# Dictionary to store Pokemon
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
			# Abilities
			if link.has_attr('href'):
				if '/attackdex-xy/' in link['href'] and 'img' not in link.renderContents() and 'Attackdex XY' not in link.renderContents():
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
		
		# Add to list
		pokedex.append(pokemon)

	# Get each Pokemon that is a Mega-Evolution
	for i in range(1, 722):
		# Check to see if the given Pokemon has a Mega-Evolution
		if False:
			print "No Mega-Evolution for #" + i
		
		else:			
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
			
			# Dictionary to store Pokemon
			pokemon = {}
		
		
		
	# Output the finished Pokedex
	return pokedex