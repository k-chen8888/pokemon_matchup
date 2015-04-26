import parserV2
import json
from copy import deepcopy

def battleData(filename):
	file = open(filename, 'r')
	battles = []
	for battle in file:
		#print battle
		match = parserV2.parse(battle)
		battles.append(deepcopy(match))
	
	file.close()
	son = json.dumps(battles, sort_keys=True, indent = 2)
	
	file = open("battleData.txt", 'w')
	file.write(son)
	file.close()

battleData('test.txt')
