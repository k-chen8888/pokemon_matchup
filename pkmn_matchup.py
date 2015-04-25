'''
System tools and utilities
'''
import os, sys, math, re

# JSON tool for reading parsed data file
import json


'''
Data analysis tools
'''
import numpy as np
from sklearn.cluster import spectral_clustering


'''
All scraper and db tools
'''
from scrape_db_simple.pkmn_db_simple import *
from scrape_db_simple.scrape_abilities import *
from scrape_db_simple.scrape_items import *
from scrape_db_simple.scrape_moves import *
from scrape_db_simple.scrape_pkmn import *

# Runs the scraper
from scrape_db_simple.scrape_dex_simple import *

# SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


'''
All parser and data cleaning tools
'''
# Parsing Pokemon Showdown data and generating data dictionaries

# Distance measures and data evaluation
from pkmn_dist_simple.mock_battle_simple import *
from pkmn_dist_simple.pkmn_dist_simple import *
from pkmn_dist_simple.clustering_tools import *


'''
Database session tools
'''

# Need to start up a database session first
Session = sessionmaker()
engine = create_engine('sqlite:///pkmn_db_simple.db', echo = True)
Session.configure(bind=engine)

# Work with this one
s_global = Session()


'''
For each team in the list, pack it into a 
'''
def pack(teams):
	# New list of teams
	all_teams = []
	
	for team in teams:
		queried_team = []
		
		# Cleaning house, adding dummy Pokemon to fill space
		while len(team) < 6:
			team.append(MAGIKARP)
		
		for pkmn in team:
			packed_pkmn = {}
			
			# Extract Pokemon by name
			packed_pkmn['pkmn'] = s_global.query(Pokemon).filter(Pokemon.name == pkmn['name']).first()
			
			# Save actual number of moves
			packed_pkmn['move_count'] = len( pkmn['moves'] )
			
			# Cleaning house, adding dummy moves to fill space
			while len(pkmn['moves']) < 4:
				pkmn['moves'].append("Splash")
			
			packed_pkmn['moves'] = []
			# Extract moves by name
			for move in pkmn['moves']:
				packed_pkmn['moves'].append( get_move(move, s_global) )
			
			# Extract items; give it a useless Soothe Bell if it has no item
			if 'item' in pkmn:
				if pkmn['item'] == None:
					packed_pkmn['item'] = s_global.query(HoldItem).filter(HoldItem.name == "Soothe Bell").first()
				else:
					packed_pkmn['item'] = s_global.query(HoldItem).filter(HoldItem.name == pkmn['item']).first()
			
			else:
				packed_pkmn['item'] = s_global.query(HoldItem).filter(HoldItem.name == "Soothe Bell").first()
			
			# Just in case
			if packed_pkmn['item'] == None:
				packed_pkmn['item'] = s_global.query(HoldItem).filter(HoldItem.name == "Soothe Bell").first()
			
			# Add to packed list
			queried_team.append( packed_pkmn )
		
		all_teams.append( queried_team )
	
	# Output pre-processed list
	return all_teams


'''
Parsed data file is formatted with newlines
Convert to no newlines, populate and output...
	Array of teams
		Pack each team by pre-querying everything
	Array of results
'''
def populate(json_file):
	# Build json string, without newlines
	json_str = ""
	for line in json_file:
		json_str += line.rstrip()
	
	# Interpret string
	data = json.loads(json_str)
	
	# Populate lists
	teams = []
	results = []
	for match in data:
		# team1 info
		teams.append( match['team1'] )
		if match['winner'] == 'team1':
			results.append(True)
		else:
			results.append(False)
		
		# team2 info
		teams.append( match['team2'] )
		if match['winner'] == 'team2':
			results.append(True)
		else:
			results.append(False)
	
	# Query now, or forever hold your silence
	teams = pack(teams)
	
	return teams, results


if __name__ == '__main__':
	# Gather the data and fill up the database
	#scrape_dex()
	
	'''
	Take the json dictionaries and make a list of teams (split up all match pairs) and a list of results
	Results is boolean list
		True = win
		False = loss
	Index of a given result is equal to the index of the team it is associated with
	'''
	json_data = open(sys.argv[1], "r")
	teams, results = populate(json_data)
	
	# For each team, compare to each other team
	# Generate an adjacency matrix by calculating similarity as the distance between each team and normalizing
	sim_mtrx = similarity(teams)
	adj_mtrx = normalize(sim_mtrx) # Similarity matrix needs to be normalized for spectral clustering
	
	# Generate labels (spectral clustering)
	# Note that the adjacency matrix needs to be converted into a numpy array
	# Run the clustering 5 times
	i = 1
	while i < 6:
		labels = spectral_clustering(np.asarray(adj_mtrx), n_clusters = 2, eigen_solver = 'arpack', assign_labels = 'discretize')
		
		# Name of file to output test results
		outfile_name = 'test' + str(i) + '_results.txt'
		
		# Compute the purity of the clustering
		purity(labels, teams, results, sim_mtrx, outfile_name)
		
		# Next test
		i += 1
	
	# Close out all sessions
	#stop_dist()
	#stop_mock()
	
	print "Done"
