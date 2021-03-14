from tkinter import Pack
from matplotlib import lines
from matplotlib.markers import MarkerStyle
from copy import deepcopy
import random
from my_constants import (
    width, 
    height, 
    timer, 
    get_color, 
    clique_dist,
    time_quanta,
    ttl_acknowledgement
)
import matplotlib.pyplot as plt
from collections import defaultdict
import math
from utils import paint_debug_point


class Packet:
    def __init__(self, timestamp, rogue, found_by, transmitted_by, color, sender_list) -> None:
        self.timestamp = timestamp
        self.rogue = rogue
        self.found_by = str(found_by)
        self.transmitted_by_x = transmitted_by.x
        self.transmitted_by_y = transmitted_by.y
        self.nei = [str(x) for x in transmitted_by.neighbours]
        self.color = color
        self.sender_list = sender_list  # Will help in reducing loop transmission 

    def __str__(self):
        return f'{self.rogue}'

    def print_sender_locations(self):
        """
        For debug purposes
        Prints locations of all the previous senders.
        i.e locations of all the vessels through which this packet has travelled.
        """
        for sender in self.sender_list:
            print(f"({sender.x}, {sender.y})->")
        print("\n")


class Node:
    line = None

    def __init__(self) -> None:
        self.x = random.randint(2, width-2)
        self.y = random.randint(2, height-2)
        self.received = defaultdict(bool)
        self.curr_signals = []
        self.waiting_acknowledgement = []

    def check_acknowledgement(self, packet):
        """
        Checks if this is an acknowledgement packet or not.
        If this is acknowledgement packet : We make sure this packet is never tranmitted again,
        otherwise after TTL has passed, we transmit the packet again.
        """

        acknowledgement_packet = None
        # We can either check for direct/indirect acknowledgement
        # Direct acknowledgement : if self == packet.sender_list[-2]:
        # Indirect acknowledgement from subsequent receiver
        if self in packet.sender_list:
            acknowledgement_packet = packet

        # Check all packets waiting approval and update TTL
        buffer_list = []
        for sent_packet in self.waiting_acknowledgement:
            if acknowledgement_packet and sent_packet[0].rogue == acknowledgement_packet.rogue:
                    continue
            else:
                # If TTL has passed for a packet waiting acknowledgement, add it to ready queue
                if sent_packet[1] <= time_quanta:
                    self.ready.append(sent_packet[0])
                # Else, decease time by one time_quanta
                else:
                    buffer_list.append((sent_packet[0],sent_packet[1]-time_quanta))
        self.waiting_acknowledgement = buffer_list

    def is_receive_successful(self):
        # more than one signals with result in noise
        if len(self.curr_signals) > 1:
            self.curr_signals = []

        if self.curr_signals:
            packet = self.curr_signals[0]
            self.check_acknowledgement(packet)

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

    def receive(self, packet):
        clone_pkt = Packet(
            timestamp = packet.timestamp, 
            rogue = packet.rogue,
            found_by = packet.found_by, 
            transmitted_by = self, 
            color = packet.color,
            sender_list = packet.sender_list
        )
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
        self.received = defaultdict(bool)

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
        # mark the curr_signal as received so that
        # the node doesn't retransmit the same thing
        # again and again
        if self.curr_signals:
            packet = self.curr_signals[0]
            if self not in packet.sender_list:
                self.ready.append(packet)

        return super().plot_lines()

    def is_broadcast_successful(self):
        # broadcast is successful if no overlapping signal is received currently
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
        packet.sender_list.append(self)
        
        if self.received[str(packet)]:
            return
            
        packet.transmitted_by_x = self.x
        packet.transmitted_by_y = self.y
        packet.neighbours = [str(x) for x in self.neighbours]
        self.curr_broadcast = packet
        
        for nei in self.neighbours:
            nei.receive(packet)

        self.waiting_acknowledgement.append((packet,ttl_acknowledgement))    # Packet, TTL

        # to prevent the retransmission if the same packet
        # is received from the neighbour
        self.received[str(packet)] = True

    def push_to_ready(self, rogue_vessel):
        packet = Packet(
            timestamp = timer,
            found_by = self,
            rogue = rogue_vessel,
            transmitted_by = self,
            color = get_color(),
            sender_list = [self, ]
        )

        self.ready.append(packet)
