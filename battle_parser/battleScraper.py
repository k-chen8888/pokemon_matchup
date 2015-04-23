import requests
import StringIO
from bs4 import BeautifulSoup, SoupStrainer

def battleScrape(webpage):
	r = requests.get(webpage)
	page_source = r.text

	file = open("battles.txt", 'a')

	for link in BeautifulSoup(page_source, parse_only=SoupStrainer('a')):
		if link.has_attr('href'):
				if "http://replay.pokemonshowdown.com/" in link['href']:
					if  not ("gen5" in link['href'] or "gen4" in link['href']):
						if "-ou-" in link['href'] or "-ubers-" in link['href']:
							#print link['href']
							file.write('\n'+link['href'])

	file.close()
