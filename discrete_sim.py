#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from enum import Enum

T_COLUMNS = ['susceptible', 'infected', 'dead', 'recovered']
P_COLUMNS = ['population', 'backend', 'initial_infected', 'network_name', 'infectiousness', 'i_d', 'i_r', 'int_time', 'gamma']

'''
    SUSCEPTIBLE = 0
    INFECTED = 1
    DEAD = 2
    RECOVERED = 3
'''

class ModelParameters:
    #number of nodes in the network (10^2, 10^5)
    population: int

    #number of infected nodes at the beginning of the simulation (0,small)
    initial_infected: int

    #probability of infection per infected neighbor (0,1)
    infectiousness: float

    #probability of moving from infected to dead (0-1)
    i_d: float

    #probability of moving from infected to recovered (0-1)
    i_r: float

    # maximum number of steps the epidemic will run for (in case it never terminates)
    maxtime: int

    # determines the sample rate of the simulation, time_series information should only be captured every delta steps of the simulation
    delta: int

    #time of intervention (0-maxtime)
    int_time: int

    #intensiy of intervention (0-1)
    gamma: float

class Node:
    def __init__(self):
        self.comp = 0
        self.next_comp = 0
        self.neighbors = []
        # added for continuous sim
        self.num = 0

    def add_edge(self, other):
        self.neighbors.append(other)
        other.neighbors.append(self)

    def num_neighbors(self, comp):
        out = 0
        for other in self.neighbors:
            if (other.comp == comp):
                out += 1
        return out

    def has_neighbor(self, other):
        return self.neighbors.count(other) > 0

    def set_comp(self, comp):
        self.comp = comp
        self.next_comp = comp

    def set_num(self, num):
        self.num = num


def set_initial_infected(nodes, inf):
    while (inf > 0):
        i = random.randint(0, len(nodes) - 1)
        if (nodes[i].comp == 0):
            nodes[i].set_comp(1)
            inf -= 1

def step(mp: ModelParameters, nodes, time):
    for node in nodes:
        if (node.comp == 0):
            if (time < mp.int_time):    
                if (random.random() < (mp.infectiousness * node.num_neighbors(1))):
                    node.next_comp = 1
            else:
                if (random.random() < (mp.infectiousness * node.num_neighbors(1) * mp.gamma)):
                    node.next_comp = 1
        elif (node.comp == 1):
            x = random.random()
            if (x < mp.i_d):
                node.next_comp = 2
            elif (x < mp.i_d + mp.i_r):
                node.next_comp = 3
    for node in nodes:
        node.comp = node.next_comp

def run_model(mp: ModelParameters, nodes):
    maxtime, time_left = mp.maxtime, mp.maxtime
    delta = mp.delta
    timeseries_info = [None]*(maxtime // delta)

    set_initial_infected(nodes, mp.initial_infected)
    results = [-1]*4
    while (results[1] != 0 and time_left > 0):
        results = [0]*4
        for node in nodes:
            results[node.comp]+=1
        if (maxtime - time_left) % delta == 0:
            idx = (maxtime - time_left) // delta
            timeseries_info[idx] = results
        time_left -= 1
        step(mp, nodes, maxtime-time_left)
    timeseries_info = [inf for inf in timeseries_info if inf is not None]
    return timeseries_info
