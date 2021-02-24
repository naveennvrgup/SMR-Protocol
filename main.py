from utils import visualise_adj
from matplotlib import lines
from node import Node, NormalVessel, RogueVessel, GroundStation
import matplotlib.pyplot as plt
from my_constants import width, height, normal_vessels_count, rouge_vessels_count, ground_stations_count, clique_dist, time_quanta, timer
from collections import defaultdict
from tkinter import *
import traceback
import math


def start_simula(normal_vessels, good_vessels):
    global timer, time_quanta
    clock_text = None

    # for i in range(3):
    while True:
        # print(f'----------------------{timer}------------------------')
        broadcasts_left = sum([len(node.ready) for node in normal_vessels])
        # print(f"broadcasts left: {broadcasts_left}")

        if not broadcasts_left:
            break

        timer += time_quanta

        if clock_text:
            clock_text.remove()

        for vessel in normal_vessels:
            vessel.broadcast()
        for vessel in normal_vessels:
            vessel.is_broadcast_successful()
        for vessel in good_vessels:
            vessel.plot_lines()

        clock_text = plt.text(0, 0, f'Clock: {timer}s')

        # waiting time_quanta seconds until next run
        plt.pause(time_quanta)


def main():
    # initialising graph
    plt.axis([0, width, 0, height])
    plt.title('Team Fuffy Cats - SMR Protocol Simulation')

    # create nodes
    normal_vessels = [NormalVessel() for _ in range(normal_vessels_count)]
    rouge_vessels = [RogueVessel() for _ in range(rouge_vessels_count)]
    ground_stations = [GroundStation() for _ in range(ground_stations_count)]
    all_vessels = normal_vessels + rouge_vessels + ground_stations
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
            # is less than clique_dist units then can recieve each others transmission
            if dist <= clique_dist:
                normal_vessels[i].neighbours.append(normal_vessels[j])

        for j in range(rouge_vessels_count):
            x2 = rouge_vessels[j].x
            y2 = rouge_vessels[j].y
            dist = math.sqrt((x1-x2)**2+(y1-y2)**2)

            if dist <= clique_dist:
                normal_vessels[i].push_to_ready(rouge_vessels[j])

    # paint all them nodes
    for node in all_vessels:
        node.plot_node()

    # for visualising the meshnet
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
