'''
Scrapes all Pokemon moves out of Serebii.net's movedex
	Scrape all move names from the dropdown first

URL structure is: http://serebii.net/attackdex-xy/<move_name>.shtml
	Move name is condensed and all lowercase
		Example: Absorb = absorb
		Example: Hydro Pump = hydropump

Information to get:
	Name
	Base power
	Type
	Physical, Special, Other
	Accuracy
	Priority
'''

import sys, os, re

# Uses beautifulsoup to scrape
from bs4 import BeautifulSoup, SoupStrainer

# Uses requests to access pages
import requests

# Need the pkmn_types constant from the database
from pkmn_db_simple import pkmn_types, move_cats


def moves(base_url = "http://serebii.net/attackdex-xy/"):
	# Store moves (in alphabetical order) as a list of dictionaries
	movedex = []
	
	# Access the page, take the text, and feed it to BeautifulSoup
	r = requests.get(base_url)
	data = r.text
	soup = BeautifulSoup(data)
	soup.prettify()
	
	# First step is to get all the options
	for option in soup.findAll("option"):
		move = {}
		if "AttackDex:" not in option.renderContents() and '(Col)' not in option.renderContents() and 'XD' not in option.renderContents():
			try:
				move['name'] = option.renderContents()[0:option.renderContents().index("<option")].strip()
			except:
				move['name'] = option.renderContents().strip()
		# Dump moves into list, ignore empty dictionaries
		if bool(move):
			movedex.append(move)
	
	# Scrape information for each move in the list
	for move in movedex:
		# Build move url from name
		condensed = move['name'].replace(" ", "")
		url = base_url + condensed.lower() + ".shtml"
		
		# Access the page, take the text, and feed it to BeautifulSoup
		move_r = requests.get(url)
		move_data = move_r.text
		move_soup = BeautifulSoup(move_data)
		move_soup.prettify()
		
		i = 0
		priority_loc = -1
		for child in move_soup.find('table', {'class', 'dextable'} ).findChildren():
			
			# Get type of move
			if i == 11:
				# print "Type", child.find("img")["src"]
				for t in pkmn_types:
					if t.lower() in child.find("img")["src"] :
						move['move_type'] = pkmn_types.index(t)
			
			if i == 25:
				# print "Base Power", child.getText().strip()
				move['base_power'] = int( child.getText().strip() )
			
			# Get category of move
			if i == 15:
				# print "Category", child["src"]
				for cat in move_cats:
					if cat in child["src"]:
						move['move_cat'] = move_cats.index(cat)
			
			# Get accuracy rating; 0 = never misses
			if i == 26:
				# print "Accuracy", child.getText().strip()
				move['accuracy'] = int( child.getText().strip() )
			
			if child.getText() == "Speed Priority":
				priority_loc = i + 5
			
			# Get speed priority
			if i == priority_loc:
				try:
					# print "Priority", child.getText().strip()
					move['priority'] = int( child.getText().strip() )
				except:
					priority_loc += 1
			
			i += 1
			
			# Oops
			if move['name'] == 'Camouflage':
				move['priority'] = 0
			
		print move
		
	# Output finished movedex
	return movedex