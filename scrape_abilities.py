'''
Scrapes all Pokemon abilities out of Serebii.net's abilitydex
	Scrape all ability names from the dropdowns first

URL structure is: http://serebii.net/attackdex-xy/<ability_name>.shtml
	Move name is condensed and all lowercase
		Example: Adaptability = adaptability
		Example: Air Lock = airlock
'''

import sys, os, re

# Uses beautifulsoup to scrape
from bs4 import BeautifulSoup, SoupStrainer

# Uses requests to access pages
import requests


def abilities(base_url = "http://serebii.net/abilitydex/"):
	# Store abilities (in alphabetical order) as a list of dictionaries
	abilitydex = []
	
	# Access the page, take the text, and feed it to BeautifulSoup
	r = requests.get(base_url)
	data = r.text
	soup = BeautifulSoup(data)
	soup.prettify()
	
	# Get all the options
	# Only need names for abilities
	for option in soup.findAll("option"):
		ability = {}
		if "AbilityDex:" not in option.renderContents() and '(Col)' not in option.renderContents() and 'XD' not in option.renderContents():
			try:
				ability['name'] = option.renderContents()[0:option.renderContents().index("<option")].strip()
			except:
				ability['name'] = option.renderContents().strip()
		# Dump abilities into list, ignore empty dictionaries
		if bool(ability):
			abilitydex.append(ability)
			print ability
	
	# Output finished abilitydex
	return abilitydex
