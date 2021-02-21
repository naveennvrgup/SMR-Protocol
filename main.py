from node_types import NodeType
from node import Node, NormalVessel, RogueVessel, GroundStation
import numpy as np
import matplotlib.pyplot as plt
import my_constants
from collections import defaultdict
from tkinter import *


# global
nodes = defaultdict(Node)


def main():
    # initialising graph
    plt.axis([0, my_constants.width, 0, my_constants.height])

    normal_vessels = [NormalVessel() for _ in range(100)]
    rouge_vessels = [RogueVessel() for _ in range(5)]
    ground_stations = [GroundStation() for _ in range(5)]
    all_vessels = [*normal_vessels, *rouge_vessels, *ground_stations]

    for node in all_vessels:
        node.plot_node()

    plt.show()


if __name__ == "__main__":
    try:
        print("Starting SMR Protocol Simulation")
        main()
    except Exception:
        print("Ending Simulation")
