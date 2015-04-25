'''
Various distance measures for determining how similar two teams are

Evaluate distance for two Pokemon in terms of...
	Type similarity... it is safe to assume that...
		1. If two Pokemon have the same type, their type distance is 0
		2. If two Pokemon have different types, then type advantages determine similarity (compute two type advantage rows and take the Euclidean distance)
	
	Move type similarity: The distribution of move types that a team has
	
	Base stat simimlarity (Euclidean distance on a 1x6 vector)
	
	Move similarity
		If the names match, declare the moves to be identical
		Otherwise, take the Euclidean distance on [Category, Base Power, Accuracy, Priority]
		Average the similarity of each move with each other move
	
Perform the measure with each possible pairing of Pokemon and output the average
'''
import os, sys, re, math, copy

# Query Pokemon from database to get information
from scrape_db_simple.pkmn_db_simple import *

# Use to get a distance measure for each Pokemon based on mock battles
from mock_battle_simple import *


'''
Load database
'''
'''
# Need to start up a database session first
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Session = sessionmaker(autoflush=False)
engine = create_engine('sqlite:///pkmn_db_simple.db', echo = True)
Session.configure(bind=engine)

# Work with this one
s_dist = Session()
'''

'''
Distance between teams

Define a team as a list of Pokemon
'''
def team_dist(team1, team2, mode):
	if team1 == team2: # Identical teams means distance = 0
		return 0.0
	
	# Use a different metric based on mode
	if mode == 0: # Basic team difference
		# Type distributions for each team
		team1_types = [0] * 18
		team2_types = [0] * 18
		
		# Populate type distribution lists
		for p in team1:
			team1_types[p['pkmn'].type1] += 1
			if p['pkmn'].type2 > -1:
				team1_types[p['pkmn'].type2] += 1
		for p in team2:
			team2_types[p['pkmn'].type1] += 1
			if p['pkmn'].type2 > -1:
				team2_types[p['pkmn'].type2] += 1
		
		# Squared distance of type distribution
		type_dist = sum( [ (team1_types[i] - team2_types[i]) ** 2 for i in range(0, 18) ] )
		
		# Squared distance of move type distribution
		team1_move_types = [0] * 18
		team2_move_types = [0] * 18
		
		# Populate move type distribution lists
		for p in team2:
			for m in p['moves']:
				if not m.name == "Splash":
					team1_move_types[m.move_type] += 1
		for p in team2:
			for m in p['moves']:
				if not m.name == "Splash":
					team2_move_types[m.move_type] += 1 
		
		# Squared distance of type distribution
		move_type_dist = sum( [ (team1_move_types[i] - team2_move_types[i]) ** 2 for i in range(0, 18) ] )
		
		# Output square root
		return ( type_dist + move_type_dist ) ** 0.5
	
	elif mode == 1: # Pokemon difference
		# Simple distance between each pkmn1 on team1 and each other pkmn2 on team2
		pkmn_distance = 0
		for pkmn1 in team1:
			for pkmn2 in team2:
				# Distances between pkmn1 and each opponent
				# Add to total
				pkmn_distance += pkmn_dist(pkmn1, pkmn2)
		
		# Output square root
		return pkmn_distance ** 0.5
		
	else: # Mock battle difference
		# Squared "distance" between base strengths of Pokemon
		# Use mock_battle_simple
		mock_results = mock_battle(team1, team2)
		
		# Output square root
		return mock_results ** 0.5


'''
Distance between Pokemon

Define each Pokemon in the team as a dictionary
	'name' -> String, Pokemon official name
	'moves' -> List of moves
'''
def pkmn_dist(pkmn1, pkmn2):
	# Type Similarity
	type_dist = 0
	if not pkmn1['pkmn'].type1 == pkmn2['pkmn'].type1 or not pkmn1['pkmn'].type2 == pkmn2['pkmn'].type2:
		# Table for first Pokemon
		adv_table_pkmn1 = []
		for i in range(0, 18):
			if pkmn1['pkmn'].type2 == -1:
				adv_table_pkmn1.append( typing[i][pkmn1['pkmn'].type1] )
			else:
				adv_table_pkmn1.append( typing[i][pkmn1['pkmn'].type1] * typing[i][pkmn1['pkmn'].type2] )
		
		# Table for second Pokemon
		adv_table_pkmn2 = []
		for i in range(0, 18):
			if pkmn2['pkmn'].type2 == -1:
				adv_table_pkmn2.append( typing[i][pkmn2['pkmn'].type1] )
			else:
				adv_table_pkmn2.append( typing[i][pkmn2['pkmn'].type1] * typing[i][pkmn2['pkmn'].type2] )
		
		# Euclidean Distance
		type_dist = sum( [ ( adv_table_pkmn1[i] - adv_table_pkmn2[i] ) ** 2 for i in range(0, 18) ] )
	
	
	# Distance between base stats
	pkmn1_base = sum([ pkmn1['pkmn'].base_hp, pkmn1['pkmn'].base_atk, pkmn1['pkmn'].base_def, pkmn1['pkmn'].base_spatk, pkmn1['pkmn'].base_spdef, pkmn1['pkmn'].base_spd ])
	pkmn2_base = sum([ pkmn2['pkmn'].base_hp, pkmn2['pkmn'].base_atk, pkmn2['pkmn'].base_def, pkmn2['pkmn'].base_spatk, pkmn2['pkmn'].base_spdef, pkmn2['pkmn'].base_spd ])
	base_dist = (pkmn1_base - pkmn2_base) ** 2
	
	# Pairwise distance between each move, averaged using the number of moves it was compared to
	m_dist = 0
	for move1 in pkmn1['moves']:
		for move2 in pkmn2['moves']:
			m_dist += move_dist(move1, move2)
	
	# Distance between hold items
	i_dist = item_dist(pkmn1['item'], pkmn2['item'])
	
	# Output sum
	return type_dist + base_dist# + m_dist + i_dist


