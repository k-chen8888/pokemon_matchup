'''
Mock Battles

For each Pokemon on the team
	For each damaging move
		Test effectiveness against each opponent
		
		Use equation:
			Product of the following terms
				(2 * level + 10) / 250
				p1_a/p2_d
				Move base power
			Add 2
			Multiply the result of the above by a modifier
				Product of the following terms
					STAB: 1.5x if same type as user
					Type effectiveness (from table)
					Critical
						Do one with crit (1.5)
						Do one without crit (1)
					Other: Item bonuses, etc.
					Assume RNG generates a 1
			Round down, drop remainders
		
		0.5 points for each "victory"
			That is, +0.5 for winning with crit and +0.5 for winning without crit for a total of 6 possible points for each "match"
			Define "victory" as reducing the enemy's HP by more than 50%
	
	For each non-damaging move
		+1 point if user is faster than half of opponents
		+1 point for weather effect
		+1 point for entry hazard (hail, sandstorm counts)
		+1 point for status effect
		+1 point for healing
		+1 point for buffs/weakens
		
		Total of 6 points

At the end of the mock battle, each move gets a score from 1-6
	Store like so:
		move1_score: [ _, _, _, _, _, _ ]
			Each blank represents the "score" against the Pokemon in the corresponding slot
		move2_score: [ _, _, _, _, _, _ ]
		move3_score: [ _, _, _, _, _, _ ]
		move4_score: [ _, _, _, _, _, _ ]
		defense: [ [ _, _, _, _ ], [ _, _, _, _ ], [ _, _, _, _ ], [ _, _, _, _ ], [ _, _, _, _ ], [ _, _, _, _ ], ]
			Each sublist represents a corresponding attacking Pokemon on the opponent's side
			Each blank in the sublist represents the defensive score against a particular move used by attacking Pokemon
				Calculate this defensive score by subtracting the opponent's offensive score from 6

Output the squared distance between teams based on battle results

Note:
	For each Pokemon, get an attacking measure and a defending measure and get the distance between both of them
	To preserve symmetry, do this twice (call this function twice, with the arguments reversed the second time)
'''
import os, sys, re, math

# Query Pokemon from database to get information
from scrape_db_simple.pkmn_db_simple import *

'''
Conduct a mock battle between two Pokemon

Attacking Pokemon: team1
Defending Pokemon: team2
'''
def mock_battle(team1, team2):