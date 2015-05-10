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
def runEnsemble(matches, labels, win, valid_size, all_settings, iterations):
	# Generate data and results
	data, results = expand(matches)
	
	# Store results for the ensemble
	out = []
	acc_list = []
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
		clf_svm = []
		for j in range(0, len(all_settings)):
			svm_settings = all_settings[j]
			clf_svm.append( svm.SVC(kernel = svm_settings[0], degree = svm_settings[1], gamma = 1 / float( svm_settings[2] ), coef0 = 2 ** svm_settings[3], max_iter = svm_settings[4]) )
			clf_svm[j].fit( np.array(test), np.array(test_res) )
		
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
				# Naive Bayes
				predict_nb = clf_nb.predict( valid[j] )
				if predict_nb[0] == 0:
					lose_vote += 1
				else:
					win_vote += 1
				# SVM
				for l in range(0, len(clf_svm)):
					predict_svm = clf_svm[l].predict( valid[j] )
					if predict_svm[0] == 0:
						lose_vote += 0.25
					else:
						win_vote += 0.25
				# Spectral Clustering
				predict_spec = []
				for k in range(0, len(win)):
					predict_spec = [1] if labels [ data.index( valid[j] ) ] == win[k] else [0]
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
		f.write( "Precision: " + str(prec) + "\n" )
		rec = float(out[i][0]) / float(out[i][0] + out[i][1]) if out[i][0] > 0 else 0
		f.write( "Recall: " + str(rec) + "\n" )
		fscore = float(2 * rec * prec) / float(rec + prec) if rec > 0 or prec > 0 else 0
		f.write( "F-score: " + str(fscore) + "\n\n" )
		
		# Accuracy
		acc = float(out[i][0] + out[i][3]) / float(out[i][0] + out[i][1] + out[i][2] + out[i][3]) if out[i][0] > 0 or out[i][3] > 0 else 0
		f.write( "Accuracy: " + str(acc) + "\n\n" )
		acc_list.append([acc])
		
		print "Iteration", i, "done"
	
	# Mean and standard deviation of confusion matrix
	out_arr = np.array(out)
	f.write( "Mean of each measure: " + np.array_str( np.mean(out_arr, axis = 0) ) + "\n" )
	f.write( "Standard deviation of each measure: " + np.array_str( np.std(out_arr, axis = 0, dtype = np.float64) ) + "\n\n" )
	
	# Mean and standard deviation of accuracy
	acc_arr = np.array(acc_list)
	f.write( "Mean accuracy: " + np.array_str( np.mean(acc_arr, axis = 0) ) + "\n" )
	f.write( "Standard deviation of accuracy: " + np.array_str( np.std(acc_arr, axis = 0, dtype = np.float64) ) )
	
	f.close()
	print "Done"


