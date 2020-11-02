import csv
import json
import random
import statistics
import urllib.request

votes = {}
states = []
probs = {}
purl = 'https://www.predictit.org/api/marketdata/all/'
with open('electoralvotes.csv') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        states.append(row[0])
        votes[row[0]] = int(row[1])

with urllib.request.urlopen(purl) as response:
    r = response.read()
bets = json.loads(r)
for m in bets['markets']:
    for state in states:
        if 'Which party will win ' + state in m['name']:
            dem = 0
            rep = 0
            for c in m['contracts']:
                if c['name'] == 'Democratic':
                    dem = c['lastTradePrice']
                elif c['name'] == 'Republican':
                    rep = c['lastTradePrice']
            prob = dem / (dem+rep)
            probs[state] = prob

for state in states:
    print("%20s, %2d votes, %5.2f%% Biden, %5.2f%% Trump"%(state, votes[state], 100*probs[state], 100*(1-probs[state])))



def simulate(seed, epochs):
    trump_votes = []
    biden_votes = []
    random.seed(seed)
    for e in range(epochs):
        biden = 0
        trump = 0
        for state in states:
            if probs[state] > random.random():
                biden += votes[state]
            else:
                trump += votes[state]
        biden_votes.append(biden)
        trump_votes.append(trump)
        # print("Biden: %d, Trump: %d"%(biden, trump))
    return biden_votes, trump_votes
    

"""
biden_best = 0
biden_seed = 0
trump_best = 0
trump_seed = 0
for seed in range(10000):
    biden_votes, trump_votes = simulate(seed, n)
    biden_wins = sum(map(lambda x: x[0] > x[1], zip(biden_votes, trump_votes)))
    trump_wins = sum(map(lambda x: x[0] < x[1], zip(biden_votes, trump_votes)))
    if biden_wins > biden_best:
        biden_best = biden_wins
        biden_seed = seed
        print ("Biden: %f %d"% (biden_wins/n, seed))
    if trump_wins > trump_best:
        trump_best = trump_wins
        trump_seed = seed
        print ("Trump: %f %d"% (trump_wins/n, seed))
"""
n = 100000

biden_votes, trump_votes = simulate(0, n)
    

biden_wins = sum(map(lambda x: x[0] > x[1], zip(biden_votes, trump_votes)))
trump_wins = sum(map(lambda x: x[0] < x[1], zip(biden_votes, trump_votes)))
tie = sum(map(lambda x: x[0] == x[1], zip(biden_votes, trump_votes)))
biden_mean = statistics.mean(biden_votes)
trump_mean = statistics.mean(trump_votes)
biden_med = statistics.median(biden_votes)
trump_med = statistics.median(trump_votes)


print()
print("%d Simulations"%n)
print("Counts: Biden: %d, Trump: %d, Ties: %d"%(biden_wins, trump_wins, tie))
print("Probs:  Biden: %.2f%%, Trump: %.2f%%, Ties: %.2f%%"%(biden_wins*100.0/n, trump_wins*100.0/n, tie*100./n))
print("Avg:    Biden: %f, Trump: %f"%(biden_mean, trump_mean))
print("Median: Biden: %d, Trump: %d"%(biden_med, trump_med))


