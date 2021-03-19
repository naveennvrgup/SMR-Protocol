import random

width = 100
height = 100
load_from_pickles = False

normal_vessels_count = 400
rogue_vessels_count = 5
ground_stations_count = 2

ttl_acknowledgement = 0.1
clique_dist = 10
time_quanta = 0.1
timer = 0

colors = ['b-', 'r-', 'c-', 'm-', 'y-', 'k-']

DEBUG = False
track_packet_id = 1
track_packet = True
track_vessel_id = 1
track_vessel = True

def get_color():
    return random.choice(colors)
