'''
Experimental spectral clustering classifier
'''


'''
System tools and utilities
'''
import os, sys, math, re, random

# JSON tool for reading parsed data file
import json


'''
Data analysis tools
'''
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn import svm

# Data cleaning
from pkmn_data_eval.cleaning_tools import *

# Distance measures and data evaluation
from pkmn_dist_simple.mock_battle_simple import *
from pkmn_dist_simple.pkmn_dist_simple import *
from pkmn_dist_simple.clustering_tools import *

# Number of clusters
k = 2


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
Database session tools
'''

# Need to start up a database session first
Session = sessionmaker()
engine = create_engine('sqlite:///pkmn_db_simple.db', echo = True)
Session.configure(bind=engine)

# Work with this one
s_global = Session()


'''
Runs spectral clustering on a given proportion p of the inputted matches for some number of iterations

Returns the labels if only one iteration is made
'''
def spec_cluster(matches, p, mode, iterations):
	labels = []
	win = -1
	
	for i in range(0, iterations):
		# Run the test using the given p
		teams, results = select(matches, p)
		
		# For each team, compare to each other team
		# Generate an adjacency matrix by calculating similarity as the distance between each team and normalizing
		sim_mtrx = similarity(teams)
		adj_mtrx = normalize(sim_mtrx) # Similarity matrix needs to be normalized for spectral clustering
		
		# Generate labels (spectral clustering)
		# Note that the adjacency matrix needs to be converted into a numpy array
		k += i
		labels = spectral_clustering(np.asarray(adj_mtrx), n_clusters = k, eigen_solver = 'arpack', assign_labels = mode)
		
		# Name of file to output test results
		outfile_name = 'test' + str(k) + '_results.txt'
		
		# Compute the purity of the clustering
		win = purity(k, labels, teams, results, sim_mtrx, outfile_name)
	
	if iterations == 1 && k == 2:
		return labels, win
	else:
		return None


'''
sys.argv
	1 -> JSON file
	2 -> Decimal proportion of data to use
	3 -> kmeans or discretize
	4 -> Number of iterations to run for
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
	json_data = open(sys.argv[1], "r")
	matches = populate(json_data)
	
	# Proportion of data to use in the test
	p = float(sys.argv[2])
	
	# Run the clustering
	spec_cluster( matches, p, sys.argv[3], int(sys.argv[4]) )
	
	print "Done"
