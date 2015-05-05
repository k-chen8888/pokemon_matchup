'''
Mock Battles

For each Pokemon on the team
	For each damaging move
		Test effectiveness against each opponent
		
		Use equation:
			Product of the following terms
				(2 * level + 10) / 250, assuming level 100, this is a constant 210/250 = 0.84
				p1_a/p2_d
				Move base power
			Add 2
			Multiply the result of the above by a modifier
				Product of the following terms
					STAB: 1.5x if same type as user
					Type effectiveness (from table)
					Critical
						Do one with critical (1.5)
						Do one without critical (1)
					Other: Item bonuses, etc.
					Assume RNG generates a 1
			Round down, drop remainders
		
		+1 point for each "victory"
			That is, +1 for winning with critical and +1 for winning without critical
			Define "victory" as reducing the enemy's HP by more than some percentage (different for slow and fast attackers)
		+1 point for higher priority or speed
		+1 point for hitting an opponent when they don't have a reduction item or Leftovers/Focus Sash and do not have the move Substitute
		+1 point for STAB
		+1 point for type advantage
		
		Total of 6 points
	
	For each non-damaging move
		+1 point if user is faster than opponent
		+1 point for weather effect
		+1 point for entry hazard (hail, sandstorm counts)
		+1 point for status effect
		+1 point for healing
		+1 point for buffs/weakens
		
		Total of 6 points

At the end of the mock battle, each move gets a score from 1-6
	Store like so for each Pokemon:
		move0_score: [ _, _, _, _, _, _ ]
			Each blank represents the "score" against the Pokemon in the corresponding slot
		move1_score: [ _, _, _, _, _, _ ]
		move2_score: [ _, _, _, _, _, _ ]
		move3_score: [ _, _, _, _, _, _ ]
		defense: [ [ _, _, _, _ ], [ _, _, _, _ ], [ _, _, _, _ ], [ _, _, _, _ ], [ _, _, _, _ ], [ _, _, _, _ ] ]
			Each sublist represents a corresponding attacking Pokemon on the opponent's side
			Each blank in the sublist represents the defensive score against a particular move used by attacking Pokemon
				Calculate this defensive score by subtracting the opponent's offensive score from 6
			Each opponent Pokemon has a defense list

Output the squared distance between teams based on battle results

Note:
	For each Pokemon, get an attacking measure and a defending measure and get the distance between both of them
	To preserve symmetry, perform the mock battle twice (with the arguments reversed the second time)
		This completes all lists for both teams
	Take the distance by comparing the lists like so:
		Squared Euclidean distance between the move arrays
'''
import os, sys, re, math, json

# Query Pokemon from database to get information
from scrape_db_simple.pkmn_db_simple import *


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
s_mock = Session()
'''


'''
A Hidden Power fix for digging up moves by name
'''
def get_move(move, session):
	if "Hidden Power" not in move:
		return session.query(Move).filter(Move.name == move).first()
	else:
		m = session.query(Move).filter(Move.name == "Hidden Power").first()
		
		# Adjust Hidden Power type
		if len(move) > len("Hidden Power"):
			m.move_type = hp_type.index(move)
		else:
			m.move_type = 0
		
		return m


'''
The percentage of HP that needs to be knocked off in order to declare "victory"
SLOW if the attacker is slower, FAST otherwise
'''
VICTORY_BOUND_SLOW = 0.75
VICTORY_BOUND_FAST = 0.55


'''
Dummy Pokemon to fill up space
'''
MAGIKARP = {}
MAGIKARP['name'] = 'Magikarp'
MAGIKARP['item'] = 'Soothe Bell'
MAGIKARP['moves'] = ['Splash', 'Splash', 'Splash', 'Splash']


'''
Conduct a mock battle between two Pokemon

Round 1
	Attacking Pokemon: team1
	Defending Pokemon: team2

Round 2
	Attacking Pokemon: team2
	Defending Pokemon: team1

