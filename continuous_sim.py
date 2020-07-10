#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import time
import queue
import numpy as np
import copy
from enum import Enum
import pandas
import multiprocessing
from multiprocessing import *
from discrete_sim import T_COLUMNS, P_COLUMNS, ModelParameters

class State_Info():
    def __init__(self, inf_rate, state):
        self.inf_rate = inf_rate
        self.state = state
    def __lt__(self, other):
        selfPriority = (self.inf_rate, self.state)
        otherPriority = (other.inf_rate, other.state)
        return selfPriority < otherPriority

class PQ_Elements():
    def __init__(self, time, state, node):
        self.time = time
        self.state = state
        self.node = node
    def __lt__(self, other):
        selfPriority = (self.time, self.state)
        otherPriority = (other.time, other.state)
        return selfPriority < otherPriority


def generate_time(state_list, start_time, node):
    #DEAD OR RECOVERED

    if state_list[0].inf_rate == -1:
        return PQ_Elements(99999999999999999999999, state_list[0].state, node)

    smallest_time = -1
    smallest_state = state_list[0].state
    for a in state_list:
        fire_time=(-np.log(random.random()) / a.inf_rate)
        if smallest_time == -1:
            smallest_time = fire_time
            smallest_state = a.state
        elif fire_time < smallest_time:
            smallest_time = fire_time
            smallest_state = a.state
    return PQ_Elements(smallest_time+start_time, smallest_state, node)

def next_event(node, start_time, mp):
    state_list = []
    if node.comp == 0:
        if node.num_neighbors(1) == 0:
            return PQ_Elements(99999999999999999999999, 0, node)
        inf_rate = mp.infectiousness * node.num_neighbors(1)
        state_list.append(State_Info(inf_rate, 1))
    elif node.comp == 1:
        #print("here")
        state_list.append(State_Info(mp.i_r, 2))
        state_list.append(State_Info(mp.i_d, 3))
    else:
        #print("DEAD OR RECOVERED")
        state_list.append(State_Info(-1, node.comp))

    return generate_time(state_list, start_time, node)

def set_initial_infected(nodes, inf):
    while (inf > 0):
        i = random.randint(0, len(nodes) - 1)
        if (nodes[i].comp == 0):
            nodes[i].set_comp(2)
            inf -= 1

def run_model(mp: ModelParameters, nodes):
    set_initial_infected(nodes, mp.initial_infected)

    holder = copy.deepcopy(nodes[0])
    res = []
    results = [mp.population-mp.initial_infected,mp.initial_infected,0,0]
    res.append(results)
    q=queue.PriorityQueue() #MIGHT NOT BE PROCESS SAFE - TEST!!
    markers=0
    for a in range(int(mp.time/mp.sample_time)):
        q.put(PQ_Elements(mp.sample_time*a,-1,holder))
    q.put(PQ_Elements(mp.time,-1,holder))

    #SETUP
    for node in nodes:
        e=next_event(node, 0, mp)
        q.put(e)

    global_time=0
    prev=copy.deepcopy(res[len(res)-1])

    while (global_time <= mp.time) and not(prev[1] == 0):
        current_event = q.get()

        global_time = current_event.time
        if global_time > mp.time:
            break

        #SAMPLING
        if current_event.state==-1:
            res.append(prev)
            prev=copy.deepcopy(res[len(res)-1])
            continue

        old_state = current_event.node.comp
        new_state = current_event.state

        if new_state > old_state:
            #UPDATE THE SIM
            prev[old_state]-=1
            prev[new_state]+=1

            current_event.node.comp = new_state
            #IF YOU ARE EXPOSED, YOU HAVE ENTERED THE TRANSMISSION STAGE
            if new_state == 1:
                for n in current_event.node.neighbors:
                    e=next_event(n, global_time, mp)
                    q.put(e)

        #GENERATE NEW EVENT
        e=next_event(current_event.node, global_time, mp)
        q.put(e)

    return res