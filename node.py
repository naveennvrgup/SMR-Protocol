from matplotlib import lines
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
        # deleting the previous plotted lines
        for _ in range(len(self.lines)):
            plt_line = self.lines.pop()
            plt_line.pop().remove()

        # successful transmission is blue
        # if a reciever get multiple signals at the same time
        # then it will result in noise (green)
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
        self.broadcast_cooldown = 0

    def plot_node(self):
        plt.scatter(self.x, self.y, s=30,
                    facecolors='none', edgecolors='k')

    def is_broadcast_successful(self):
        # broadcast is successful if no overlapping signal is recieved currently
        # during transmission 

        if not self.curr_broadcast:
            return

        if self.curr_signals:
            self.ready.insert(0, self.curr_broadcast)

            # in case of a collision the transmitter will wait for a random 
            # amount of time before tring again. typical
            # TDM collision handling like CSMA/CD
            self.broadcast_cooldown = random.randint(0, 10)
            print(f'broadcast failed in {self}')
        
        # clear curent broadcast
        self.curr_broadcast = None

    def broadcast(self):
        self.broadcast_cooldown -= 1

        if not self.ready or self.broadcast_cooldown > 0:
            return

        rogue_vessel = self.ready.pop(0)

        for nei in self.neighbours:
            self.curr_broadcast = rogue_vessel
            nei.recieve(Packet(
                timestamp=timer,
                found_by=self,
                rouge=rogue_vessel
            ))
