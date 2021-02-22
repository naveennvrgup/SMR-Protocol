from tkinter import Pack
from tkinter.constants import E, NONE
from matplotlib.markers import MarkerStyle
import random
from my_constants import width, height, timer
import matplotlib.pyplot as plt
from collections import defaultdict


class Packet:
    def __init__(self, timestamp, rouge, found_by) -> None:
        self.timestamp = timestamp
        self.rouge = rouge
        self.found_by = found_by
        self.lines = []

    def __str__(self):
        return f'{self.timestamp}-{self.rouge}-{self.found_by}'


class Node:
    def __init__(self) -> None:
        self.x = random.randint(2, width-2)
        self.y = random.randint(2, height-2)
        self.recieved = defaultdict(Packet)
        self.curr_signals = []
        self.lines = []

    def plot_lines(self):
        for line in self.lines:
            line.pop().remove()

        color = 'b-'

        if len(self.curr_signals) == 1:
            self.recieved[self.curr_signals[0]] = self.curr_signals[0]
        else:
            color = 'g-'

        for signal in self.curr_signals:
            self.lines.append(plt.plot(
                [self.x, signal.found_by.x],
                [self.y, signal.found_by.y],
                color))

        self.curr_signals = []

    def recieve(self, packet: Packet):
        self.curr_signals.append(packet)

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

    def plot_node(self):
        plt.scatter(self.x, self.y, s=30,
                    facecolors='none', edgecolors='k')

    def any_rogue_nearby(self):
        for nei in self.neighbours:
            if nei.__name__ == 'RougeVessel':
                rouge_in_ready = False
                for vessel in self.ready:
                    if vessel == nei:
                        rouge_in_ready = True

                if not rouge_in_ready:
                    self.ready.append(nei)

    def is_broadcast_successful(self):
        if not self.curr_broadcast:
            return

        if self.curr_signals:
            self.ready.insert(0, self.curr_broadcast)
            self.curr_broadcast = None
            print(f'broadcast fail in {self}')

    def broadcast(self):
        if not self.ready:
            return

        rogue_vessel = self.ready.pop(0)

        for nei in self.neighbours:
            self.curr_broadcast = rogue_vessel
            nei.recieve(Packet(
                timestamp=timer,
                found_by=self,
                rouge=rogue_vessel
            ))
