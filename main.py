from utils import visualise_adj, visualise_mesh
from matplotlib import lines
from node import Node, NormalVessel, RogueVessel, GroundStation
import matplotlib.pyplot as plt
from my_constants import width, height, normal_vessels_count, rogue_vessels_count, ground_stations_count, clique_dist, time_quanta, timer, load_from_pickles
from collections import defaultdict
from tkinter import *
import traceback
import math
import pickle
import random

# this is to fix the randomness
random.seed(10)


def start_simula(normal_vessels, good_vessels):
    global timer, time_quanta
    clock_text = None

    while True:
        print(f'----------------------{timer}------------------------')
        broadcasts_left = sum([len(node.ready) for node in normal_vessels])
        print(f"broadcasts left: {broadcasts_left}")

        if not broadcasts_left:
            exit()

        timer += time_quanta

        if clock_text:
            clock_text.remove()

        for vessel in normal_vessels:
            vessel.broadcast()  # curr_broadcast curr_signals
        for vessel in normal_vessels:
            vessel.is_receive_successful()  # noise in reciver side
        for vessel in normal_vessels:
            vessel.is_broadcast_successful()  # noise in tranmisstor side
        for vessel in good_vessels:
            vessel.plot_lines()  # plot lines

        clock_text = plt.text(0, 0, f'Clock: {timer}s')

        # waiting time_quanta seconds until next run
        plt.pause(time_quanta)


def main():
    # initialising graph
    plt.axis([0, width, 0, height])
    plt.title('Team Fuffy Cats - SMR Protocol Simulation')

    total_vessel_count = 0
    total_packet_count = 0

    # create nodes
    if load_from_pickles:
        print('-----------------------')
        print("loading from pickle")
        print('-----------------------')
        with open('data.pickle', 'rb') as f:
            data = pickle.load(f)

        normal_vessels = data['normal_vessels']
        rogue_vessels = data['rogue_vessels']
        ground_stations = data['ground_stations']
    else:
        print('-----------------------')
        print("creating new data")
        print('-----------------------')

        normal_vessels = []
        rogue_vessels = []
        ground_stations = []

        for _ in range(normal_vessels_count):
            normal_vessel = NormalVessel(total_vessel_count) 
            total_vessel_count = total_vessel_count + 1 
            normal_vessels.append(normal_vessel)

        for _ in range(rogue_vessels_count):
            rogue_vessel = RogueVessel(total_vessel_count) 
            total_vessel_count = total_vessel_count + 1 
            rogue_vessels.append(rogue_vessel)

        for _ in range(ground_stations_count):
            ground_station = GroundStation(total_vessel_count) 
            total_vessel_count = total_vessel_count + 1 
            ground_stations.append(ground_station)

        data = {
            'normal_vessels': normal_vessels,
            'rogue_vessels': rogue_vessels,
            'ground_stations': ground_stations
        }

        with open('data.pickle', 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    all_vessels = normal_vessels + rogue_vessels + ground_stations
    good_vessels = normal_vessels + ground_stations

    # adjacency list of nodes
    for i in range(normal_vessels_count):
        x1 = all_vessels[i].x
        y1 = all_vessels[i].y

        for j in range(normal_vessels_count):
            if i == j:
                continue

            x2 = all_vessels[j].x
            y2 = all_vessels[j].y
            dist = math.sqrt((x1-x2)**2+(y1-y2)**2)

            # for sake of simulation if the distance between two nodes
            # is less than clique_dist units then can receive each others transmission
            if dist <= clique_dist:
                normal_vessels[i].neighbours.append(normal_vessels[j])

        for j in range(rogue_vessels_count):
            x2 = rogue_vessels[j].x
            y2 = rogue_vessels[j].y
            dist = math.sqrt((x1-x2)**2+(y1-y2)**2)

            if dist <= clique_dist:
                normal_vessels[i].push_to_ready(rogue_vessels[j], total_packet_count)
                total_packet_count = total_packet_count + 1


    # paint all them nodes
    for node in all_vessels:
        node.plot_node()

    # for visualising the meshnet
    # visualise_mesh(plt, normal_vessels)

    # show the neighbours of the nodes
    # visualise_adj(plt, normal_vessels)

    # this never ends
    start_simula(normal_vessels, good_vessels)

    plt.show()




if __name__ == "__main__":
    try:
        print("Starting SMR Protocol Simulation")
        main()
    except Exception as err:
        print("oops something went wrong")
        traceback.print_exc()
        exit()
    finally:
        print("Ending Simulation")