'''
sys.argv
	1 -> JSON file
	2 -> Decimal proportion of data to use as the validation set (modes 0, 2, 3)
	3 -> kmeans or discretize
	4 -> Number of times to run chosen method
	5 -> Mode
		0 = ensemble
		1 = spectral clustering
		2 = naive bayes
		3 = svm
'''
if __name__ == '__main__':
	# Pull instances and results out of JSON table
	json_data = open(sys.argv[1], "r")
	matches = populate(json_data)
	
	# Run the ensemble using the data received from the spectral clustering
	if int(sys.argv[5]) == 0:
		# Run spectral clustering ONCE on the all of the matches to get the labels
		labels, win = spec_cluster( matches, 1.0, sys.argv[3], 0, 1 )
		
		# Generate data and results
		data, results = expand(matches)
		
		# Generate optimal settings for each SVM in the ensemble
		test, test_res, valid, valid_res = partition(data, results, float( sys.argv[2] ))
		set_data = [test, test_res, valid, valid_res]
		
		all_svm_settings = []
		# Cross-validation to determine SVM settings
		for mode in ['linear', 'poly', 'rbf', 'sigmoid']:
			# [kernel, degree, gamma, coef0, max_iter]
			svm_settings = []
			
			# Determine the best settings for each mode
			if mode == 'linear' or mode == 'rbf':
				all_svm_settings.append( ['linear', 3, len(data[1]), 0.0, 10000] )
			
			elif mode == 'poly':
				best_acc = 0.0
				best_settings = ['poly', 2, 1, 0.0, 10000]
				
				# Run cross-validation to determine best settings
				for degree in range(2, 9): # degree
					for j in range(-10, 6): # coef0
						print "Degree", degree, "polynomial with and coefficient of 2 **", j
						
						svm_settings = ['poly', degree, len(data[1]), j, 10000]
						acc = runSVM(data, results, float( sys.argv[2] ), svm_settings, 1, use_data = set_data, outfile = False )
						
						# Update accuracy
						if acc > best_acc:
							best_acc = acc
							best_settings = svm_settings
				
				all_svm_settings.append( best_settings )
			
			else: # mode == 'sigmoid'
				best_acc = 0.0
				best_settings = ['sigmoid', 2, 1, 0.0, 10000]
				
				# Run cross-validation to determine best settings
				for j in range(-10, 6): # coef0
					print "Sigmoid with coefficient of 2 **", j
					
					svm_settings = ['sigmoid', degree, 1, j, 10000]
					acc = runSVM(data, results, float( sys.argv[2] ), svm_settings, 1, use_data = set_data, outfile = False )
					
					# Update accuracy
					if acc > best_acc:
						best_acc = acc
						best_settings = svm_settings
				
				all_svm_settings.append( best_settings )
		
		print svm_settings
		runEnsemble(matches, labels, win, float( sys.argv[2] ), all_svm_settings, int( sys.argv[4] ) )
	
	elif int(sys.argv[5]) == 1:
		spec_cluster( matches, float( sys.argv[2] ), sys.argv[3], 0, int( sys.argv[4] ) )
	
	elif int(sys.argv[5]) == 2:
		# Generate data and results
		data, results = expand(matches)
		
		runNB( data, results, float( sys.argv[2] ), int( sys.argv[4] ) )
	
	elif int(sys.argv[5]) == 3:
		# Generate data and results
		data, results = expand(matches)
		
		# Run SVM sys.argv[4] times for each kernel
		test, test_res, valid, valid_res = partition(data, results, float( sys.argv[2] ))
		set_data = [test, test_res, valid, valid_res]
		
		# Cross-validation to determine SVM settings
		for mode in ['linear', 'poly', 'rbf', 'sigmoid']:
			# [kernel, degree, gamma, coef0, max_iter]
			svm_settings = []
			
			# Determine the best settings for each mode
			if mode == 'linear' or mode == 'rbf':
				svm_settings = ['linear', 3, len(data[1]), 0.0, 10000]
			
			elif mode == 'poly':
				best_acc = 0.0
				best_settings = ['poly', 2, 1, 0.0, 10000]
				
				# Run cross-validation to determine best settings
				for degree in range(2, 9): # degree
					for j in range(-10, 6): # coef0
						print "Degree", degree, "polynomial with and coefficient of 2 **", j
						
						svm_settings = ['poly', degree, len(data[1]), j, 10000]
						acc = runSVM(data, results, float( sys.argv[2] ), svm_settings, 1, use_data = set_data, outfile = False )
						
						# Update accuracy
						if acc > best_acc:
							best_acc = acc
							best_settings = svm_settings
				
				svm_settings = best_settings
			
			else: # mode == 'sigmoid'
				best_acc = 0.0
				best_settings = ['sigmoid', 2, 1, 0.0, 10000]
				
				# Run cross-validation to determine best settings
				for j in range(-10, 6): # coef0
					print "Sigmoid with coefficient of 2 **", j
					
					svm_settings = ['sigmoid', degree, 1, j, 10000]
					acc = runSVM(data, results, float( sys.argv[2] ), svm_settings, 1, use_data = set_data, outfile = False )
					
					# Update accuracy
					if acc > best_acc:
						best_acc = acc
						best_settings = svm_settings
				
				svm_settings = best_settings
			
			print svm_settings
			runSVM(data, results, float( sys.argv[2] ), svm_settings, int( sys.argv[4] ) )
	
	else:
		print "Invalid choice"