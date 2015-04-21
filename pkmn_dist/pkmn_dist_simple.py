'''
Various distance measures for determining how similar two teams are

Evaluate distance for two Pokemon in terms of...
	Base stat simimlarity (Euclidean distance on a 1x6 vector)
	Move similarity
		If the names match, declare the moves to be identical
		Otherwise, take the Euclidean distance on [Type, Category, Base Power, Accuracy, Priority]
		Average the similarity of each move with each other move
Sum all measures to get team distance
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
Define each Pokemon in the team as a dictionary
'''
def team_dist(team1, team2):
	# Pairwise distance between each Pokemon (assuming full teams of 6 Pokemon)
	return sum( [ sum( [ pkmn_dist(pkmn1, pkmn2) for pkmn1 in team1 ] ) for pkmn2 in team2 ] )

	
'''
Similarity between Pokemon
'''
def pkmn_dist(pkmn1, pkmn2):
	base_dist = sum( [ sum( [ (x - y) ** 2 for x in pkmn1['base'] ] ) for y in pkmn2['base'] ] ) ** 0.5
	
	# Query moves from database for each pokemon
	
	# Pairwise distance between each move, averaged (assuming 4 moves)
	move_dist = sum( [ ( sum( [ move_dist(move1, move2) for move1 in pkmn1['moves'] ] ) / 4.0 ) for move2 in pkmn2['moves'] ] ) ** 0.5
	
	# Output sum
	return base_dist + move_dist

	
'''
Similarity between moves
'''
def move_dist(move1, move2):
	pass