from matplotlib import lines
from node import Node, NormalVessel, RogueVessel, GroundStation
import numpy as np
import matplotlib.pyplot as plt
import my_constants
from collections import defaultdict
from tkinter import *


# global
nodes = defaultdict(Node)
lines = None
time = 0


def main():
    global lines
    global time

    # initialising graph
    plt.axis([0, my_constants.width, 0, my_constants.height])
    plt.title('Team Fuffy Cats - SMR Protocol Simulation')

    # create nodes
    normal_vessels = [NormalVessel() for _ in range(100)]
    rouge_vessels = [RogueVessel() for _ in range(5)]
    ground_stations = [GroundStation() for _ in range(5)]
    all_vessels = [*normal_vessels, *rouge_vessels, *ground_stations]

    for node in all_vessels:
        node.plot_node()

    # this never ends
    for i in range(99):
        if lines:
            lines.pop().remove()
        lines = plt.plot([all_vessels[i].x, all_vessels[i+1].x],
                         [all_vessels[i].y, all_vessels[i+1].y])
        plt.pause(0.5)

    plt.show()


if __name__ == "__main__":
    try:
        print("Starting SMR Protocol Simulation")
        main()
    except Exception:
        print("Ending Simulation")
