'''
Simplified version of the database
'''


# Utilities
import os, sys

# SQLAlchemy
from sqlalchemy import create_engine, Table, Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.sql import exists


'''
Useful constants
'''
# Use this to look up types
# Save types in database as array index
pkmn_types = ['normal', 'fire', 'water', 'electric', 'grass', 'ice',
			  'fighting', 'poison', 'ground', 'flying', 'psychic', 'bug',
			  'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy']


# Table of damage multipliers for type matchups (indices match the pkmn_types array)
#	Row: Attacking type
# 	Column: Defending type
# 	Entry: Damage multiplier
# Recorded as a decimal
# For dual types, multiply values when they are looked up
typing = [[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.0, 1.0, 1.0, 0.5, 1.0], # Normal
		  [1.0, 0.5, 0.5, 1.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 0.5, 1.0, 0.5, 1.0, 2.0, 1.0], # Fire
		  [1.0, 2.0, 0.5, 1.0, 0.5, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.5, 1.0, 1.0, 1.0], # Water
		  [1.0, 1.0, 2.0, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 2.0, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0], # Electric
		  [1.0, 0.5, 2.0, 1.0, 0.5, 1.0, 1.0, 0.5, 2.0, 0.5, 1.0, 0.5, 2.0, 1.0, 0.5, 1.0, 0.5, 1.0], # Grass
		  [1.0, 0.5, 0.5, 1.0, 2.0, 0.5, 1.0, 1.0, 2.0, 2.0, 1.0, 1.0, 1.0, 0.0, 2.0, 1.0, 0.5, 1.0], # Ice
		  [2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.5, 1.0, 0.5, 0.5, 0.5, 2.0, 0.0, 1.0, 2.0, 2.0, 1.0], # Fighting
		  [1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 0.5, 0.5, 1.0, 1.0, 1.0, 0.5, 0.5, 1.0, 1.0, 0.0, 2.0], # Poison
		  [1.0, 2.0, 1.0, 2.0, 0.5, 2.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.5, 2.0, 1.0, 1.0, 1.0, 2.0, 1.0], # Ground
		  [1.0, 1.0, 1.0, 0.5, 2.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 0.5, 1.0, 1.0, 1.0, 0.5, 1.0], # Flying
		  [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 0.0, 0.5, 1.0], # Psychic
		  [1.0, 0.5, 1.0, 1.0, 2.0, 1.0, 1.0, 0.5, 0.5, 0.5, 2.0, 1.0, 1.0, 0.5, 1.0, 1.0, 0.5, 1.0], # Bug
		  [1.0, 2.0, 1.0, 1.0, 1.0, 2.0, 0.5, 1.0, 0.5, 2.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0], # Rock
		  [0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 2.0, 1.0, 0.5, 1.0, 1.0], # Ghost
		  [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.5, 0.0], # Dragon
		  [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 2.0, 1.0, 0.5, 1.0, 0.5], # Dark
		  [1.0, 0.5, 0.5, 0.5, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 0.5, 2.0], # Steel
		  [1.0, 0.5, 1.0, 1.0, 1.0, 2.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 0.5, 1.0], # Fairy
		  ]


# Use this to look up format for battle
# Save types in database as array index
formats = ['NU', 'UU', 'OU', 'Uber', 'Smogon']


'''
Make a database in the cwd if it doesn't already exist
Engine is used to store data in database in local directory
'''
engine = create_engine('sqlite:///C:\\Users\\ScionOfTheVoid\\Documents\\GitHub\\pokemon_matchup\\pkmn_db.db', echo = True)
Base = declarative_base()


'''
All moves learnable by a Pokemon
'''
moveset = Table('moveset', Base.metadata,
	Column('move_id', Integer, ForeignKey('move.id')),
	Column('pokemon_id', Integer, ForeignKey('pokemon.id'))
)

'''
All abilities a pokemon may have
'''
abilityset = Table('abilityset', Base.metadata,
	Column('ability_id', Integer, ForeignKey('ability.id')),
	Column('pokemon_id', Integer, ForeignKey('pokemon.id')),
	Column('mega_only', Boolean, default = False) # This ability is only available if the Pokemon is holding a Mega Stone
)

'''
Moves learned by a Pokemon
'''
learned_moves = Table('learned_moves', Base.metadata,
	Column('move_id', Integer, ForeignKey('move.id')),
	Column('pokemon_id', Integer, ForeignKey('trained_pokemon.id')),
	Column('slot', Integer) # Position in move list
)

'''
Pokemon teams
'''
team_roster = Table('team_roster', Base.metadata,
	Column('team_id', Integer, ForeignKey('team.id')),
	Column('pokemon_id', Integer, ForeignKey('trained_pokemon.id')),
	Column('slot', Integer) # Position in party
)


