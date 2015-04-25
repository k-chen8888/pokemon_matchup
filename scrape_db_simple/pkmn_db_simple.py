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


# Use this to look up the type granted to Arceus by its hold item
# Key = type
plate_types = {}
plate_types['dragon'] = 'Draco Plate'
plate_types['dark'] = 'Dread Plate'
plate_types['ground'] = 'Earth Plate'
plate_types['fighting'] = 'Fist Plate'
plate_types['fire'] = 'Flame Plate'
plate_types['ice'] = 'Icicle Plate'
plate_types['bug'] = 'Insect Plate'
plate_types['steel'] = 'Iron Plate'
plate_types['grass'] = 'Meadow Plate'
plate_types['psychic'] = 'Mind Plate'
plate_types['fairy'] = 'Pixie Plate'
plate_types['flying'] = 'Sky Plate'
plate_types['water'] = 'Splash Plate'
plate_types['ghost'] = 'Spooky Plate'
plate_types['rock'] = 'Stone Plate'
plate_types['poison'] = 'Toxic Plate'
plate_types['electric'] = 'Zap Plate'


# Use this to look up the type granted to Techno Blast
# Key = hold item
techno_blast = {}
techno_blast["Shock Drive"] = 'electric'
techno_blast["Burn Drive"] = 'fire'
techno_blast["Chill Drive"] = 'ice'
techno_blast["Douse Drive"] = 'water'


# Use this to look up move categories
# Save category in database as array index
move_cats = ['physical', 'special', 'other']


# Use this to look up the special conditions for 'Other'
# Saved as regex components
other = {}
other['weather'] = [' rain ', 'sandstorm', 'hail', 'sunny']
other['entry'] = ['trap']
other['status'] = ['burn ', 'paralysis', 'poison ', 'confuse', 'confusion', 'sleep', 'freeze', 'protect', 'evade all']
other['heal'] = ['cure', 'restore', 'regains']
other['stat_change'] = ['ups', 'raise', 'raising', 'boost', 'reduce', ' lower']


# Berries that reduce damage dealt by super-effective moves by 50%
se_reduce = []
se_reduce.append("Occa Berry") # Fire
se_reduce.append("Passho Berry") # Water
se_reduce.append("Wacan Berry") # Electric
se_reduce.append("Rindo Berry") # Grass
se_reduce.append("Yache Berry") # Ice
se_reduce.append("Chople Berry") # Fighting
se_reduce.append("Kebia Berry") # Poison
se_reduce.append("Shuca Berry") # Ground
se_reduce.append("Coba Berry") # Flying
se_reduce.append("Payapa Berry") # Psychic
se_reduce.append("Tanga Berry") # Bug
se_reduce.append("Charti Berry") # Rock
se_reduce.append("Kasib Berry") # Ghost
se_reduce.append("Haban Berry") # Dragon
se_reduce.append("Colbur Berry") # Dark
se_reduce.append("Babiri Berry") # Steel
se_reduce.append("Chilan Berry") # Normal, any move
se_reduce.append("Roseli Berry") # Fairy


# Mapping for all Hidden Power Types
# Corresponds to type locations in pkmn_types
# Note: No Normal or Fairy Hidden Power
hp_type = ["", "Hidden Power Fire", "Hidden Power Water", "Hidden Power Electric", "Hidden Power Grass", "Hidden Power Ice", "Hidden Power Fighting", "Hidden Power Poison", "Hidden Power Ground", "Hidden Power Flying", "Hidden Power Psychic", "Hidden Power Bug", "Hidden Power Rock", "Hidden Power Ghost", "Hidden Power Dragon", "Hidden Power Dark", "Hidden Power Steel"]


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
engine = create_engine('sqlite:///pkmn_db_simple.db', echo = True)
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
	type2 = Column(Integer, default = -1)
	
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
	possible_moves = relationship('Move', secondary = moveset, backref='pokemon')
	possible_abilities = relationship('Ability', secondary = abilityset, backref='pokemon')
	
	
	# Add Pokemon to database
	# Takes a dictionary that represents a Pokemon
	def __init__(self, stats):
		self.name = stats['name']
		self.dex_id = stats['id']
		
		# Populate types
		self.type1 = pkmn_types.index( stats['type'][0] )
		if len(stats['type']) > 1:
			self.type2 = pkmn_types.index( stats['type'][1] )
		
		# Populate base stats
		self.base_hp = stats['base'][0]
		self.base_atk = stats['base'][1]
		self.base_def = stats['base'][2]
		self.base_spatk = stats['base'][3]
		self.base_spdef = stats['base'][4]
		self.base_spd = stats['base'][5]
		
		# Is this Pokemon a Mega-Evolution?
		self.mega = stats['mega']

		
'''
All possible moves
'''
class Move(Base):
	__tablename__ = 'move'
	
	
	id = Column(Integer, primary_key = True)
	
	name = Column(String(20), nullable = False)
	move_type = Column(Integer, nullable = False)
	move_cat = Column(Integer, nullable = False)
	base_power = Column(Integer, nullable = False)
	
	# The higher the speed priority, the faster it is; 0 means read from SPD staticmethod
	priority = Column(Integer, nullable = False)
	
	# Accuracy rating
	accuracy = Column(Integer, nullable = False)
	
	# Special parameters for 'Other' moves
	weather = Column(Boolean, default = False)
	entry = Column(Boolean, default = False)
	status = Column(Boolean, default = False)
	heal = Column(Boolean, default = False)
	stat_change = Column(Boolean, default = False)
	
	# Add move to database
	# Takes a dictionary that represents a move
	def __init__(self, stats):
		self.name = stats['name']
		self.move_type = stats['move_type']
		self.move_cat = stats['move_cat']
		self.base_power = stats['base_power']
		self.priority = stats['priority']
		self.accuracy = stats['accuracy']
		
		# 'Other' only
		if stats['move_cat'] == 2:
			self.weather = stats['weather']
			self.entry = stats['entry']
			self.status = stats['status']
			self.heal = stats['heal']
			self.stat_change = stats['stat_change']


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
	
	# Berries only
	# -1 in all numerical fields indicates that this is not a berry
	natural_gift_type = Column(Integer, default = -1) # Note that this type is the same as the type of the super-effective move that is blocked
	natural_gift_power = Column(Integer, default = -1) # Amount of damage done by natural gift
	se_dmg_down = Column(Boolean, default = -1) # Damage reduction from super-effective move, 0 if none and 1 if 50%
	
	# Pokemon holding this item
	# Parent in relationship
	held_by = relationship("TrainedPokemon")
	
	
	# Add hold item to database
	# Takes a dictionary that represents a hold item
	def __init__(self, stats):
		self.name = stats['name']
		self.fling_dmg = stats['fling']
		self.mega_stone = stats['mega_stone']
		self.natural_gift_type = stats['natural_gift_type']
		self.natural_gift_power = stats['natural_gift_power']
		
		# Check list
		if stats['name'] in se_reduce:
			self.se_dmg_down = 1
		else:
			self.se_dmg_down = 0


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
	
	
	# Add ability to database
	# Takes a dictionary that represents an ability
	def __init__(self, stats):
		self.name = stats['name']


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
