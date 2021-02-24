import random
from collections import defaultdict

width = 100
height = 100

normal_vessels_count = 300
rouge_vessels_count = 20
ground_stations_count = 2

clique_dist = 8
time_quanta = 0.1
timer = 0

colors = ['b-', 'r-', 'c-', 'm-', 'y-', 'k-']
packets_info = defaultdict(int)


def get_color():
    return random.choice(colors)
