from tkinter.constants import NO
from matplotlib.markers import MarkerStyle
import random
import my_constants
import matplotlib.pyplot as plt


class Node:
    def __init__(self) -> None:
        self.x = random.randint(2, my_constants.width-2)
        self.y = random.randint(2, my_constants.height-2)


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
