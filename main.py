from utils import visualise_adj, visualise_mesh
from matplotlib import lines
from node import Node, NormalVessel, RogueVessel, GroundStation
import matplotlib.pyplot as plt
from collections import defaultdict
from tkinter import *
import traceback
import math
import pickle
import random
from IPython import display
import pandas as pd

# this is to fix the randomness
random.seed(10)


def start_simula(normal_vessels, good_vessels, config_obj):
    clock_text = None
    load_df = pd.DataFrame(index=[str(x) for x in normal_vessels])
    packet_df = pd.DataFrame()

    while True:
        broadcasts_left = sum([len(node.ready) for node in normal_vessels])
        print(f'{config_obj.timer} >>> broadcasts left: {broadcasts_left}', end='\r')

        load_observation = pd.Series(
            [False for x in normal_vessels],
            index=[str(x) for x in normal_vessels]
        )
        packet_observation = defaultdict(int)

        if not broadcasts_left:
            return load_df, packet_df

        config_obj.timer = round(config_obj.timer + config_obj.time_quanta, 2)

        if clock_text:
            clock_text.remove()

        for vessel in normal_vessels:
            vessel.broadcast()  # curr_broadcast curr_signals
        for vessel in normal_vessels:
            # returns a boolean indicating a reception
            # noise in reciver side
            reception, reception_packet_pk = vessel.is_receive_successful()
            load_observation.loc[str(vessel)] |= reception
            if reception_packet_pk is not None:
                packet_observation[reception_packet_pk] += 1

        for vessel in normal_vessels:
            # returns a boolean indicating a broadcast
            # noise in tranmisstor side
            load_observation.loc[str(vessel)] |= vessel.is_broadcast_successful()
        for vessel in good_vessels:
            vessel.plot_lines()  # plot lines

        clock_text = plt.text(0, 0, f'Clock: {config_obj.timer}s')

        # waiting time_quanta seconds until next run
        # plt.pause(time_quanta)

        load_df[config_obj.timer] = load_observation
        packet_df[config_obj.timer] = pd.Series(packet_observation)
    print(packet_df)


class Config:
    def __init__(
            self,
            width,
            height,
            normal_vessels_count,
            rogue_vessels_count,
            ground_stations_count,
            clique_dist,
            time_quanta,
            ttl_acknowledgement,
            timer):
        super().__init__()
        self.width = width
        self.height = height
        self.normal_vessels_count = normal_vessels_count
        self.rogue_vessels_count = rogue_vessels_count
        self.ground_stations_count = ground_stations_count
        self.clique_dist = clique_dist
        self.time_quanta = time_quanta
        self.ttl_acknowledgement = ttl_acknowledgement
        self.timer = timer


def main(config_obj):
    # initialising graph
    plt.axis([0, config_obj.width, 0, config_obj.height])
    plt.title('Team Fuffy Cats - SMR Protocol Simulation')

    total_vessel_count = 0
    total_packet_count = 0

    # create nodes

    normal_vessels = []
    rogue_vessels = []
    ground_stations = []

    for _ in range(config_obj.normal_vessels_count):
        normal_vessel = NormalVessel(total_vessel_count, config_obj)
        total_vessel_count = total_vessel_count + 1
        normal_vessels.append(normal_vessel)

    for _ in range(config_obj.rogue_vessels_count):
        rogue_vessel = RogueVessel(total_vessel_count, config_obj)
        total_vessel_count = total_vessel_count + 1
        rogue_vessels.append(rogue_vessel)

    for _ in range(config_obj.ground_stations_count):
        ground_station = GroundStation(total_vessel_count, config_obj)
        total_vessel_count = total_vessel_count + 1
        ground_stations.append(ground_station)

    all_vessels = normal_vessels + rogue_vessels + ground_stations
    good_vessels = normal_vessels + ground_stations

    # adjacency list of nodes
    for i in range(config_obj.normal_vessels_count):
        x1 = all_vessels[i].x
        y1 = all_vessels[i].y

        for j in range(config_obj.normal_vessels_count):
            if i == j:
                continue

            x2 = all_vessels[j].x
            y2 = all_vessels[j].y
            dist = math.sqrt((x1-x2)**2+(y1-y2)**2)

            # for sake of simulation if the distance between two nodes
            # is less than clique_dist units then can receive each others transmission
            if dist <= config_obj.clique_dist:
                normal_vessels[i].neighbours.append(normal_vessels[j])

        for j in range(config_obj.rogue_vessels_count):
            x2 = rogue_vessels[j].x
            y2 = rogue_vessels[j].y
            dist = math.sqrt((x1-x2)**2+(y1-y2)**2)

            if dist <= config_obj.clique_dist:
                normal_vessels[i].push_to_ready(
                    rogue_vessels[j], total_packet_count)
                total_packet_count = total_packet_count + 1

    # paint all them nodes
    for node in all_vessels:
        node.plot_node()

    # for visualising the meshnet
    # visualise_mesh(plt, normal_vessels)

    # show the neighbours of the nodes
    # visualise_adj(plt, normal_vessels)

    # return the result dataframe
    return start_simula(normal_vessels, good_vessels, config_obj)

    # plt.show()


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
