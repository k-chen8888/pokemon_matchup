'''
Experimental SVM classifier
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

# Data cleaning
from pkmn_data_eval.cleaning_tools import *

# Distance measures and data evaluation
from pkmn_dist_simple.mock_battle_simple import *
from pkmn_dist_simple.pkmn_dist_simple import *
from pkmn_dist_simple.clustering_tools import *


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
Run inputted number of iterations of Naive Bayes using 10 different randomly generated data sets
Save results in a list of lists [ [ tp, fn, fp, tn ], ... ]
Also find mean and standard deviation for each of the 4 measures

Write output to text file
'''
def runSVM(data, results, valid_size, iterations):
	out = []
	f = open("svm_results.txt", "w")
	
	for i in range(0, iterations):
		# Add iteration to array
		out.append([])
		
		# Create test and validation sets randomly
		test, test_res, valid, valid_res = partition(data, results, valid_size)
		
		# Run support vector machine
		# Note that numpy arrays are needed
		clf = svm.SVC()
		clf.fit( np.array(test), np.array(test_res) )
		
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
				predict = clf.predict( valid[j] )
				
				if predict[0] == 0: # N
					if predict[0] == valid_res[j]: # TN
						out[i][3] += 1
					else: # FN
						out[i][1] += 1
				else: # P
					if predict[0] == valid_res[j]: # TP
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
		f.write( "F-score: " + str(fscore) + "\n\n\n")
		
		# Accuracy
		acc = float(out[i][0] + out[i][3]) / float(out[i][0] + out[i][1] + out[i][2] + out[i][3]) if out[i][0] > 0 or out[i][3] > 0 else 0
		f.write( "Accuracy: " + str(acc) + "\n\n")
		
		print "Iteration", i, "done"
	
	f.close()
	print "Done"


'''
sys.argv
	1 -> JSON file
	2 -> Decimal proportion of data to use as the validation set
	3 -> Number of iterations to run Naive Bayes
'''
if __name__ == '__main__':
	# Pull instances and results out of JSON table
	json_data = open(sys.argv[1], "r")
	matches = populate(json_data)
	
	# Generate data and results
	data, results = expand(matches)
	
	# Run 50 iterations of Naive Bayes
	runSVM(data, results, float( sys.argv[2] ), int( sys.argv[3] ) )