'''
Purity measure

Given labels, sort into two lists
	zero = []
	one = []

Calculate percentage of winners/losers in zero
Calculate percentage of winners/losers in one
'''
def purity(labels, teams, results):
	print labels
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
	win = [zero_win_purity, zero_loss_purity] if zero_win_purity > one_win_purity else [one_win_purity, one_loss_purity]
	loss = [zero_win_purity, zero_loss_purity] if zero_win_purity < one_win_purity else [one_win_purity, one_loss_purity]
	
	# Display test results
	print "The winners cluster contained", win[0] * 100, "% wins and", win[1] * 100, "% losses"
	print "The losers cluster contained", loss[0] * 100, "% wins and", loss[1] * 100, "% losses"


def silhouette():
	pass
