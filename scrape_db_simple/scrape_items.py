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

# Constants from database file
from pkmn_db_simple import pkmn_types


def items(base_url = "http://serebii.net/itemdex/"):
	# Store items (in mostly alphabetical order) as a list of dictionaries
	r_itemdex = []
	
	# First, get all standard hold items
	# Access the page, take the text, and feed it to BeautifulSoup
	r = requests.get(base_url + "list/holditem.shtml")
	data = r.text
	
	for item in BeautifulSoup( data, parse_only = SoupStrainer('td') ).findAll('a'):
		new_item = {}
		try:
			new_item['name'] = str(item.getText())
			# Really??
			if new_item['name'] == 'Home' or new_item['name'] == 'Forums' or new_item['name'] == 'Contact' or new_item['name'] == 'Chat' or new_item['name'] == 'Back' or new_item['name'] == 'Forward' or new_item['name'] == 'Top':
				new_item['name'] = ""
		except:
			new_item['name'] = ""
		
		if len(new_item['name']) > 0:
			new_item['mega_stone'] = False
			new_item['fling'] = 0
			
			new_item['natural_gift_type'] = -1
			new_item['natural_gift_power'] = -1
			
			# Scrape information for each item in the list
			# For items, only need to get the Fling damage

			# Build move url from name
			condensed = new_item['name'].replace(" ", "")
			url = base_url + condensed.lower() + ".shtml"
			
			# Access the page, take the text, and feed it to BeautifulSoup
			item_r = requests.get(url)
			item_data = item_r.text
			soup = BeautifulSoup( item_data, parse_only = SoupStrainer('tr') )
			
			# Fling damage
			for f_item in soup.findAll(text=re.compile(r'^[0-9]{2}$')):
				try:
					new_item['fling'] = int(f_item)
				except:
					pass
			
			print new_item
			r_itemdex.append(new_item)
	
	# Get the Mega Stones off of the list "Evolutionary Items"
	# Access the page, take the text, and feed it to BeautifulSoup
	r = requests.get(base_url + "list/megastone.shtml")
	data = r.text
	
	for item in BeautifulSoup( data, parse_only = SoupStrainer('td') ).findAll('a'):
		new_item = {}
		try:
			new_item['name'] = str(item.getText())
			# Really??
			if new_item['name'] == 'Home' or new_item['name'] == 'Forums' or new_item['name'] == 'Contact' or new_item['name'] == 'Chat' or new_item['name'] == 'Back' or new_item['name'] == 'Forward' or new_item['name'] == 'Top':
				new_item['name'] = ""
		except:
			new_item['name'] = ""
		
		if len(new_item['name']) > 0:
			new_item['mega_stone'] = True
			new_item['fling'] = 0
			
			new_item['natural_gift_type'] = -1
			new_item['natural_gift_power'] = -1
			
			r_itemdex.append(new_item)
			print new_item
	
	# Get the berries off of the list "Berries"
	# Access the page, take the text, and feed it to BeautifulSoup
	r = requests.get(base_url + "list/berry.shtml")
	data = r.text
	
	for item in BeautifulSoup( data, parse_only = SoupStrainer('td') ).findAll('a'):
		new_item = {}
		try:
			new_item['name'] = str(item.getText())
			# Really??
			if new_item['name'] == 'Home' or new_item['name'] == 'Forums' or new_item['name'] == 'Contact' or new_item['name'] == 'Chat' or new_item['name'] == 'Back' or new_item['name'] == 'Forward' or new_item['name'] == 'Top':
				new_item['name'] = ""
		except:
			new_item['name'] = ""
		
		if len(new_item['name']) > 0:
			new_item['mega_stone'] = False
			new_item['fling'] = 10 # Constant for berries
			
			# Natural Gift
			new_item['natural_gift_type'] = 0
			new_item['natural_gift_power'] = 0
			
			# Scrape information for each item in the list
			# For berries, need to get the Fling damage, natural gift type, and natural gift damage
			
			# Build move url from name
			condensed = new_item['name'].replace(" ", "")
			url = base_url + condensed.lower() + ".shtml"
			
			# Access the page, take the text, and feed it to BeautifulSoup
			berry_r = requests.get(url)
			berry_data = berry_r.text
			soup = BeautifulSoup( berry_data, parse_only = SoupStrainer('tr') )
			
			# Get Natural Gift info
			ng = soup.find(text = re.compile(r'Natural Gift Type')).parent.parent.parent.findAll("td", { "class" : "cen" })
			
			# Natural Gift type
			for t in pkmn_types:
				try:
					if t in ng[23].find('img')['src']:
						new_item['natural_gift_type'] = pkmn_types.index(t)
				except:
					'''
					if new_item['name'] == "Kebia Berry":
						new_item['natural_gift_type'] = pkmn_types.index('poison')
					elif new_item['name'] == "Roseli Berry":
						new_item['natural_gift_type'] = pkmn_types.index('fairy')
					else:
						pass
					'''
					try:
						if t in ng[22].find('img')['src']:
							new_item['natural_gift_type'] = pkmn_types.index(t)
					except:
						pass
			
			# Natural Gift damage
			try:
				new_item['natural_gift_power'] = int(ng[24].renderContents().strip())
			except:
				try:
					new_item['natural_gift_power'] = int( ng[23].renderContents().strip() )
				except:
					pass
			
			r_itemdex.append(new_item)
			print new_item
	
	# Sort itemdex
	itemdex = sorted(r_itemdex, key=lambda k: k['name'])
	
	# Output finished itemdex
	return itemdex
