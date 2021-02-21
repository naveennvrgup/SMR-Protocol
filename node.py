from matplotlib.markers import MarkerStyle
import random
from my_constants import width, height
import matplotlib.pyplot as plt


class Node:
    def __init__(self) -> None:
        self.x = random.randint(2, width-2)
        self.y = random.randint(2, height-2)


class NormalVessel(Node):
    def __init__(self) -> None:
        super().__init__()

    def plot_node(self):
        plt.scatter(self.x, self.y, s=30,
                    facecolors='none', edgecolors='k')


class RogueVessel(Node):
    def __init__(self) -> None:
        super().__init__()

    def plot_node(self):
        plt.scatter(self.x, self.y, s=30, facecolors='r')


class GroundStation(Node):
    def __init__(self) -> None:
        super().__init__()

    def plot_node(self):
        plt.scatter(self.x, self.y, s=30, facecolors='b')
