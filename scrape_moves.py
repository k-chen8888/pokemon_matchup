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
		Special parameters for Other
			Weather
			Entry hazards
			Status effect (confuse, paralyze, etc.)
			Healing
			Buffing/Weakening stats
	Accuracy
	Priority
'''

import sys, os, re

# Uses beautifulsoup to scrape
from bs4 import BeautifulSoup, SoupStrainer

# Uses requests to access pages
import requests

# Need the pkmn_types constant from the database
from pkmn_db_simple import pkmn_types, move_cats, other


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

				# Special conditions for 'Other'
				if move['move_cat'] == 2:
					move['weather'] = False
					move['entry'] = False
					move['status'] = False
					move['heal'] = False
					move['stat_change'] = False
					
					# Weather
					for x in other['weather']:
						if soup.findAll(text = re.compile(x)):
							move['weather'] = True
						else:
							pass
					
					# Entry hazard
					for x in other['entry']:
						if soup.findAll(text = re.compile(x)):
							move['entry'] = True
						else:
							pass
					
					# Status effect
					for x in other['status']:
						if soup.findAll(text = re.compile(x)):
							move['status'] = True
						else:
							pass
					
					# Healing
					for x in other['heal']:
						if soup.findAll(text = re.compile(x)):
							move['heal'] = True
						else:
							pass
					
					# Buff/weaken
					for x in other['stat_change']:
						if soup.findAll(text = re.compile(x)):
							move['stat_change'] = True
						else:
							pass
			
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
	
	# Oops
	hail = {}
	hail['name'] = 'Hail'
	hail['move_type'] = pkmn_types.index('ice')
	hail['move_cat'] = 2
	hail['priority'] = 0
	hail['accuracy'] = 0
	hail['weather'] = True
	hail['entry'] = True
	hail['status'] = False
	hail['heal'] = False
	hail['stat_change'] = False
	# Append Hail
	movedex.append(hail)
	
	# Output finished movedex
	return movedex
