# Distance measures and data evaluation
from mock_battle_simple import *
from pkmn_dist_simple import *

'''
Data analysis tools
'''
import numpy as np
from sklearn.cluster import spectral_clustering


'''
Purity measure

Given labels, sort into two lists
	zero = []
	one = []

Calculate percentage of winners/losers in zero
Calculate percentage of winners/losers in one
'''
def purity(k, labels, teams, results, sim_mtrx, out = None):
	f = None
	if out == None:
		pass
	else:
		# Store test results in file
		f = open(out, "w")
	
	# The number k represents the number of unique labels
	# In scikit, this is [0, k - 1]
	for i in range(0, k):
		# Look for i in labels
		cluster = []
		cluster_res = []
		
		for j in range(0, len(labels)):
			# Process all data points labeled i
			if labels[j] == i:
				cluster.append( teams[i] )
				cluster_res.append( results[i] )
					
			else:
				pass
		
		# Calculate percentage of wins and losses in cluster
		cluster_wins = 0
		cluster_losses = 0
		
		for i in range(0, len(cluster)):
			if results[i] == True: # Winner
				cluster_wins += 1
			else:
				cluster_losses += 1
		
		# Purity for cluster
		cluster_win_purity = float(cluster_wins) / len(cluster) if len(cluster) > 0 else 0
		cluster_loss_purity = float(cluster_losses) / len(cluster) if len(cluster) > 0 else 0
		
		# If there is an output file specified, use it
		if out == None:
			# Display test results
			print "Cluster label", i, ", size ", str( len(cluster) )
			print cluster_win_purity * 100, "% wins and", cluster_loss_purity * 100, "% losses"
			print "\n"
			
		else:
			f.write( "Cluster label " + str(i) + ", size " + str( len(cluster) ) )
			f.write( str(cluster_win_purity * 100) + "% wins and " + str(cluster_loss_purity * 100) + "% losses" )
			f.write("\n")
	
	# Close file
	f.close()
	
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