Take distance and output
'''
def mock_battle(team1, team2):
	# Offence evaluation for team1
	# Defence evaluation for team2
	for opponent in team2:
		opponent['defense'] = []
	
	for pkmn in team1:
		# Make labels
		for i in range(0, len(pkmn['moves'])):
			label = 'move' + str(i) + '_score'
			pkmn[label] = []
		
		# Run the mock battle
		partial_mock(pkmn, team2)
	
	# Offence evaluation for team2
	# Defence evaluation for team1
	for opponent in team1:
		opponent['defense'] = []
	
	for pkmn in team2:
		# Make labels
		for i in range(0, len(pkmn['moves'])):
			label = 'move' + str(i) + '_score'
			pkmn[label] = []
		
		# Run the mock battle
		partial_mock(pkmn, team1)
	
	# Calculate the distances
	return mock_dist(team1, team2)


'''
Partial mock battle pitting a single Pokemon from one team against each Pokemon from the other team
'''
def partial_mock(pkmn, team):
	# Calculate for each opponent
	for opponent in team:
		# Use this array to store opponent's defensive scores for each move faced
		defend = []
		for i in range(0, len(pkmn['moves'])):
			move = pkmn['moves'][i]
			label = 'move' + str(i) + '_score'
			
			# Accumulator for score
			score = 0
			
			# Non-damaging move
			if move.move_cat == 2:
				score += 1 if move.priority > 0 or pkmn['stats'][5] > opponent['stats'][5] or ( pkmn['item'].name == "Quick Claw" and move.priority > 0 ) else 0
				score += 1 if move.weather == True else 0
				score += 1 if move.entry == True else 0
				score += 1 if move.status == True else 0
				score += 1 if move.heal == True else 0
				score += 1 if move.stat_change == True else 0
				
				pkmn[label].append(score)
				defend.append(6 - score)
			
			# Useless placeholder move; assume equality
			elif move.name == "Splash":
				pkmn[label].append(0)
				defend.append(6)
			
			# Damaging move
			else:
				# Special moves
				if move == "Fling":
					if pkmn['item'].name == "Soothe Bell": # Useless if dummy hold item
						pkmn[label].append(0)
						defend.append(6)
					
					else: # Normal calculations
						score = mock_calculate(pkmn, opponent, 1)
						
						pkmn[label].append(score)
						defend.append(6 - score)
				
				elif move == "Natural Gift":
					if pkmn['item'].name == "Soothe Bell": # Useless if dummy hold item
						pkmn[label].append(0)
						defend.append(6)
					
					else:
						if pkmn['item'].natural_gift_type == -1: # Useless if not berry
							pkmn[label].append(0)
							defend.append(6)
						
						else: # Normal calculations
							score = mock_calculate(pkmn, opponent, 2)
							
							pkmn[label].append(score)
							defend.append(6 - score)
				
				# Just any old damaging move
				else:
					score = mock_calculate(pkmn, move, opponent, 0)
			
					pkmn[label].append(score)
					defend.append(6 - score)
		
			#print pkmn[label]
		
		# Save aggregate defensive score against this Pokemon
		opponent['defense'].append( sum(defend) )


'''
Equation for calculating damaging moves, loaded into one convenient function

@pokemon = attacking Pokemon (dictionary of database objects)
@move = the move in question (database object)
@opponent = defending Pokemon (dictionary of database objects)
@special = (0, normal), (1, Fling), (2, Natural Gift)
'''
def mock_calculate(pokemon, move, opponent, special):
	score = 0
	
	# Pre-load all variables for damage equation
	pkmn = pokemon['pkmn']
	p_item = pokemon['item']
	opp = opponent['pkmn']
	o_item = opponent['item']
	
	# Does the opponent have Substitute?
	opp_sub = False
	for move in opponent['moves']:
		if move.name == "Substitute":
			opp_sub = True
	
	# Move power
	move_power = 0
	if special == 1: # Fling
		move_power = p_item.fling_dmg
	elif special == 2: # Natural Gift
		move_power = p_item.natural_gift_power
	else:
		move_power = move.base_power
	
	# Attack/Defense ratio, based off of move category
	atk = pkmn['stats'][1] if move.move_cat == 0 else pkmn['stats'][3]
	de = opp['stats'][2] if move.move_cat == 0 else opp['stats'][4]
	atk_de_ratio = float(atk) / float(de)
	
	# Modifier
	stab = 1.5 if move.move_type == pkmn.type1 or move.move_type == pkmn.type2 else 1 # Same-type attack bonus
	type_eff = typing[move.move_type][opp.type1] if opp.type2 == -1 else typing[move.move_type][opp.type1] * typing[pkmn.type1][opp.type2] # Type effectiveness
	reduce = 1.0
	if o_item:
		reduce = 0.5 if o_item.name in se_reduce and move.move_type == o_item.natural_gift_type else 1.0 # 50% reduction from super-effective reducing Berry, if any
	
	# Calculate damage-based score
	if not opp_sub:
		no_crit = (0.84 * atk_de_ratio * move_power + 2) * stab * type_eff * reduce
		crit = (0.84 * atk_de_ratio * move_power + 2) * stab * type_eff * reduce * 1.5
		
		# Add percentage of health taken away to score
		score += min( no_crit / opp['stats'][0], 1.0 ) * 3
		score += min( crit / opp['stats'][0], 1.0 ) * 3
	
	else: # Very often going to be only 25% of health in damage
		score += 0.25 * 6
	
	return score


'''	
Calculate the squared distance between two teams based on mock battle results
Larger distance -> greater strength difference
'''
def mock_dist(team1, team2):
	# For each Pokemon on team1, sum up scores
	team1_scores = []
	for pkmn1 in team1:
		team1_scores.append( sum(pkmn1['move0_score']) )
		team1_scores.append( sum(pkmn1['move1_score']) )
		team1_scores.append( sum(pkmn1['move2_score']) )
		team1_scores.append( sum(pkmn1['move3_score']) )
		team1_scores.append( sum(pkmn1['defense']) )
		#team1_scores.append( sum( [ sum( pkmn1['defense'][i] ) for i in range(0, len(pkmn1['defense'])) ] ) )
	
	# For each Pokemon on team2, sum up scores
	team2_scores = []
	for pkmn2 in team2:
		team2_scores.append( sum(pkmn2['move0_score']) )
		team2_scores.append( sum(pkmn2['move1_score']) )
		team2_scores.append( sum(pkmn2['move2_score']) )
		team2_scores.append( sum(pkmn2['move3_score']) )
		team2_scores.append( sum(pkmn2['defense']) )
		#team2_scores.append( sum( [ sum( pkmn2['defense'][i] ) for i in range(0, len(pkmn2['defense'])) ] ) )
	
	# Find square difference and output it
	diff = []
	for i in range(0, len(team1_scores)):
		diff.append( ( team1_scores[i] - team2_scores[i] ) ** 2 )
	
	return sum( diff )


'''
Stops the database session for mock battles
'''
def stop_mock():
	s_mock.close()