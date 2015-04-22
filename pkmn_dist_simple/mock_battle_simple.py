'''
Mock Battles

For each Pokemon
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
	
	For each non-damaging move
		+1 point if user is faster than half of opponents
		+1 point for weather effect
		+1 point for entry hazard (hail, sandstorm counts)
		+1 point for status effect
		+1 point for healing
		+1 point for buffs/weakens

At the end of the mock battle, each move gets a score from 1-6
'''
