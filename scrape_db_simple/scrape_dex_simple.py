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
# Use the simple version
from pkmn_db_simple import *


# Import all scraping modules in other files
# The simple version assumes legality
from scrape_items import *
from scrape_moves import *
from scrape_abilities import *
from scrape_pkmn import *


'''
Call all of the scrapers and get to work
'''
def scrape_dex():
	# Load all documented information, scraping from serebii.net
	#d_items = items()
	#d_moves = moves()
	#d_abilities = abilities()
	d_pkmn = pkmn()
	
	'''
	Load database
	'''
	
	# Need to start up a database session first
	from sqlalchemy.orm import sessionmaker
	from sqlalchemy import create_engine
	
	Session = sessionmaker()
	engine = create_engine('sqlite:///pkmn_db_simple.db', echo = True)
	Session.configure(bind=engine)
	
	# Work with this one
	s = Session()
	
	# For each item, make a new HoldItem and commit to database
	# Only add if it doesn't exist
	for i in d_items:
		if not s.query(exists().where(HoldItem.name == i['name'])).scalar():
			new_item = HoldItem(i)
			s.add(new_item)
		s.commit()
	
	# For each move, make a new Move and commit to database
	# Only add if it doesn't exist
	for m in d_moves:
		if not s.query(exists().where(Move.name == m['name'])).scalar():
			new_move = Move(m)
			s.add(new_move)
		s.commit()
	
	# For each ability, make a new Ability and commit to database
	# Only add if it doesn't exist
	for a in d_abilities:
		if not s.query(exists().where(Ability.name == a['name'])).scalar():
			new_ability = Ability(a)
			s.add(new_ability)
		s.commit()
	
	# For each Pokemon, make a new Pokemon and commit to database
	# Only add if it doesn't exist
	# Set up relationship between (moves, abilities) and the Pokemon that can possibly have them
	#	Again, only add an entry if it doesn't exist
	for p in d_pkmn:
		if not s.query(exists().where(Pokemon.name == p['name'])).scalar():
			new_pkmn = Pokemon(p)
			
			# Moves
			for m in p['moves']:
				# Pull the Move object to add out of database
				link_move = s.query(Move).filter_by(name = m).first()
				# Actually add the move to the list of possible moves
				new_pkmn.possible_moves.append(link_move)
				
			# Abilities
			for a in p['abilities']:
				# Pull the Ability object to add out of database
				link_ability = s.query(Ability).filter(Ability.name == a).first()
				# Actually add the ability to the list of possible abilities
				new_pkmn.possible_abilities.append(link_ability)
			
			s.add(new_pkmn)
		
		else:
			print "Found"
	
		s.commit()
	
	# Done
	s.close()


if __name__ == '__main__':
	scrape_dex()