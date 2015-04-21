'''
The main scraper file

Scrape in this order:
	Hold Items (serebii)
	Moves (serebii)
	Abilities (serebii)
	Pokemon (serebii)
	Ban lists (smogon)
'''

import sys, os

# Uses beautifulsoup to scrape
from bs4 import BeautifulSoup

# Uses requests to access pages
import requests

# Database used to store everything
from pkmn_db import *

# Import all scraping modules in other files
from scrape_items import *
from scrape_moves import *
from scrape_abilities import *
from scrape_pkmn import *
from scrape_bans import *