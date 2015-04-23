'''
System tools and utilities
'''
import os, sys, math, re

# JSON tool for reading parsed data file
import json


'''
Data analysis tools
'''
#import numpy as np
#from sklearn.cluster import spectral_clustering


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
'''
# Need to start up a database session first
Session = sessionmaker()
engine = create_engine('sqlite:///pkmn_db_simple.db', echo = True)
Session.configure(bind=engine)

# Work with this one
s_global = Session()
'''

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
	#teams = []
	#results = []
	#json_data = sys.argv[1]
	
	# For each team, compare to each other team
	# Generate an adjacency matrix by calculating similarity as the distance between each team and normalizing
	#adj_mtrx = similarity(teams)
	
	# Generate labels (spectral clustering)
	# Note that the adjacency matrix needs to be converted into a numpy array
	#labels = spectral_clustering(np.asarray(adj_mtrx), n_clusters = 2, eigen_solver = 'arpack', assign_labels = 'discretize')
	
	# Compute the purity of the clustering
	#purity(teams, labels, results)
	
	print "Done"
