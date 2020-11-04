import csv
import json
import random
import statistics
import urllib.request
import datetime

states = []
votes = {}
with open('electoralvotes.csv') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        states.append(row[0])
        votes[row[0]] = int(row[1])

def get(url):
    with urllib.request.urlopen(url) as response:
        r = response.read().decode('utf-8')
        return r


def get_state_data(fetch):
    purl = 'https://www.predictit.org/api/marketdata/all/'
    state_data = {}
    try:
        bets = json.loads(open("states.json", "r").read())
    except:
        print("Failed to load state cache")

    if fetch:
        try:
            r = get(purl)
            bets = json.loads(r)
            bets['time'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            open("states.json", "w").write(json.dumps(bets))
        except:
            print("Failed to fetch state data")

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
                state_data[state] = prob
    if 'time' in bets:
        state_data['time'] = bets['time']
    return state_data

    

def print_national(us):
    toprint = ""
    toprint += "National Election Betting Odds\n"
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
            toprint += "%s : %2.0f%%, Avg: %2.0f%%\n"%(name, ltp*100, avg*100)
    if 'time' in us:
        toprint += "Updated at: " + us['time'] + "\n"
    toprint += "\n"
    return toprint

def get_national_data(fetch):
    try:
        jsonstr = open("national.json").read()
        ndata = json.loads(jsonstr)
    except:
        print("Couldn't load national.json")
    if fetch:
        try:
            aurl = 'https://www.predictit.org/api/marketdata/markets/2721/'
            ndata = json.loads(get(aurl))
            ndata['time'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            open("national.json", "w").write(json.dumps(ndata))
        except TypeError as e:
            print(e)
    return ndata



def print_states(statelist, probs):
    toprint = ""
    svotes = 0
    for state in statelist:
        svotes += votes[state]
        toprint+="%20s, %2d votes, %5.2f%% Biden, %5.2f%% Trump %3d\n"%(state, votes[state], 100*probs[state], 100*(1-probs[state]), svotes)
    return toprint
        


def print_state_data(probs):
    toprint = ""
    #toprint += "Alphabetical\n"
    #toprint += print_states(states, probs)

    toprint +="Sorted\n"
    def bprob(state):
        return probs[state]

    sortedstates = states
    sortedstates.sort(key=bprob)
    toprint += print_states(sortedstates, probs)
    toprint += "\n"
    return toprint

def simulate(probs, seed, epochs):
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

def run_simulations(probs, n):
    toprint = ""
    biden_votes, trump_votes = simulate(probs, 0, n)
    biden_wins = sum(map(lambda x: x[0] > x[1], zip(biden_votes, trump_votes)))
    trump_wins = sum(map(lambda x: x[0] < x[1], zip(biden_votes, trump_votes)))
    tie = sum(map(lambda x: x[0] == x[1], zip(biden_votes, trump_votes)))
    biden_mean = statistics.mean(biden_votes)
    trump_mean = statistics.mean(trump_votes)
    biden_med = statistics.median(biden_votes)
    trump_med = statistics.median(trump_votes)


    toprint += "\n"
    toprint += "%d Simulations\n"%n
    toprint += "Counts: Biden: %d, Trump: %d, Ties: %d\n"%(biden_wins, trump_wins, tie)
    toprint += "Probs:  Biden: %.2f%%, Trump: %.2f%%, Ties: %.2f%%\n"%(biden_wins*100.0/n, trump_wins*100.0/n, tie*100./n)
    toprint += "Avg:    Biden: %.2f, Trump: %.2f\n"%(biden_mean, trump_mean)
    toprint += "Median: Biden: %d, Trump: %d\n"%(biden_med, trump_med)
    if 'time' in probs:
        toprint += "Updated at: " + probs['time'] + "\n"
    toprint += "\n"
    return toprint

from flask import Flask
from flask import jsonify
app = Flask(__name__)

@app.route('/cached/')
def cached():
    toprint = ""
    n = 10000

    statedata = get_state_data(0)
    toprint += run_simulations(statedata, n)

    ndata = get_national_data(0)
    toprint += print_national(ndata)
    toprint += print_state_data(statedata)
    return jsonify(toprint)

@app.route('/reload/')
def reload():
    toprint = ""
    n = 10000

    statedata = get_state_data(1)
    toprint += run_simulations(statedata, n)

    ndata = get_national_data(1)
    toprint += print_national(ndata)
    toprint += print_state_data(statedata)
    return jsonify(toprint)


@app.route('/')
def index():
    template = """
<!doctype html>
<html>
<body><a href="https://github.com/pjreddie/prezsim">Open Source on Github</a><pre id="odds"></pre></body>
<script>
fetch('./cached/')
  .then(response => response.json())
  .then(data => document.getElementById("odds").innerHTML = data);

fetch('./reload/')
  .then(response => response.json())
  .then(data => document.getElementById("odds").innerHTML = data);
</script>
</html>"""
    return template

n = 10000
ndata = get_national_data(1)
print_national(ndata)

statedata = get_state_data(1)
print_state_data(statedata)
run_simulations(statedata, n)


print_national(ndata)

