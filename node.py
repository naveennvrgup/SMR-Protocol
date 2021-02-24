from matplotlib import lines
from matplotlib.markers import MarkerStyle
from copy import deepcopy
import random
from my_constants import width, height, timer, get_color, packets_info
import matplotlib.pyplot as plt
from collections import defaultdict


class Packet:
    def __init__(self, timestamp, rouge, found_by, transmitted_by, color) -> None:
        self.timestamp = timestamp
        self.rouge = rouge
        self.found_by = str(found_by)
        self.transmitted_by_x = transmitted_by.x
        self.transmitted_by_y = transmitted_by.y
        self.color = color

    def __str__(self):
        return f'{self.rouge}'


class Node:
    def __init__(self) -> None:
        self.x = random.randint(2, width-2)
        self.y = random.randint(2, height-2)
        self.recieved = defaultdict(bool)
        self.curr_signals = []
        self.lines = []

    def plot_lines(self):
        # deleting the previous plotted lines
        for _ in range(len(self.lines)):
            plt_line = self.lines.pop()
            plt_line.pop().remove()

        for packet in self.curr_signals:
            # if a reciever get multiple signals at the same time
            # then it will result in noise (shown by green)
            self.lines.append(plt.plot(
                [self.x, packet.transmitted_by_x],
                [self.y, packet.transmitted_by_y],
                'g-' if len(self.curr_signals) == 1 else packet.color))

        self.curr_signals = []

    def recieve(self, packet):
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
        self.broadcast_cooldown = 0

    def plot_node(self):
        plt.scatter(self.x, self.y, s=30,
                    facecolors='none', edgecolors='k')

    def plot_lines(self):
        if len(self.curr_signals) == 1:
            # mark the curr_signal as recieved so that
            # the node doesn't retransmit the same thing
            # again and again
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

    def broadcast(self):
        self.broadcast_cooldown -= 1

        if not self.ready or self.broadcast_cooldown > 0:
            return

        packet = self.ready.pop(0)
        packet.transmitted_by_x = self.x
        packet.transmitted_by_y = self.y
        self.curr_broadcast = packet

        if self.recieved[str(packet)]:
            return

        for nei in self.neighbours:
            nei.recieve(packet)

        # to prevent the retransmission if the same packet
        # is recieved from the neighbour
        self.recieved[str(packet)] = True
        packets_info[str(packet)] += 1

    def push_to_ready(self, rogue_vessel):
        packet = Packet(
            timestamp=timer,
            found_by=self,
            rouge=rogue_vessel,
            transmitted_by=self,
            color=get_color()
        )

        self.ready.append(packet)
