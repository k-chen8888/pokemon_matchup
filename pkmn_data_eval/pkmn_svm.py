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


'''
Run inputted number of iterations of Naive Bayes using 10 different randomly generated data sets
Save results in a list of lists [ [ tp, fn, fp, tn ], ... ]
Also find mean and standard deviation for each of the 4 measures

Write output to text file
'''
def runSVM(data, results, valid_size, svm_settings, iterations, use_data = None, outfile = True):
	out = []
	acc_list = []
	f = None
	if outfile:
		f = open(svm_settings[0] + "_svm_results.txt", "w")
	
	for i in range(0, iterations):
		# Create test and validation sets randomly
		test, test_res, valid, valid_res = [], [], [], []
		if use_data == None:
			test, test_res, valid, valid_res = partition(data, results, valid_size)
		else:
			test, test_res, valid, valid_res = use_data[0], use_data[1], use_data[2], use_data[3]
		
		# Run support vector machine using the inputted settings
		# Note that numpy arrays are needed
		clf = svm.SVC(kernel = svm_settings[0], degree = svm_settings[1], coef0 = 2 ** svm_settings[3], max_iter = svm_settings[4])
		clf.fit( np.array(test), np.array(test_res) )
		
		# Make note of the current iteration
		if f == None:
			pass
		else:
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
		if f == None:
			pass
		else:
			f.write( "True Positives = " + str(out[i][0]) + "\n" )
			f.write( "False Negatives = " + str(out[i][1]) + "\n" )
			f.write( "False Positives = " + str(out[i][2]) + "\n" )
			f.write( "True Negatives = " + str(out[i][3]) + "\n\n" )
		
		# Precision, recall, and f-score
		prec = float(out[i][0]) / float(out[i][0] + out[i][2]) if out[i][0] > 0 else 0
		if f == None:
			pass
		else:
			f.write( "Precision: " + str(prec) + "\n" )
		rec = float(out[i][0]) / float(out[i][0] + out[i][1]) if out[i][0] > 0 else 0
		if f == None:
			pass
		else:
			f.write( "Recall: " + str(rec) + "\n" )
		fscore = float(2 * rec * prec) / float(rec + prec) if rec > 0 or prec > 0 else 0
		if f == None:
			pass
		else:
			f.write( "F-score: " + str(fscore) + "\n\n" )
		
		# Accuracy
		acc = float(out[i][0] + out[i][3]) / float(out[i][0] + out[i][1] + out[i][2] + out[i][3]) if out[i][0] > 0 or out[i][3] > 0 else 0
		if f == None:
			pass
		else:
			f.write( "Accuracy: " + str(acc) + "\n\n" )
		acc_list.append([acc])
		
		print "Iteration", i, "done"
	
	# Mean and standard deviation of confusion matrix
	out_arr = np.array(out)
	if f == None:
		pass
	else:
		f.write( "Mean of each measure: " + np.array_str( np.mean(out_arr, axis = 0) ) + "\n" )
		f.write( "Standard deviation of each measure: " + np.array_str( np.std(out_arr, axis = 0, dtype = np.float64) ) + "\n\n" )
	
	# Mean and standard deviation of accuracy
	acc_arr = np.array(acc_list)
	acc = np.mean(acc_arr, axis = 0)
	if f == None:
		pass
	else:
		f.write( "Mean accuracy: " + np.array_str( acc ) + "\n" )
		f.write( "Standard deviation of accuracy: " + np.array_str( np.std(acc_arr, axis = 0, dtype = np.float64) ) )
	
		f.close()
	
	print "Done"
	
	if iterations == 1:
		return acc
		


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
	
	# Run user-inputted number of iterations of Naive Bayes
	runSVM(data, results, float( sys.argv[2] ), int( sys.argv[3] ) )