'''
Scrapes Smogon's ban lists for each format: NU, UU, OU, Uber, Smogon
'''

import sys, os, re

# Uses beautifulsoup to scrape
from bs4 import BeautifulSoup

# Uses requests to access pages
import requests