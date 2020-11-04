import csv
import json
import random
import statistics
import urllib.request

def get(url):
    with urllib.request.urlopen(url) as response:
        r = response.read()
        return r

votes = {}
states = []
probs = {}
purl = 'https://www.predictit.org/api/marketdata/all/'

def national(us):
    print()
    print("National Election Betting Odds")
    for c in us['contracts']:
        ltp = c['lastTradePrice']
        by = c['bestBuyYesCost']
        sn = c['bestSellNoCost']

        sy = c['bestSellYesCost']
        bn = c['bestBuyNoCost']
        name = c['name']
        #print( name)
        #print(by)
        #print(sn)
        #print(sy)
        #print(bn)
        if ltp and by and sn and sy and bn:
            avg = (by + (1-sn) + sy + (1-bn))/4.
            print ("%s : %2.0f%%, Avg: %2.0f%%"%(name, ltp*100, avg*100))
    print()

aurl = 'https://www.predictit.org/api/marketdata/markets/2721/'
ndata = json.loads(get(aurl))

national(ndata)

with open('electoralvotes.csv') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        states.append(row[0])
        votes[row[0]] = int(row[1])


r = get(purl)
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
print("Avg:    Biden: %.2f, Trump: %.2f"%(biden_mean, trump_mean))
print("Median: Biden: %d, Trump: %d"%(biden_med, trump_med))

national(ndata)
