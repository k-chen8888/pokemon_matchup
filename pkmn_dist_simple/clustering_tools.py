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

Return the label that indicates the cluster of winners
'''
def purity(k, labels, teams, results, sim_mtrx, out = None):
	f = None
	if out == None:
		pass
	else:
		# Store test results in file
		f = open(out, "w")
	
	all_clusters = []
	
	# The label of the cluster of winners (integer)
	win = -1
	max_cluster_win_purity = 0
	
	# The number k represents the number of unique labels
	# In scikit, this is [0, k - 1]
	for i in range(0, k):
		# Look for i in labels
		cluster = []
		cluster_res = []
		
		for j in range(0, len(labels)):
			# Process all data points labeled i
			if labels[j] == i:
				cluster.append( teams[j] )
				cluster_res.append( results[j] )
			else:
				pass
		
		all_clusters.append(cluster)
		
		# Calculate percentage of wins and losses in cluster
		cluster_wins = 0
		cluster_losses = 0
		
		for j in range(0, len(cluster)):
			if results[j] == True: # Winner
				cluster_wins += 1
			else:
				cluster_losses += 1
		
		# Purity for cluster
		cluster_win_purity = float(cluster_wins) / len(cluster) if len(cluster) > 0 else 0
		cluster_loss_purity = float(cluster_losses) / len(cluster) if len(cluster) > 0 else 0
		
		# Just in case
		if i == k - 1 and max_cluster_win_purity == 0:
			max = k
		
		# Check to see if this is the cluster of winners
		if cluster_win_purity > max_cluster_win_purity:
			max_cluster_win_purity = cluster_win_purity
			win = i
		
		report0 = "Cluster label " + str(i) + ", size " + str( len(cluster) ) + "\n"
		report1 = str(cluster_win_purity * 100) + "% wins and " + str(cluster_loss_purity * 100) + "% losses\n"
		
		# If there is an output file specified, use it
		if out == None:
			# Display test results
			print report0
			print report1
			print "\n\n"
			
		else:
			f.write( report0 )
			f.write( report1 )
			f.write("\n\n")
	
	# Compute and output silhouette coefficient
	for cluster1 in all_clusters:
		for cluster2 in all_clusters:
			if not cluster1 == cluster2:
				sil_report = "Silhouette Coefficient: " + str( silhouette(cluster1, cluster2, teams, sim_mtrx) )
				f.write( sil_report )
	
	# Close file
	f.close()
	
	print "Test done"
	return win

'''
Silhouette coefficient

Assume that the cluster to get the coefficient for is the first argument
Queries the distances out of the original similarity matrix 

a = Average distance between each point and points in the same cluster
b = Average distance between each point and points in a different cluster
Store a list of coefficients (b - a) / max(a, b)

Output the average of the list as the coefficent of the cluster
	Coefficients close to 1 are better
'''
def silhouette(cluster1, cluster2, teams, sim_mtrx):
	# Get a list of coefficients
	coefficients = []
	
	for team1 in cluster1:
		# Distance to points in same cluster
		a = sum( [ sim_mtrx[teams.index(team1)][teams.index(team2)] for team2 in cluster1 if not team1 == team2 ] ) / len(cluster1)
		
		# Distance to points in different cluster
		b = sum( [ sim_mtrx[teams.index(team1)][teams.index(team2)] for team2 in cluster2 ] ) / len(cluster2)
		
		coefficients.append( (b - a) / max(a, b) )
	
	# Output average of all coefficients to get cluster coefficient
	return sum( coefficients ) / len(coefficients)