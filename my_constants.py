import random


width = 100
height = 100

normal_vessels_count = 200
rouge_vessels_count = 10
ground_stations_count = 2

clique_dist = 5
time_quanta = 0.3
timer = 0

colors = ['b-', 'r-', 'c-', 'm-', 'y-', 'k-']


def get_color():
    return random.choice(colors)
