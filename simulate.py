import csv
import json
import random
import statistics
import datetime
import requests
import re

states = []
votes = {}

def get_state_data():
    state_data = {}
    r = requests.get("https://electionbettingodds.com")

    p1 = r"case\s'([A-Z0-9]+)':\n.*?Republican:\s([\d\.]+)%.*?Democrat:\s([\d\.]+)%.*?Electoral votes:\s(\d+)"
    matches = re.findall(p1, r.text)

    probs = {}

    for match in matches:
        state, republican_prob, democrat_prob, electoral_votes = match
        p = float(democrat_prob) / (float(democrat_prob) + float(republican_prob))
        state_data[state] = p
        votes[state] = int(electoral_votes)

    p2 = r"case\s'([A-Z0-9]+)':\n.*?Democrat:\s([\d\.]+)%.*?Republican:\s([\d\.]+)%.*?Electoral votes:\s(\d+)"
    matches = re.findall(p2, r.text)

    for match in matches:
        state, democrat_prob, republican_prob, electoral_votes = match
        p = float(democrat_prob) / (float(democrat_prob) + float(republican_prob))
        state_data[state] = p
        votes[state] = int(electoral_votes)

    # Election betting odds doesn't have DC idk why
    votes['DC'] = 3
    state_data['DC'] = .99
    return state_data


def simulate(probs, seed, epochs):
    trump_votes = []
    harris_votes = []
    random.seed(seed)
    for e in range(epochs):
        harris = 0
        trump = 0
        for state in probs.keys():
            if probs[state] > random.random():
                harris += votes[state]
            else:
                trump += votes[state]
        harris_votes.append(harris)
        trump_votes.append(trump)
        # print("Harris: %d, Trump: %d"%(harris, trump))
    return harris_votes, trump_votes

def run_simulations(probs, n):
    toprint = ""
    harris_votes, trump_votes = simulate(probs, 0, n)
    harris_wins = sum(map(lambda x: x[0] > x[1], zip(harris_votes, trump_votes)))
    trump_wins = sum(map(lambda x: x[0] < x[1], zip(harris_votes, trump_votes)))
    tie = sum(map(lambda x: x[0] == x[1], zip(harris_votes, trump_votes)))
    harris_mean = statistics.mean(harris_votes)
    trump_mean = statistics.mean(trump_votes)
    harris_med = statistics.median(harris_votes)
    trump_med = statistics.median(trump_votes)


    toprint += "\n"
    toprint += "%d Simulations\n"%n
    toprint += "Counts: Harris: %d, Trump: %d, Ties: %d\n"%(harris_wins, trump_wins, tie)
    toprint += "Probs:  Harris: %.2f%%, Trump: %.2f%%, Ties: %.2f%%\n"%(harris_wins*100.0/n, trump_wins*100.0/n, tie*100./n)
    toprint += "Avg:    Harris: %.2f, Trump: %.2f\n"%(harris_mean, trump_mean)
    toprint += "Median: Harris: %d, Trump: %d\n"%(harris_med, trump_med)
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

n = 100000

statedata = get_state_data()
print(run_simulations(statedata, n))

