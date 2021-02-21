from utils import visualise_adj
from matplotlib import lines
from node import Node, NormalVessel, RogueVessel, GroundStation
import numpy as np
import matplotlib.pyplot as plt
import my_constants
from collections import defaultdict
from tkinter import *
import traceback
import math

# global
lines = None
clock_text = None
time = 0
adj = []
timer = 0


def main():
    global lines, time, adj, timer, clock_text

    # initialising graph
    plt.axis([0, my_constants.width, 0, my_constants.height])
    plt.title('Team Fuffy Cats - SMR Protocol Simulation')

    # starting params
    normal_vessels_count = 125
    rouge_vessels_count = 5
    ground_stations_count = 2
    clique_dist = 10
    time_quanta = 0.5
    n = normal_vessels_count + rouge_vessels_count + ground_stations_count

    # create nodes
    normal_vessels = [NormalVessel() for _ in range(normal_vessels_count)]
    rouge_vessels = [RogueVessel() for _ in range(rouge_vessels_count)]
    ground_stations = [GroundStation() for _ in range(ground_stations_count)]
    all_vessels = normal_vessels + rouge_vessels + ground_stations

    for node in all_vessels:
        node.plot_node()

    # adjacency list of nodes
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue

            x1 = all_vessels[i].x
            x2 = all_vessels[j].x
            y1 = all_vessels[i].y
            y2 = all_vessels[j].y
            dist = math.sqrt((x1-x2)**2+(y1-y2)**2)

            # for sake of simulation if the distance between two nodes
            # is less than clique_dist units then can recieve each others transmission
            if dist <= clique_dist:
                adj[i].append(all_vessels[j])

    visualise_adj(plt, all_vessels, adj)

    # this never ends
    for i in range(99):
        timer += time_quanta

        if clock_text:
            clock_text.remove()

        if lines:
            lines.pop().remove()

        lines = plt.plot([all_vessels[i].x, all_vessels[i+1].x],
                         [all_vessels[i].y, all_vessels[i+1].y])

        clock_text = plt.text(0, 0, f'Clock: {timer}s')

        # waiting time_quanta seconds until next run
        plt.pause(time_quanta)

    plt.show()


if __name__ == "__main__":
    try:
        print("Starting SMR Protocol Simulation")
        main()
    except Exception as err:
        print("oops something went wrong")
        traceback.print_exc()
    finally:
        print("Ending Simulation")
