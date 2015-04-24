import requests
import StringIO
from bs4 import BeautifulSoup, SoupStrainer

def battleScrape(webpage):
	r = requests.get(webpage)
	page_source = r.text

	OU = open("OU.txt", 'a')
	UBER = open("UBERS.txt", 'a')
	OTHERS = open("OTHERS.txt", 'a')

	

	for link in BeautifulSoup(page_source, parse_only=SoupStrainer('a')):
		if link.has_attr('href'):
				if "http://replay.pokemonshowdown.com/" in link['href']:
					if  not ("gen5" in link['href'] or "gen4" in link['href'] or \
					"gen3" in link['href'] or "gen2" in link['href'] or "gen1" in link['href']):
						if "ou-" in link['href']:
							#print link['href']
							OU.write('\n'+link['href'])
						elif "ubers-" in link['href']:
							UBER.write('\n'+link['href'])
						else:
							OTHERS.write('\n'+link['href'])
	OU.close()
	UBER.close()
	OTHERS.close()
