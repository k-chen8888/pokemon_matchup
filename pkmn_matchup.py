'''
Experimental classifier that usese NB, SVM, and spectral clustering as an ensemble
'''


'''
System tools and utilities
'''
import os, sys, math, re, random, copy

# JSON tool for reading parsed data file
import json


'''
Data analysis tools
'''
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn import svm

# Distance measures and data evaluation
from pkmn_dist_simple.mock_battle_simple import *
from pkmn_dist_simple.pkmn_dist_simple import *
from pkmn_dist_simple.clustering_tools import *


'''
The functions from all the other evaluators
'''
from pkmn_data_eval.pkmn_spectral import *
from pkmn_data_eval.pkmn_nb import *
from pkmn_data_eval.pkmn_svm import *

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


# A dictionary of movepools for each Pokemon
# Prevents redundant queries
all_movepools = {}


'''
Runs the ensemble off of the results of all other classifiers for a given number of iterations
User may input size of validation set as a proportion p of the data

Output the results to a file
'''
def runEnsemble(matches, labels, win, valid_size, iterations):
	# Generate data and results
	data, results = expand(matches)
	
	# Store results for the ensemble
	out = []
	f = open("ensemble_results.txt", "w")
	
	# Run the ensemble for the given number of iterations
	for i in range(0, iterations):
		# Create test and validation sets randomly
		test, test_res, valid, valid_res = partition(data, results, valid_size)
		
		# Naive Bayes (Gaussian)
		# Note that numpy arrays are needed
		clf_nb = GaussianNB()
		clf_nb.fit( np.array(test), np.array(test_res) )
		
		# Support vector machine
		# Note that numpy arrays are needed
		clf_svm = svm.SVC()
		clf_svm.fit( np.array(test), np.array(test_res) )
		
		# Make note of the current iteration
		f.write( "Iteration " + str(i + 1) + "\n\n" )
		out.append([])
		
		# Preload values
		out[i].append(0) # TP, 0
		out[i].append(0) # FN, 1
		out[i].append(0) # FP, 2
		out[i].append(0) # TN, 3
		
		# Run some predictions and get [ [tp, fn], [fp, tn] ]
		for j in range(0, len(valid)):
			try:
				win_vote = 0
				lose_vote = 0
				
				# Run all predictors
				predict_nb = clf_nb.predict( valid[j] )
				if predict_nb[0] == 0:
					lose_vote += 1
				else:
					win_vote += 1
				predict_svm = clf_svm.predict( valid[j] )
				if predict_svm[0] == 0:
					lose_vote += 1
				else:
					win_vote += 1
				predict_spec = [1] if labels [ data.index( valid[j] ) ] == win else [0]
				if predict_spec[0] == 0:
					lose_vote += 1
				else:
					win_vote += 1
				
				# Take the majority vote
				predict = 0 if lose_vote > win_vote else 1
				
				if predict == 0: # N
					if predict == valid_res[j]: # TN
						out[i][3] += 1
					else: # FN
						out[i][1] += 1
				else: # P
					if predict == valid_res[j]: # TP
						out[i][0] += 1
					else: # FP
						out[i][2] += 1
			except:
				print "error"
		
		# Output results
		f.write( "True Positives = " + str(out[i][0]) + "\n" )
		f.write( "False Negatives = " + str(out[i][1]) + "\n" )
		f.write( "False Positives = " + str(out[i][2]) + "\n" )
		f.write( "True Negatives = " + str(out[i][3]) + "\n\n" )
		
		# Precision, recall, and f-score
		prec = float(out[i][0]) / float(out[i][0] + out[i][2]) if out[i][0] > 0 else 0
		f.write( "Precision: " + str(prec) + "\n")
		rec = float(out[i][0]) / float(out[i][0] + out[i][1]) if out[i][0] > 0 else 0
		f.write( "Recall: " + str(rec) + "\n")
		fscore = float(2 * rec * prec) / float(rec + prec) if rec > 0 or prec > 0 else 0
		f.write( "F-score: " + str(fscore) + "\n\n")
		
		# Accuracy
		acc = float(out[i][0] + out[i][3]) / float(out[i][0] + out[i][1] + out[i][2] + out[i][3]) if out[i][0] > 0 or out[i][3] > 0 else 0
		f.write( "Accuracy: " + str(acc) + "\n\n\n")
		
		print "Iteration", i, "done"
	
	# Mean and standard deviation
	out_arr = np.array(out)
	f.write( "Mean of each measure: " + np.array_str( np.mean(out_arr, axis = 0) ) + "\n")
	f.write( "Standard deviation of each measure: " + np.array_str( np.std(out_arr, axis = 0, dtype=np.float64) ) + "\n\n\n")
	
	f.close()
	print "Done"


'''
sys.argv
	1 -> JSON file
	2 -> Decimal proportion of data to use as the validation set
	3 -> kmeans or discretize
	4 -> Number of times to run the ensemble method
'''
if __name__ == '__main__':
	# Pull instances and results out of JSON table
	json_data = open(sys.argv[1], "r")
	matches = populate(json_data)
	
	# Run spectral clustering ONCE on the all of the matches to get the labels
	labels, win = spec_cluster( matches, 1.0, sys.argv[3], 1 )
	
	# Run the ensemble using the data received from the spectral clustering
	runEnsemble(matches, labels, win, float( sys.argv[2] ), int( sys.argv[4] ) )