'''
All possible Pokemon
'''
class Pokemon(Base):
	__tablename__ = 'pokemon'
	
	
	id = Column(Integer, primary_key = True)
	
	# Pokemon name and PokeDex ID
	name = Column(String(12), nullable = False)
	dex_id = Column(Integer, nullable = False)
	
	# Pokemon type (up to 2)
	type1 = Column(Integer, nullable = False)
	type2 = Column(Integer)
	
	# Base stats
	base_hp = Column(Integer, nullable = False)
	base_atk = Column(Integer, nullable = False)
	base_def = Column(Integer, nullable = False)
	base_spatk = Column(Integer, nullable = False)
	base_spdef = Column(Integer, nullable = False)
	base_spd = Column(Integer, nullable = False)
	
	# Is this Pokemon a Mega-Evolution?
	mega = Column(Boolean, default = False)
	
	# Move pool and ability pool(many to many)
	possible_moves = relationship("Move", secondary = moveset)
	possible_abilities = relationship("Ability", secondary = abilityset)
	
	
	# Add Pokemon to database
	# Takes a dictionary that represents a Pokemon
	def __init__(self, stats):
		self.name = stats['name']
		
		# Populate types
		self.type1 = stats['type'][0]
		if len(stats['type']) > 1:
			self.type2 = stats['type'][1]
		
		# Populate base stats
		self.base_hp = stats['base'][0]
		self.base_atk = stats['base'][1]
		self.base_def = stats['base'][2]
		self.base_spatk = stats['base'][3]
		self.base_spdef = stats['base'][4]
		self.base_spd = stats['base'][5]
		
		# Can this Pokemon Mega-Evolve?
		self.can_mega = stats['can_mega']

'''
All possible moves
'''
class Move(Base):
	__tablename__ = 'move'
	
	
	id = Column(Integer, primary_key = True)
	
	name = Column(String(20), nullable = False)
	type = Column(Integer, nullable = False)
	base_power = Column(Integer, nullable = False)
	
	# The higher the speed priority, the faster it is; 0 means read from SPD staticmethod
	priority = Column(Integer, nullable = False)
		
	# Accuracy rating
	accuracy = Column(Integer, nullable = False)
	
	# Add move to database
	# Takes a dictionary that represents a move
	def __init__(self, stats):
		self.name = stats['name']
		self.type = stats['type']
		self.base_power = stats['base_power']


'''
All hold items
'''
class HoldItem(Base):
	__tablename__ = 'hold_item'
	
	
	id = Column(Integer, primary_key = True)
	
	name = Column(String(20), nullable = False)
		
	# How much fling damage does it do?
	fling_dmg = Column(Integer, nullable = False)
	
	# Is this a Mega Stone?
	mega_stone = Column(Boolean, default = False)
	
	# Pokemon holding this item
	# Parent in relationship
	held_by = relationship("TrainedPokemon")


'''
All abilities that a Pokemon can have
'''
class Ability(Base):
	__tablename__ = 'ability'
	
	
	id = Column(Integer, primary_key = True)
	
	name = Column(String(20), nullable = False)
	
	# Pokemon with this ability
	# Parent in relationship
	has_ability = relationship("TrainedPokemon")


'''
A Pokemon raised by a player
'''
class TrainedPokemon(Base):
	__tablename__ = 'trained_pokemon'
	
	
	id = Column(Integer, primary_key = True)
	
	# Base Pokemon
	# Child in relationship
	orig_pokemon = Column(Integer, ForeignKey('pokemon.id'))
	
	# The moves that the Pokemon knows
	movelist = relationship("Move", secondary = learned_moves)
	
	# Ability
	ability = Column(Integer, ForeignKey('ability.id'))
	
	# Mega-Evolution?
	mega = Column(Boolean, default = False)
	
	# Optional nickname
	nick = Column(String(12))
	
	# Level (assume 100 if not given)
	level = Column(Integer, default = 100)
	
	# Hold item
	hold = Column(Integer, ForeignKey('hold_item.id'))


'''
A match consists of 2 teams, with one winner
'''
matchup = Table("match", Base.metadata,
    Column("team_one_id", Integer, ForeignKey("team.id"), primary_key = True),
    Column("team_two_id", Integer, ForeignKey("team.id"), primary_key = True),
	Column("winner", Boolean, nullable = False), # Who won the match? True for team1, False otherwise
)


'''
A team consists of 6 Pokemon
'''
class Team(Base):
	__tablename__ = 'team'
	
	
	id = Column(Integer, primary_key = True)
	
	# Player name
	owner = Column(String(64), nullable = False, default = "Player")
	
	# Pokemon on the team
	roster = relationship("TrainedPokemon", secondary = team_roster)
	
	# Follows the rules of the format (only one Mega, not using banned/infeasible Pokemon or moves, etc.)
	legal = Column(Boolean, nullable = False)
	
	# Matches are a self-referential relationship between teams
	match = relationship("Team",
						 secondary = matchup,
						 primaryjoin = id == matchup.c.team_one_id,
						 secondaryjoin = id == matchup.c.team_two_id
	)


# Creates all tables (if they aren't already there)
Base.metadata.create_all(engine)