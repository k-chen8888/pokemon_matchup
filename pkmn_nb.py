'''
Experimental Naive Bayes classifier
'''


import sys, os, math, re, copy, json, random


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
Get the moves for a Pokemon
moveset = s_global.query(Move).filter(Move.pokemon.any(name=pkmn.name)).all()
where pkmn is a database object that represents a Pokemon
'''


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
For a single team, pack it into a dictionary of database objects
'''
def pack(team):
	queried_team = []
	
	# Cleaning house, adding dummy Pokemon to fill space
	while len(team) < 6:
		team.append(MAGIKARP)
	
	for pkmn in team:
		if 'name' in pkmn:
			packed_pkmn = {}
			
			# Extract Pokemon by name
			packed_pkmn['pkmn'] = s_global.query(Pokemon).filter(Pokemon.name == pkmn['name']).first()
			
			# Save actual number of moves
			packed_pkmn['move_count'] = len( pkmn['moves'] )
				
			# Cleaning house, adding dummy moves to fill space
			while len(pkmn['moves']) < 4:
				pkmn['moves'].append("Splash")
			
			# Cleaning house, removing moves if there are too many
			while len(pkmn['moves']) > 4:
				pkmn['moves'].pop()
				
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
			
			# Keep extra information just the way it is
			packed_pkmn['extra'] = pkmn['extra']
			
			# Add to packed list
			queried_team.append( packed_pkmn )
		
		else: # Must be extra information
			pass # not sure what to do with this yet
		
	# Output pre-processed team
	return queried_team


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
	
	# Populate a list of matches with everything queried
	queried_matches = []
	for match in data:
		q = {}
		
		# team1 info, queried
		q['team1'] = pack( match['team1'] )
		
		# team2 info, queried
		q['team2'] = pack( match['team2'] )
		
		q['winner'] = match['winner']
		
		queried_matches.append(q)
	
	return queried_matches


