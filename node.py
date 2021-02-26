from tkinter import Pack
from matplotlib import lines
from matplotlib.markers import MarkerStyle
from copy import deepcopy
import random
from my_constants import width, height, timer, get_color, clique_dist
import matplotlib.pyplot as plt
from collections import defaultdict
import math
from utils import paint_debug_point


class Packet:
    def __init__(self, timestamp, rouge, found_by, transmitted_by, color) -> None:
        self.timestamp = timestamp
        self.rouge = rouge
        self.found_by = str(found_by)
        self.transmitted_by_x = transmitted_by.x
        self.transmitted_by_y = transmitted_by.y
        self.nei = [str(x) for x in transmitted_by.neighbours]
        self.color = color

    def __str__(self):
        return f'{self.rouge}'


class Node:
    line = None

    def __init__(self) -> None:
        self.x = random.randint(2, width-2)
        self.y = random.randint(2, height-2)
        self.recieved = defaultdict(bool)
        self.curr_signals = []

    def is_recieve_successful(self):
        # more than one signals with result in noise
        if len(self.curr_signals) > 1:
            self.curr_signals = []

        if self.curr_signals:
            packet = self.curr_signals[0]

    def plot_lines(self):
        # deleting the previous plotted line
        if self.line:
            self.line.pop().remove()

        if self.curr_signals:
            packet = self.curr_signals.pop()
            self.line = plt.plot(
                [self.x, packet.transmitted_by_x],
                [self.y, packet.transmitted_by_y],
                packet.color)

    def recieve(self, packet):
        clone_pkt = Packet(packet.timestamp, packet.rouge,
                           packet.found_by, self, packet.color)
        clone_pkt.transmitted_by_x = packet.transmitted_by_x
        clone_pkt.transmitted_by_y = packet.transmitted_by_y
        self.curr_signals.append(clone_pkt)

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'


class RogueVessel(Node):
    def __init__(self) -> None:
        super().__init__()

    def plot_node(self):
        plt.scatter(self.x, self.y, s=30, facecolors='r')


class GroundStation(Node):
    def __init__(self) -> None:
        super().__init__()
        self.recieved = defaultdict(bool)

    def plot_node(self):
        plt.scatter(self.x, self.y, s=30, facecolors='b')


class NormalVessel(Node):
    def __init__(self) -> None:
        super().__init__()
        self.neighbours = []
        self.ready = []
        self.curr_broadcast = None
        self.broadcast_cooldown = 0

    def plot_node(self):
        plt.scatter(self.x, self.y, s=30,
                    facecolors='none', edgecolors='k')

    def plot_lines(self):
        # mark the curr_signal as recieved so that
        # the node doesn't retransmit the same thing
        # again and again
        if self.curr_signals:
            packet = self.curr_signals[0]
            if not self.recieved[str(packet)]:
                self.ready.append(packet)

        return super().plot_lines()

    def is_broadcast_successful(self):
        # broadcast is successful if no overlapping signal is recieved currently
        # during transmission

        if not self.curr_broadcast:
            return

        # in case of a collision the transmitter will wait for a random
        # amount of time before tring again. typical
        # TDM collision handling like CSMA/CD
        if self.curr_signals:
            self.ready.insert(0, self.curr_broadcast)

            self.broadcast_cooldown = random.randint(0, 10)

        # clear curent broadcast
        self.curr_broadcast = None
        self.curr_signals = []

    def broadcast(self):
        self.broadcast_cooldown -= 1

        if not self.ready or self.broadcast_cooldown > 0:
            return

        packet = self.ready.pop(0)

        if self.recieved[str(packet)]:
            return
            
        packet.transmitted_by_x = self.x
        packet.transmitted_by_y = self.y
        packet.neighbours = [str(x) for x in self.neighbours]
        self.curr_broadcast = packet

        for nei in self.neighbours:
            nei.recieve(packet)

        # to prevent the retransmission if the same packet
        # is recieved from the neighbour
        self.recieved[str(packet)] = True

    def push_to_ready(self, rogue_vessel):
        packet = Packet(
            timestamp=timer,
            found_by=self,
            rouge=rogue_vessel,
            transmitted_by=self,
            color=get_color()
        )

        self.ready.append(packet)
