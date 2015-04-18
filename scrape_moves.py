'''
Scrapes all Pokemon moves out of Serebii.net's movedex
	Scrape all move names from the dropdown first

URL structure is: http://serebii.net/attackdex-xy/<move_name>.shtml
	Move name is condensed and all lowercase
		Example: Absorb = absorb
		Example: Hydro Pump = hydropump

Information to get:
	Name
	PP
	Base power
	Type
	Physical, Special, Other
'''

import sys, os, re

# Uses beautifulsoup to scrape
from bs4 import BeautifulSoup, SoupStrainer

# Uses requests to access pages
import requests


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
		
		# Get type of move
		
		# Get category of move
		
		# Get speed priority
	
	
	
	# Output finished movedex
	return movedex