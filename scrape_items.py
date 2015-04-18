'''
Scrapes all held items out of Serebii.net's itemdex
	Scrape all item names from the dropdowns first, but only take from the following lists:
		Hold Item
		Evolutionary item (subcategory Mega Stones)
		Berries

URL structure is: http://serebii.net/attackdex-xy/<item_name>.shtml
	Move name is condensed and all lowercase
		Example: Absolite = absolite
		Example: Chesto Berry = chestoberry

Information to get:
	Name
	Mega Stone (Y/N) (all Mega Stones have suffix -ite, except Red Orb and Blue Orb)
'''

import sys, os, re

# Uses beautifulsoup to scrape
from bs4 import BeautifulSoup, SoupStrainer

# Uses requests to access pages
import requests


def items(base_url = "http://serebii.net/itemdex/"):
	# Store items (in mostly alphabetical order) as a list of dictionaries
	r_itemdex = []
	
	# First, get all standard hold items
	# Access the page, take the text, and feed it to BeautifulSoup
	r = requests.get(base_url + "list/holditem.shtml")
	data = r.text
	
	for item in BeautifulSoup( data, parse_only = SoupStrainer('tr') ).findAll('a'):
		new_item = {}
		try:
			new_item['name'] = str(item.getText())
		except:
			new_item['name'] = ""
		
		if len(new_item['name']) > 0:
			new_item['mega_stone'] = False
			new_item['fling'] = 0
			r_itemdex.append(new_item)
	
	# Scrape information for each item in the list
	# For items, only need to get the Fling damage
	for item in r_itemdex:
		# Build move url from name
		condensed = item['name'].replace(" ", "")
		url = base_url + condensed.lower() + ".shtml"
		
		# Access the page, take the text, and feed it to BeautifulSoup
		item_r = requests.get(url)
		item_data = item_r.text
		soup = BeautifulSoup( item_data, parse_only = SoupStrainer('tr') )
		
		# Fling damage
		for f_item in soup(text=re.compile(r'^[0-9]{2}$')):
			try:
				item['fling'] = int(f_item)
			except:
				pass
	
	# Get the Mega Stones off of the list "Evolutionary Items"
	# Access the page, take the text, and feed it to BeautifulSoup
	r = requests.get(base_url + "list/megastone.shtml")
	data = r.text
	
	for item in BeautifulSoup( data, parse_only = SoupStrainer('tr') ).findAll('a'):
		new_item = {}
		try:
			new_item['name'] = str(item.getText())
		except:
			new_item['name'] = ""
		
		if len(new_item['name']) > 0:
			new_item['mega_stone'] = True
			new_item['fling'] = 0
			r_itemdex.append(new_item)
	
	# Sort itemdex
	itemdex = sorted(r_itemdex, key=lambda k: k['name'])
	
	# Output finished itemdex
	return itemdex