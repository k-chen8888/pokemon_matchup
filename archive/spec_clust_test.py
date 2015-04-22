import sys

import numpy as np
from sklearn.cluster import spectral_clustering

s = []
s.append([1, 2, 3]) # 0
s.append([2, 3, 4]) # 0
s.append([2, 4, 7]) # 1
s.append([1, 5, 4]) # 1
s.append([7, 9, 3]) # 0
s.append([8, 3, 4]) # 1
s.append([8, 3, 4]) # 0
s.append([2, 4, 7]) # 0
s.append([8, 3, 4]) # 0
s.append([7, 9, 3]) # 1
s.append([8, 3, 4]) # 0
s.append([1, 5, 4]) # 0

# Similarity of all pairs of points
def similarity(data):
	sim_array = []
	
	# First instance to compare
	for instance1 in data:
		sim_row = []
		
		# Second instance to compare
		for instance2 in data:
			sim_row.append( distance(instance1, instance2) )
		
		sim_array.append( sim_row )
	
	sim_array = normalize(sim_array)

	return sim_array

# Distance between two points
def distance(i1, i2):
	return sum( [ (i1[i] - i2[i]) ** 2 for i in range(0, len(i1)) ] ) ** 0.5 

# Normalize the data using (x - min) / (max - min)
def normalize(old_array):
	min_val = sys.maxint
	max_val = 0
	
	for instance in old_array:
		for value in instance:
			if value < min_val:
				min_val = value
			if value > max_val:
				max_val = value
	
	for instance in old_array:
		for i in range(0, len(instance)):
			instance[i] = (instance[i] - min_val) / (max_val - min_val)
	
	return old_array

if __name__ == '__main__':
	sa = similarity(s)
	
	print "Adjacency matrix"
	for row in sa:
		print row
	
	print "Labels"
	for k in range(2, 5):
		labels = spectral_clustering(np.asarray(sa), n_clusters = k, eigen_solver = 'arpack', assign_labels = 'discretize')
		print labels
