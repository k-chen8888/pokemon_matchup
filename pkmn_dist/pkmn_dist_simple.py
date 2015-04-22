'''
Various distance measures for determining how similar two teams are

Evaluate distance for two Pokemon in terms of...
	Type similarity... it is safe to assume that...
		1. If two Pokemon have the same type, their type distance is 0
		2. If two Pokemon have different types, then type advantages determine similarity (compute two type advantage rows and take the Euclidean distance)
	
	Base stat simimlarity (Euclidean distance on a 1x6 vector)
	
	Move similarity
		If the names match, declare the moves to be identical
		Otherwise, take the Euclidean distance on [Type, Category, Base Power, Accuracy, Priority]
		Average the similarity of each move with each other move
	
Perform the measure with each possible pairing of Pokemon and output the average
'''
import os, sys, re, math

# Query Pokemon from database to get information
from pkmn_db_simple import *


'''
Load database
'''

# Need to start up a database session first
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Session = sessionmaker()
engine = create_engine('sqlite:///pkmn_db_simple.db', echo = True)
Session.configure(bind=engine)

# Work with this one
s = Session()


'''
Similarity between teams
 
Define a team as a list of Pokemon
'''
def team_dist(team1, team2):
	# Average pairwise Euclidean distances between each Pokemon (assuming full teams of 6 Pokemon, there are 36 calculations made)
	return sum( [ sum( [ pkmn_dist(pkmn1, pkmn2) for pkmn1 in team1 ] ) for pkmn2 in team2 ] ) / 36


'''
Similarity between Pokemon

Define each Pokemon in the team as a dictionary
	'name' -> String, Pokemon official name
	'moves' -> List of moves
'''
def pkmn_dist(pkmn1, pkmn2):
	# Query each Pokemon from the database
	p1 = s.query(Pokemon).filter(Pokemon.name == pkmn1['name']).first()
	p2 = s.query(Pokemon).filter(Pokemon.name == pkmn2['name']).first()
	
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
		type_dist = sum( [ sum( [ (x - y) ** 2 for x in adv_table_p1 ] ) for y in adv_table_p2 ] )
	
	# Distance between base stats
	pkmn1['base'] = [ p1.base_hp, p1.base_atk, p1.base_def, p1.base_spatk, p1.base_spdef, p1.base_spd ]
	pkmn2['base'] = [ p2.base_hp, p2.base_atk, p2.base_def, p2.base_spatk, p2.base_spdef, p2.base_spd ]
	base_dist = sum( [ sum( [ (x - y) ** 2 for x in pkmn1['base'] ] ) for y in pkmn2['base'] ] )
	
	# Pairwise distance between each move, averaged (assuming 4 moves)
	move_dist = sum( [ ( sum( [ move_dist(move1, move2) for move1 in pkmn1['moves'] ] ) / 4.0 ) for move2 in pkmn2['moves'] ] )
	
	# Output sum, taking the square root
	return ( type_dist + base_dist + move_dist ) ** 0.5


'''
Similarity between moves
Moves given by name only and queried
'''
def move_dist(move1, move2):
	if move1 == move2:
		return 0 # No distance if they're the same
	
	else:
		m1 = s.query(Move).filter(Move.name == move1).first()
		m2 = s.query(Move).filter(Move.name == move2).first()
		
		# Take the Euclidean distance
		sq_dist = 0
		
		sq_dist += (m1.move_type - m2.move_type) ** 2 # Type
		sq_dist += (m1.move_cat - m2.move_cat) ** 2 # Category
		sq_dist += (m1.base_power - m2.base_power) ** 2 # Base Power
		sq_dist += (m1.priority - m2.priority) ** 2 # Accuracy
		sq_dist += (m1.accuracy - m2.accuracy) ** 2 # Priority
		
		# Output sum
		return sq_dist