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
import os, sys, re, math

# Query Pokemon from database to get information
from scrape_db_simple.pkmn_db_simple import *

# Use to get a distance measure for each Pokemon based on mock battles
from mock_battle_simple import *


'''
Load database
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
Distance between teams

Define a team as a list of Pokemon
'''
def team_dist(team1, team2):
	if team1 == team2: # Identical teams means distance = 0
		return 0.0
	
	# Type distributions for each team
	team1_types = [0] * 18
	team2_types = [0] * 18
	
	# Populate type distribution lists
	for p in team1:
		p1 = s_dist.query(Pokemon).filter(Pokemon.name == p['name']).first()
		team1_types[p1.type1] += 1
		if p1.type1 > -1:
			team1_types[p1.type2] += 1
	for p in team2:
		p2 = s_dist.query(Pokemon).filter(Pokemon.name == p['name']).first()
		team2_types[p2.type1] += 1
		if p2.type1 > -1:
			team2_types[p2.type2] += 1
	
	# Squared distance of type distribution
	type_dist = sum( [ (team1_types[i] - team2_types[i]) ** 2 for i in range(0, 18) ] )
	
	# Squared distance of move type distribution
	team1_move_types = [0] * 18
	team2_move_types = [0] * 18
	
	# Populate move type distribution lists
	for p in team2:
		for m in p['moves']:
			m1 = get_move(m, s_dist)
			team1_move_types[m1.move_type] += 1
	for p in team2:
		for m in p['moves']:
			m2 = get_move(m, s_dist)
			team2_move_types[m2.move_type] += 1
	
	# Squared distance of type distribution
	move_type_dist = sum( [ (team1_move_types[i] - team2_move_types[i]) ** 2 for i in range(0, 18) ] )
	
	# Pairwise squared distances between each Pokemon (if full teams of 6 Pokemon, there are 36 calculations made)
	# Get a list of distances for each Pokemon on the team
	# Each entry in team#_distances is the average distance between a Pokemon on team# and every other Pokemon on the opposite team
	team1_distances = []
	team2_distances = []
	for pkmn1 in team1:
		for pkmn2 in team2:
			# Distances between pkmn1 and each opponent
			pkmn1_distances = []
			pkmn1_distances.append( pkmn_dist(pkmn1, pkmn2) )
			
			# Append the average distance
			team1_distances.append( sum(pkmn1_distances) / len(pkmn1_distances) )
	
	for pkmn1 in team2:
		for pkmn2 in team1:
			# Distances between pkmn1 and each opponent
			pkmn1_distances = []
			pkmn1_distances.append( pkmn_dist(pkmn1, pkmn2) )
			
			# Append the average distance
			team2_distances.append( sum(pkmn1_distances) / len(pkmn1_distances) )
	
	avg_dist = sum( [ (team1_distances[i] - team2_distances[i]) ** 2 for i in range(0, len(team1_distances)) ] )
	
	# Squared "distance" between base strengths of Pokemon
	# Use mock_battle_simple
	mock_results = mock_battle(team1, team2)
	
	# Output square root of sum
	return ( type_dist + move_type_dist + avg_dist + mock_results ) ** 0.5


