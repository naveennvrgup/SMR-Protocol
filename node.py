from tkinter import Pack

from matplotlib import lines
from matplotlib.markers import MarkerStyle
from copy import deepcopy
import random
from my_constants import (
    get_color,
    DEBUG,
    track_packet_id,
    track_packet,
    track_vessel_id,
    track_vessel
)
import matplotlib.pyplot as plt
from collections import defaultdict
import math
from utils import paint_debug_point

packet_dict = defaultdict()

class Packet:
    def __init__(self, pk, timestamp, rogue, found_by, transmitted_by, color, retransmit) -> None:
        self.pk = pk
        self.timestamp = timestamp
        self.rogue = rogue
        self.found_by = str(found_by)
        self.transmitted_by = transmitted_by
        self.color = color
        self.retransmit = retransmit

    def __str__(self):
        return f'Packet_{self.pk}'


class Node:
    line = None

    def __init__(self, total_vessel_count, config_obj) -> None:
        self.config_obj = config_obj
        self.pk = total_vessel_count
        self.x = random.randint(2, self.config_obj.width-2)
        self.y = random.randint(2, self.config_obj.height-2)
        self.prev_transmitted_packets = defaultdict(bool)
        self.curr_signals = []


    def is_receive_successful(self):
        # more than one signals with result in noise
        reception = len(self.curr_signals) > 0
        reception_packet_pk = None

        if len(self.curr_signals) > 1:
            self.curr_signals = []

        if self.curr_signals:
            packet = self.curr_signals[0]
            reception_packet_pk = packet.pk

        return reception, reception_packet_pk

    def plot_lines(self):
        # deleting the previous plotted line
        if self.line:
            self.line.pop().remove()

        if self.curr_signals:
            packet = self.curr_signals.pop()
            if self.config_obj.show_graph:
                self.line = plt.plot(
                    [self.x, packet.transmitted_by.x],
                    [self.y, packet.transmitted_by.y],
                    packet.color)

    def receive(self, packet):
        clone_pkt = Packet(
            pk=packet.pk,
            timestamp=packet.timestamp,
            rogue=packet.rogue,
            found_by=packet.found_by,
            transmitted_by=packet.transmitted_by,
            color=packet.color,
            retransmit=packet.retransmit
        )
        self.curr_signals.append(clone_pkt)

    def __str__(self) -> str:
        return f'Vessel_{self.pk}'


class RogueVessel(Node,):
    def __init__(self, total_vessel_count, config_obj) -> None:
        super().__init__(total_vessel_count, config_obj)

    def plot_node(self):
        if self.config_obj.show_graph:
            plt.scatter(self.x, self.y, s=30, facecolors='r')

    def __str__(self) -> str:
        return f'RogueVessel_{self.pk}'


class GroundStation(Node):
    def __init__(self, total_vessel_count, config_obj) -> None:
        super().__init__(total_vessel_count, config_obj)

    def plot_node(self):
        if self.config_obj.show_graph:
            plt.scatter(self.x, self.y, s=30, facecolors='b')

    def __str__(self) -> str:
        return f'GroundStation_{self.pk}'


class NormalVessel(Node):
    def __init__(self, total_vessel_count, config_obj) -> None:
        super().__init__(total_vessel_count, config_obj)
        self.neighbours = []
        self.ready = []
        self.curr_broadcast = None
        self.broadcast_cooldown = 0
        self.packet_ack = defaultdict(int)

    def __str__(self) -> str:
        return f'NormalVessel_{self.pk}'

    def plot_node(self):
        if self.config_obj.show_graph:
            plt.scatter(self.x, self.y, s=30,
                        facecolors='none', edgecolors='k')

    def plot_lines(self):
        if self.curr_signals:
            packet = self.curr_signals[0]
            self.ready.append(packet)

        return super().plot_lines()

    def is_broadcast_successful(self):
        # broadcast is successful if no overlapping signal is received currently
        # during transmission

        if not self.curr_broadcast:
            return False

        # in case of a collision the transmitter will wait for a random
        # amount of time before tring again. typical
        # TDM collision handling like CSMA/CD
        if self.curr_signals:
            self.ready.insert(0, self.curr_broadcast)

            self.broadcast_cooldown = random.randint(0, 10)

        # clear curent broadcast
        self.curr_broadcast = None
        self.curr_signals = []
        return True

    def fetch_packet_for_broadcast(self):
        if len(self.ready) == 0:
            return None

        packet = self.ready.pop(0)

        if self.prev_transmitted_packets[str(packet)]:
            return self.fetch_packet_for_broadcast()

        return packet

    def broadcast(self):
        self.broadcast_cooldown -= 1
        if self.broadcast_cooldown > 0:
            return

        packet = self.fetch_packet_for_broadcast()
        if packet is None:
            return

        packet.transmitted_by = self
        self.curr_broadcast = packet

        for nei in self.neighbours:
            nei.receive(packet)

        # to prevent the retransmission if the same packet
        # is received from the neighbour
        self.prev_transmitted_packets[str(packet)] = True


    def push_to_ready(self, rogue_vessel, total_packet_count):
        packet = Packet(
            pk=total_packet_count + 1,
            timestamp=self.config_obj.timer,
            found_by=self,
            rogue=rogue_vessel,
            transmitted_by=self,
            color=get_color(),
            retransmit = True
        )

        packet_dict[packet.pk] = packet
        self.ready.append(packet)