'''
Distance between moves
Moves given by name only and queried
'''
def move_dist(move1, move2):
	if move1 == move2:
		return 0 # No distance if they're the same
	
	elif move1.name == "Splash" or move2.name == "Splash":
		return 0 # Ignore Splash
	
	else:
		# Take the Euclidean distance (squared)
		sq_dist_m = 0
		
		sq_dist_m += 1 if move1.move_type == move2.move_type else 0 # Types match
		sq_dist_m += 1 if move1.move_cat == move2.move_cat else 0 # Category
		sq_dist_m += (move1.base_power - move2.base_power) ** 2 # Base Power
		sq_dist_m += (move1.priority - move2.priority) ** 2 # Accuracy
		sq_dist_m += (move1.accuracy - move2.accuracy) ** 2 # Priority
		
		# Output sum
		return sq_dist_m


'''
Distance between hold items
Items objects are given
'''
def item_dist(item1, item2):
	if item1 == item2:
		return 0 # No distance if they're the same
	
	elif item1.name == "Soothe Bell" or item2.name == "Soothe Bell":
		return 0 # Ignore Soothe Bell
	
	else:
		# Take the Euclidean distance (squared)
		sq_dist_i = 0
		
		sq_dist_i += (item1.fling_dmg - item2.fling_dmg) ** 2 # Power of Fling
		sq_dist_i += 1 if not item1.mega_stone == item2.mega_stone else 0 # Is it a Mega Stone (take XOR)?
		sq_dist_i += 1 if item1.natural_gift_type == item2.natural_gift_type else 0 # Type for Natural Gift
		sq_dist_i += (item1.natural_gift_power - item2.natural_gift_power) ** 2 # Power of Natural Gift
		sq_dist_i += (item1.se_dmg_down - item2.se_dmg_down) ** 2 # Does it reduce super-effective damage?
		
		# Output squared distance
		return sq_dist_i


'''
Similarity between teams

Builds and normalizes distance matrix to create adjacency matrix
'''
def similarity(teams):
	# Start off with empty array
	sim = []
	for i in range(0, len(teams)):
		row = []
		
		for j in range(0, len(teams)):
			row.append(-1)
		
		sim.append(row)
	
	# Populate with actual values
	
	# mode = 0, basic team similarity
	sim0 = copy.deepcopy(sim)
	
	# mode = 1, pkmn_dist
	sim1 = copy.deepcopy(sim)
	
	# mode = 2, mock_battle
	sim2 = copy.deepcopy(sim)
	
	for i in range(0, len(sim)):
		for j in range(0, i + 1):
			if i == j: # Same team means distance of 0
				sim0[i][j] = 0.0
			else:
				# mode = 0, basic team similarity
				sim0[i][j] = team_dist(teams[i], teams[j], 1)
				sim0[j][i] = sim0[i][j]
				
				# mode = 1, pkmn_dist
				sim1[i][j] = team_dist(teams[i], teams[j], 1)
				sim1[j][i] = sim1[i][j]
				
				# mode = 2, mock_battle
				sim2[i][j] = team_dist(teams[i], teams[j], 2)
				sim2[j][i] = sim2[i][j]
				
			print "M0 Calculation", i, j, "complete; go to next entry"
		
		print "M0 Calculation", i, "complete; go to next row"
	
	# Normalize and sum all 3 measures
	sim0_n = normalize(sim0)
	sim1_n = normalize(sim1)
	sim2_n = normalize(sim2)
	
	for i in range(0, len(sim)):
		for j in range(0, i + 1):
			if i == j: # Same team means distance of 0
				sim[i][j] = 0.0
			else:
				sim[i][j] = sim0_n[i][j] + sim1_n[i][j] + sim2_n[i][j]
				sim[j][i] = sim[i][j]
	
	return sim


'''
Normalize an adjacency matrix
'''
def normalize(adj):
	adj_norm = []
	
	min_val = sys.maxint
	max_val = 0
	
	# Get min and max values
	for row in adj:
		for value in row:
			if value < min_val:
				min_val = value
			if value > max_val:
				max_val = value
	
	# Use the equation (x - min) / (max - min)
	for row in adj:
		adj_norm_row = []
		
		for i in range(0, len(row)):
			adj_norm_row.append( (row[i] - min_val) / (max_val - min_val) )
		
		adj_norm.append(adj_norm_row)
	
	return adj_norm


'''
Stops the database session for distance measures
'''
def stop_dist():
	s_dist.close()