'''
Expands a list of queried matches into a data table arranged as such:
			type1	type2	base stats	move1_info	move2_info	move3_info	move4_info	holditem_info for each pokemon
instances

			win/lose
instances
'''
def expand(matches):
	data_table = []
	results = []
	
	for match in matches:
		team_instance1 = []
		
		# Let 1 = win, 0 = loss
		if match['winner'] == 'team1':
			results.append(1)
			results.append(0)
		else:
			results.append(0)
			results.append(1)
		
		for pkmn in match['team1']:
			# Types
			team_instance1.append(pkmn['pkmn'].type1)
			team_instance1.append(pkmn['pkmn'].type2)
			
			# Base stats
			team_instance1.append(pkmn['pkmn'].base_hp)
			team_instance1.append(pkmn['pkmn'].base_atk)
			team_instance1.append(pkmn['pkmn'].base_def)
			team_instance1.append(pkmn['pkmn'].base_spatk)
			team_instance1.append(pkmn['pkmn'].base_spdef)
			team_instance1.append(pkmn['pkmn'].base_spd)
			
			# Moves
			for move in pkmn['moves']:
				# Basic information
				team_instance1.append(move.move_type)
				team_instance1.append(move.move_cat)
				team_instance1.append(move.base_power)
				team_instance1.append(move.priority)
				team_instance1.append(move.accuracy)
				
				# Special information
				if move.weather:
					team_instance1.append(1)
				else:
					team_instance1.append(0)
				
				if move.entry:
					team_instance1.append(1)
				else:
					team_instance1.append(0)
				
				if move.status:
					team_instance1.append(1)
				else:
					team_instance1.append(0)
				
				if move.heal:
					team_instance1.append(1)
				else:
					team_instance1.append(0)
				
				if move.stat_change:
					team_instance1.append(1)
				else:
					team_instance1.append(0)
			
			# Hold item
			team_instance1.append(pkmn['item'].fling_dmg)
			
			if pkmn['item'].mega_stone:
				team_instance1.append(1)
			else:
				team_instance1.append(0)
			
			team_instance1.append(pkmn['item'].natural_gift_type)
			team_instance1.append(pkmn['item'].natural_gift_power)
			
			# Specific battle statistics
			
			# Boosts
			team_instance1.append(pkmn['extra']['boosts']['accuracy'])
			team_instance1.append(pkmn['extra']['boosts']['atk'])
			team_instance1.append(pkmn['extra']['boosts']['def'])
			team_instance1.append(pkmn['extra']['boosts']['evasion'])
			team_instance1.append(pkmn['extra']['boosts']['hp'])
			team_instance1.append(pkmn['extra']['boosts']['spa'])
			team_instance1.append(pkmn['extra']['boosts']['spd'])
			team_instance1.append(pkmn['extra']['boosts']['spe'])
			
			# Fainted
			team_instance1.append(pkmn['extra']['fainted'])
			
			# Status conditions
			team_instance1.append(pkmn['extra']['status']['Heal Block'])
			team_instance1.append(pkmn['extra']['status']['Ingrain'])
			team_instance1.append(pkmn['extra']['status']['Leech Seed'])
			team_instance1.append(pkmn['extra']['status']['Substitute'])
			team_instance1.append(pkmn['extra']['status']['Taunt'])
			team_instance1.append(pkmn['extra']['status']['brn'])
			team_instance1.append(pkmn['extra']['status']['confusion'])
			team_instance1.append(pkmn['extra']['status']['frz'])
			team_instance1.append(pkmn['extra']['status']['par'])
			team_instance1.append(pkmn['extra']['status']['psn'])
			team_instance1.append(pkmn['extra']['status']['slp'])
			team_instance1.append(pkmn['extra']['status']['tox'])
			team_instance1.append(pkmn['extra']['status']['trapped'])
			team_instance1.append(pkmn['extra']['status']['typechange'])
			
			# Un-boosts
			team_instance1.append(pkmn['extra']['unboosts']['accuracy'])
			team_instance1.append(pkmn['extra']['unboosts']['atk'])
			team_instance1.append(pkmn['extra']['unboosts']['def'])
			team_instance1.append(pkmn['extra']['unboosts']['evasion'])
			team_instance1.append(pkmn['extra']['unboosts']['hp'])
			team_instance1.append(pkmn['extra']['unboosts']['spa'])
			team_instance1.append(pkmn['extra']['unboosts']['spd'])
			team_instance1.append(pkmn['extra']['unboosts']['spe'])
			
			
		data_table.append(team_instance1)
		
		team_instance2 = []
		
		for pkmn in match['team2']:
			# Types
			team_instance2.append(pkmn['pkmn'].type1)
			team_instance2.append(pkmn['pkmn'].type2)
			
			# Base stats
			team_instance2.append(pkmn['pkmn'].base_hp)
			team_instance2.append(pkmn['pkmn'].base_atk)
			team_instance2.append(pkmn['pkmn'].base_def)
			team_instance2.append(pkmn['pkmn'].base_spatk)
			team_instance2.append(pkmn['pkmn'].base_spdef)
			team_instance2.append(pkmn['pkmn'].base_spd)
			
			# Moves
			for move in pkmn['moves']:
				# Basic information
				team_instance2.append(move.move_type)
				team_instance2.append(move.move_cat)
				team_instance2.append(move.base_power)
				team_instance2.append(move.priority)
				team_instance2.append(move.accuracy)
				
				# Special information
				if move.weather:
					team_instance2.append(1)
				else:
					team_instance2.append(0)
				
				if move.entry:
					team_instance2.append(1)
				else:
					team_instance2.append(0)
				
				if move.status:
					team_instance2.append(1)
				else:
					team_instance2.append(0)
				
				if move.heal:
					team_instance2.append(1)
				else:
					team_instance2.append(0)
				
				if move.stat_change:
					team_instance2.append(1)
				else:
					team_instance2.append(0)
			
			# Hold item
			team_instance2.append(pkmn['item'].fling_dmg)
			
			if pkmn['item'].mega_stone:
				team_instance2.append(1)
			else:
				team_instance2.append(0)
			
			team_instance2.append(pkmn['item'].natural_gift_type)
			team_instance2.append(pkmn['item'].natural_gift_power)
			
			# Specific battle statistics
			
			# Boosts
			team_instance2.append(pkmn['extra']['boosts']['accuracy'])
			team_instance2.append(pkmn['extra']['boosts']['atk'])
			team_instance2.append(pkmn['extra']['boosts']['def'])
			team_instance2.append(pkmn['extra']['boosts']['evasion'])
			team_instance2.append(pkmn['extra']['boosts']['hp'])
			team_instance2.append(pkmn['extra']['boosts']['spa'])
			team_instance2.append(pkmn['extra']['boosts']['spd'])
			team_instance2.append(pkmn['extra']['boosts']['spe'])
			
			# Fainted
			team_instance2.append(pkmn['extra']['fainted'])
			
			# Status conditions
			team_instance2.append(pkmn['extra']['status']['Heal Block'])
			team_instance2.append(pkmn['extra']['status']['Ingrain'])
			team_instance2.append(pkmn['extra']['status']['Leech Seed'])
			team_instance2.append(pkmn['extra']['status']['Substitute'])
			team_instance2.append(pkmn['extra']['status']['Taunt'])
			team_instance2.append(pkmn['extra']['status']['brn'])
			team_instance2.append(pkmn['extra']['status']['confusion'])
			team_instance2.append(pkmn['extra']['status']['frz'])
			team_instance2.append(pkmn['extra']['status']['par'])
			team_instance2.append(pkmn['extra']['status']['psn'])
			team_instance2.append(pkmn['extra']['status']['slp'])
			team_instance2.append(pkmn['extra']['status']['tox'])
			team_instance2.append(pkmn['extra']['status']['trapped'])
			team_instance2.append(pkmn['extra']['status']['typechange'])
			
			# Un-boosts
			team_instance2.append(pkmn['extra']['unboosts']['accuracy'])
			team_instance2.append(pkmn['extra']['unboosts']['atk'])
			team_instance2.append(pkmn['extra']['unboosts']['def'])
			team_instance2.append(pkmn['extra']['unboosts']['evasion'])
			team_instance2.append(pkmn['extra']['unboosts']['hp'])
			team_instance2.append(pkmn['extra']['unboosts']['spa'])
			team_instance2.append(pkmn['extra']['unboosts']['spd'])
			team_instance2.append(pkmn['extra']['unboosts']['spe'])
		
		data_table.append(team_instance2)
	
	return data_table, results


