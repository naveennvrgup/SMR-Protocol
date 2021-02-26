import random

width = 100
height = 100
load_from_pickles = False

normal_vessels_count = 400
rouge_vessels_count = 5
ground_stations_count = 2

clique_dist = 10
time_quanta = 0.1
timer = 0

colors = ['b-', 'r-', 'c-', 'm-', 'y-', 'k-']


def get_color():
    return random.choice(colors)