'''
Distance between Pokemon

Define each Pokemon in the team as a dictionary
	'name' -> String, Pokemon official name
	'moves' -> List of moves
'''
def pkmn_dist(pkmn1, pkmn2):
	# Query each Pokemon from the database
	p1 = s_dist.query(Pokemon).filter(Pokemon.name == pkmn1['name']).first()
	p2 = s_dist.query(Pokemon).filter(Pokemon.name == pkmn2['name']).first()
	
	# Type Similarity
	type_dist = 0
	if not p1.type1 == p2.type1 or not p1.type2 == p2.type2:
		# Table for first Pokemon
		adv_table_p1 = []
		for i in range(0, 18):
			if p1.type2 == -1:
				adv_table_p1.append( typing[i][p1.type1] )
			else:
				adv_table_p1.append( typing[i][p1.type1] * typing[i][p1.type2] )
		
		# Table for second Pokemon
		adv_table_p2 = []
		for i in range(0, 18):
			if p2.type2 == -1:
				adv_table_p2.append( typing[i][p2.type1] )
			else:
				adv_table_p2.append( typing[i][p2.type1] * typing[i][p2.type2] )
		
		# Euclidean Distance
		type_dist = sum( [ ( adv_table_p1[i] - adv_table_p2[i] ) ** 2 for i in range(0, 18) ] )
	
	
	# Distance between base stats
	pkmn1['base'] = [ p1.base_hp, p1.base_atk, p1.base_def, p1.base_spatk, p1.base_spdef, p1.base_spd ]
	pkmn2['base'] = [ p2.base_hp, p2.base_atk, p2.base_def, p2.base_spatk, p2.base_spdef, p2.base_spd ]
	base_dist = sum( [ ( pkmn1['base'][i] - pkmn2['base'][i] ) ** 2 for i in range(0, 6) ] )
	
	# Pairwise distance between each move, averaged using the number of moves it was compared to
	m_dist = sum( [ ( sum( [ move_dist(move1, move2) for move1 in pkmn1['moves'] ] ) / float( len(pkmn2['moves']) ) ) for move2 in pkmn2['moves'] ] )
	
	# Distance between hold items
	i_dist = item_dist(pkmn1, pkmn2)
	
	# Output sum
	return ( type_dist + base_dist + m_dist + i_dist) ** 0.5


'''
Distance between moves
Moves given by name only and queried
'''
def move_dist(move1, move2):
	if move1 == move2:
		return 0 # No distance if they're the same
	
	else:
		m1 = get_move(move1, s_dist)
		m2 = get_move(move2, s_dist)
		
		# Take the Euclidean distance (squared)
		sq_dist_m = 0
		
		sq_dist_m += 1 if m1.move_type == m2.move_type else 0 # Types match
		sq_dist_m += 1 if m1.move_cat == m2.move_cat else 0 # Category
		sq_dist_m += (m1.base_power - m2.base_power) ** 2 # Base Power
		sq_dist_m += (m1.priority - m2.priority) ** 2 # Accuracy
		sq_dist_m += (m1.accuracy - m2.accuracy) ** 2 # Priority
		
		# Output sum
		return sq_dist_m


'''
Distance between hold items
Items given by name only and queried
'''
def item_dist(pkmn1, pkmn2):
	# Find the item
	# If no hold item, give it a useless Soothe Bell
	i1 = s_dist.query(HoldItem).filter(HoldItem.name == pkmn1['item']).first() if pkmn1['item'] != None else s_dist.query(HoldItem).filter(HoldItem.name == "Soothe Bell").first()
	i2 = s_dist.query(HoldItem).filter(HoldItem.name == pkmn2['item']).first() if pkmn2['item'] != None else s_dist.query(HoldItem).filter(HoldItem.name == "Soothe Bell").first()
	
	# Take the Euclidean distance (squared)
	sq_dist_i = 0
	
	sq_dist_i += (i1.fling_dmg - i2.fling_dmg) ** 2 # Fling
	sq_dist_i += 1 if not i1.mega_stone == i2.mega_stone else 0 # Is it a Mega Stone (take XOR)?
	sq_dist_i += (i1.natural_gift_type - i2.natural_gift_type) ** 2 # Type for Natural Gift
	sq_dist_i += (i1.natural_gift_power - i2.natural_gift_power) ** 2 # Power of Natural Gift
	sq_dist_i += (i1.se_dmg_down - i2.se_dmg_down) ** 2 # Does it reduce super-effective damage?
	
	# Output squared distance
	return sq_dist_i


'''
Similarity between teams

Builds and normalizes distance matrix to create adjacency matrix
'''
def similarity(teams):
	adj = []
	
	# Get distance between each team
	for team1 in teams:
		adj_row = []
		
		for team2 in teams:
			adj_row.append( team_dist(team1, team2) )
		
		adj.append(adj_row)
	
	print "adj", adj
	# Normalize
	adj_n = normalize(adj)
	
	return adj_n


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
	
	# Use the equation 
	for row in adj:
		adj_norm_row = []
		
		for i in range(0, len(row)):
			adj_norm_row.append( (row[i] - min_val) / (max_val - min_val) )
		
		adj_norm.append(adj_norm_row)
	
	return adj_norm