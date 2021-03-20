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


class Packet:
    def __init__(self, pk, timestamp, rogue, found_by, transmitted_by, color, sender_list) -> None:
        self.pk = pk
        self.timestamp = timestamp
        self.rogue = rogue
        self.found_by = str(found_by)
        self.transmitted_by = transmitted_by
        self.nei = [str(x) for x in transmitted_by.neighbours]
        self.color = color
        self.sender_list = sender_list  # Will help in reducing loop transmission 

    def __str__(self):
        return f'Packet_{self.pk}'

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

    def __init__(self, total_vessel_count, config_obj) -> None:
        self.config_obj = config_obj
        self.pk = total_vessel_count
        self.x = random.randint(2, self.config_obj.width-2)
        self.y = random.randint(2, self.config_obj.height-2)
        self.received = defaultdict(bool)
        self.curr_signals = []
        self.waiting_acknowledgement = []

    def check_acknowledgement(self, packet):
        """
        Checks if this is an acknowledgement packet or not.
        If this is acknowledgement packet : We make sure this packet is never trasnmitted again,
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
                    # For debug purposes
                    # print(acknowledgement_packet)
                    if DEBUG and track_packet and acknowledgement_packet.pk==track_packet_id:
                        print(f"{acknowledgement_packet} ack received by {self} from {acknowledgement_packet.transmitted_by}")            
                    continue
            else:
                # If TTL has passed for a packet waiting acknowledgement, add it to ready queue
                if sent_packet[1] <= self.config_obj.time_quanta:
                    self.ready.append(sent_packet[0])
                # Else, decease time by one time_quanta
                else:
                    buffer_list.append((sent_packet[0],sent_packet[1]-self.config_obj.time_quanta))
        self.waiting_acknowledgement = buffer_list

    def is_receive_successful(self):
        # more than one signals with result in noise
        reception = len(self.curr_signals) > 0
        reception_packet_pk = None

        if len(self.curr_signals) > 1:
            self.curr_signals = []

        if self.curr_signals:
            packet = self.curr_signals[0]
            reception_packet_pk = packet.pk
            # For debug purposes
            if DEBUG and track_packet and packet.pk==track_packet_id:
                print(f"{packet} received by {self} from {packet.transmitted_by}")            
                    
            self.check_acknowledgement(packet)
        
        return reception, reception_packet_pk

    def plot_lines(self):
        # deleting the previous plotted line
        if self.line:
            self.line.pop().remove()

        if self.curr_signals:
            packet = self.curr_signals.pop()
            self.line = plt.plot(
                [self.x, packet.transmitted_by.x],
                [self.y, packet.transmitted_by.y],
                packet.color)

    def receive(self, packet):
        clone_pkt = Packet(
            pk = packet.pk,
            timestamp = packet.timestamp, 
            rogue = packet.rogue,
            found_by = packet.found_by, 
            transmitted_by = packet.transmitted_by, 
            color = packet.color,
            sender_list = packet.sender_list
        )
        self.curr_signals.append(clone_pkt)

    def __str__(self) -> str:
        return f'Vessel_{self.pk}'


class RogueVessel(Node,):
    def __init__(self, total_vessel_count, config_obj) -> None:
        super().__init__(total_vessel_count, config_obj)
    
    def plot_node(self):
        plt.scatter(self.x, self.y, s=30, facecolors='r')

    def __str__(self) -> str:
        return f'RogueVessel_{self.pk}'


class GroundStation(Node):
    def __init__(self, total_vessel_count, config_obj) -> None:
        super().__init__(total_vessel_count, config_obj)
        self.received = defaultdict(bool)

    def plot_node(self):
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

    def __str__(self) -> str:
        return f'NormalVessel_{self.pk}'

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

    def broadcast(self):
        self.broadcast_cooldown -= 1

        if not self.ready or self.broadcast_cooldown > 0:
            return

        packet = self.ready.pop(0)
        packet.sender_list.append(self)
        
        if self.received[str(packet)]:
            return
            
        packet.transmitted_by = self
        packet.neighbours = [str(x) for x in self.neighbours]
        self.curr_broadcast = packet
        
        for nei in self.neighbours:
            # For debug purposes
            if DEBUG and track_packet and packet.pk==track_packet_id:
                print(f"{packet} received by {nei} from {self}")            
            
            nei.receive(packet)

        self.waiting_acknowledgement.append((packet, self.config_obj.ttl_acknowledgement))    # Packet, TTL

        # to prevent the retransmission if the same packet
        # is received from the neighbour
        self.received[str(packet)] = True

    def push_to_ready(self, rogue_vessel, total_packet_count):
        packet = Packet(
            pk = total_packet_count + 1,
            timestamp = self.config_obj.timer,
            found_by = self,
            rogue = rogue_vessel,
            transmitted_by = self,
            color = get_color(),
            sender_list = [self, ]
        )
        
        # For debug purposes
        if DEBUG and track_packet and packet.pk==track_packet_id:
            print(f"{packet} created by ", self)

        self.ready.append(packet)
