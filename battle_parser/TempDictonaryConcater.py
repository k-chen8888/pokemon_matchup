# Battle{
	# Player1 :
		# Name: 
		# Pokemon1 : {
			# Item : 
			# Ability : 
				# Move1 : 
				# Move2 :
				# Move3 :
				# Move4 :
			# Status :
				# brn :
				# par :
				# slp :
				# frz :
				# psn :
				# tox :
				# confusion :
				# trapped :
			# critical : 
			# # }
		
		# Pokemon2 : 
	# Player2 :
	# Winner : 0/1
	# Tier : 
	# Weather :
		# RainDance :
		# PrimordialSea :
		# SunnyDay :
		# DesolateLand :
		# Sandstorm :
		# Hail :
		# DeltaStream : 
		# none : 	
# }

#Idea Code for building the Player

'''For each player, build their dictionary
	filling in their name, the entry hazards they used
	the pokemon they used and the number of heals they did'''
player = {}
player["name"] = pi.name #str
player["hazards"] = pi.hazards #dict
player["heals"] = pi.heals #int

i = 1
'''for each pokemon the player has, 
	create a dictionary with the pokemon's information, 
	then pass that dictionary to the player dictionary'''
for k,v in pokemon :
	poke = {}
	poke["name"] = pokemon[k].name #str
	poke["item"] = pokemon[k].item #str
	poke["ability"] = pokemon[k].ability #str
	poke["moves"] = pokemon[k].move #this is a list
	poke["status"] = pokemon[k].status #this is a dict
	poke["critical"] = pokemon[k].crit #int
	player["pokemon"+str(i)] = poke
	i += 1

