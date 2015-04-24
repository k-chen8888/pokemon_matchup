import battleParser
import json

def battleData(filename):
	file = open(filename, 'r')
	battles = []
	for battle in file:
		#print battle
		match = battleParser.parse(battle)
		battles.append(match)
	
	file.close()
	son = json.dumps(battles, sort_keys=True, indent = 2)
	
	file = open("battleData.txt", 'w')
	file.write(son)
	file.close()
	