'''
Randomly selects 90% of instances to be in the training set and 10% of the instances to be in the validation set
'''
def partition(data_table, results):
	# Store test data and results here
	test = []
	test_res = []
	
	# Store validation data and results here
	valid = []
	valid_res = []
	
	# Generate a list of random numbers, non-repeating
	# This is the validation set
	rand_inst = random.sample( range(0, len(data_table)), len(data_table) / 10 )
	
	for i in range(0, len(data_table)):
		# Append to validation set
		if i in rand_inst:
			valid.append( copy.deepcopy(data_table[i]) )
			valid_res.append( copy.deepcopy(results[i]) )
		
		# Append to test set
		else:
			test.append( copy.deepcopy(data_table[i]) )
			test_res.append( copy.deepcopy(results[i]) )
	
	return test, test_res, valid, valid_res

	
if __name__ == '__main__':
	# Pull instances and results out of JSON table
	json_data = open(sys.argv[1], "r")
	matches = populate(json_data)
	
	# Generate data and results
	data, results = expand(matches)
	
	# Create test and validation sets randomly
	test, test_res, valid, valid_res = partition(data, results)
	
	
	# Run Naive Bayes (Gaussian)
	# Note that numpy arrays are needed
	clf = GaussianNB()
	clf.fit( np.array(test), np.array(test_res) )
	
	tp_nb = 0
	fn_nb = 0
	fp_nb = 0
	tn_nb = 0
	
	# Run some predictions and get [ [tp, fn], [fp, tn] ]
	for i in range(0, len(valid)):
		try:
			predict = clf.predict( valid[i] )
			print predict, str( predict[0] == valid_res[i] )
			
			if predict[0] == 0:
				if predict[0] == valid_res[i]:
					tn_nb += 1
				else:
					fn_nb += 1
			else:
				if predict[0] == valid_res[i]:
					tp_nb += 1
				else:
					fp_nb += 1
		except:
			print "error"
	
	# Output results
	print "tp_nb =", tp_nb
	print "fn_nb =", fn_nb
	print "fp_nb =", fp_nb
	print "tn_nb =", tn_nb
	
	
	# SVM
	l = svm.SVC()
	l.fit( np.array(test), np.array(test_res) )
	
	tp_svm = 0
	fn_svm = 0
	fp_svm = 0
	tn_svm = 0
	
	# Run some predictions and get [ [tp, fn], [fp, tn] ]
	for i in range(0, len(valid)):
		try:
			predict = l.predict( valid[i] )
			print predict, str( predict[0] == valid_res[i] )
			
			if predict[0] == 0:
				if predict[0] == valid_res[i]:
					tn_svm += 1
				else:
					fn_svm += 1
			else:
				if predict[0] == valid_res[i]:
					tp_svm += 1
				else:
					fp_svm += 1
		except:
			print "error"
	
	# Output results
	print "tp_svm =", tp_svm
	print "fn_svm =", fn_svm
	print "fp_svm =", fp_svm
	print "tn_svm =", tn_svm