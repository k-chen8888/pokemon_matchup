# Distance measures and data evaluation
from mock_battle_simple import *
from pkmn_dist_simple import *


'''
Purity measure

Given labels, sort into two lists
	zero = []
	one = []

Calculate percentage of winners/losers in zero
Calculate percentage of winners/losers in one
'''
def purity(labels, teams, results, sim_mtrx, out = None):
	zero = []
	one = []
	
	# Sort by cluster
	for i in range(0, len(labels)):
		if labels[i] == 0:
			zero.append(teams[i])
		else:
			one.append(teams[i])
	
	# Calculate percentage of wins and losses in 0 list
	zero_wins = 0
	zero_losses = 0
	
	for team in zero:
		if results[teams.index(team)] == True: # Winner
			zero_wins += 1
		else:
			zero_losses += 1
	
	# Purity for zero array
	zero_win_purity = float(zero_wins) / len(zero) if len(zero) > 0 else 0
	zero_loss_purity = float(zero_losses) / len(zero) if len(zero) > 0 else 0
	
	# Calculate percentage of wins and losses in 1 list
	one_wins = 0
	one_losses = 0
	
	for team in one:
		if results[teams.index(team)] == True: # Winner
			one_wins += 1
		else:
			one_losses += 1
	
	# Purity for one array
	one_win_purity = float(one_wins) / len(one) if len(one) > 0 else 0
	one_loss_purity = float(one_losses) / len(one) if len(one) > 0 else 0
	
	# Which cluster had more winners?
	# Store purity values and silhouette coefficients
	win = [zero_win_purity, zero_loss_purity, silhouette(zero, one, teams, sim_mtrx)] if zero_win_purity > one_win_purity else [one_win_purity, one_loss_purity, silhouette(one, zero, teams, sim_mtrx)]
	loss = [zero_win_purity, zero_loss_purity, silhouette(zero, one, teams, sim_mtrx)] if zero_win_purity < one_win_purity else [one_win_purity, one_loss_purity, silhouette(one, zero, teams, sim_mtrx)]
	
	# If there is an output file specified, use it
	if out == None:
		# Display test results
		print "The winners cluster contained", win[0] * 100, "% wins and", win[1] * 100, "% losses. The silhouette coefficient for this cluster is", win[2]
		print "The losers cluster contained", loss[0] * 100, "% wins and", loss[1] * 100, "% losses. The silhouette coefficient for this cluster is", loss[2]
	else:
		# Store test results in file
		f = open(out, "w")
		f.write("The winners cluster contained " + str( win[0] * 100 ) "% wins and " + str( win[1] * 100 ) "% losses. The silhouette coefficient for this cluster is " + str( win[2] ) + "\n")
		f.write("The losers cluster contained " + str( loss[0] * 100 ) "% wins and " + str( loss[1] * 100 ) "% losses. The silhouette coefficient for this cluster is " + str( loss[2] ) + "\n")
	
	print "Test done"

'''
Silhouette coefficient

Assume that the cluster to get the coefficient for is the first argument
Queries the distances out of the original similarity matrix 

a = Average distance between each point and points in the same cluster
b = Average distance between each point and points in a different cluster
Store a list of coefficients 1 - a / b

Output the average of the list as the coefficent of the cluster
	Coefficients close to 1 are better
'''
def silhouette(winners, losers, teams, sim_mtrx):
	# Get a list of coefficients
	coefficients = []
	
	for team1 in winners:
		# Distance to points in same cluster
		#a = sum( [ team_dist(team1, team2) for team2 in winners if not team1 == team2 ] ) / len(winners)
		a = sum( [ sim_mtrx[teams.index(team1)][teams.index(team2)] for team2 in winners if not team1 == team2 ] ) / len(winners)
		
		# Distance to points in different cluster
		#b = sum( [ team_dist(team1, team2) for team2 in losers ] ) / len(losers)
		b = sum( [ sim_mtrx[teams.index(team1)][teams.index(team2)] for team2 in losers ] ) / len(losers)
		
		coefficients.append(1 - a / b)
	
	# Output average of all coefficients to get cluster coefficient
	return sum( coefficients ) / len(coefficients)