#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import queue
import numpy as np
import copy
from enum import Enum
import matplotlib.pyplot as plt
#from discrete_sim import ModelParameters

T_COLUMNS = ['susceptible', 'c_infected', 'recovered', 'dead']
P_COLUMNS = ['population', 'backend', 'initial_infected', 'network_name', 'infectiousness', 'i_out', 'i_rec_prop']

class ModelParameters:
    #number of nodes in the network (10^2, 10^5)
    population: int

    #number of infected nodes at the beginning of the simulation (0,small)
    initial_infected: int

    #probability of infection per infected neighbor (0,1)
    infectiousness: float

    #probability of moving from infected to dead (0-1)
    i_out: float

    #probability of moving from infected to recovered (0-1)
    i_rec_prop: float

    # maximum number of steps the epidemic will run for (in case it never terminates)
    maxtime: int

    # determines the sample rate of the simulation, time_series information should only be captured every delta steps of the simulation
    delta: int

class State_Info():
    def __init__(self, inf_rate, state):
        self.inf_rate = inf_rate
        self.state = state
    def __lt__(self, other):
        selfPriority = (self.inf_rate, self.state)
        otherPriority = (other.inf_rate, other.state)
        return selfPriority < otherPriority

def generate_time(state_list, start_time, num, eventid):

    if state_list[0].inf_rate == -1:
        return 99999999999999999999999, state_list[0].state

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
    return smallest_time+start_time, smallest_state, num, eventid

def next_event(node, start_time, mp):
    node.set_eventID(node.eventID+1)
    state_list = []
    if node.comp == 0:
        if node.num_neighbors(1) == 0:
            return 99999999999999999999999, 0
        inf_rate = mp.infectiousness * node.num_neighbors(1)
        state_list.append(State_Info(inf_rate, 1))
    elif node.comp == 1:
        state_list.append(State_Info(mp.i_out * (mp.i_rec_prop), 2))
        state_list.append(State_Info(mp.i_out * (1 - mp.i_rec_prop), 3))
    else:
        state_list.append(State_Info(-1, node.comp))

    return generate_time(state_list, start_time, node.num, node.eventID)

def set_initial_infected(nodes, inf):
    while (inf > 0):
        i = random.randint(0, len(nodes) - 1)
        if (nodes[i].comp == 0):
            nodes[i].set_comp(1)
            inf -= 1

def run_model(mp: ModelParameters, nodes):
    set_initial_infected(nodes, mp.initial_infected)
    res = []
    c_inf_res = []
    results = [mp.population-mp.initial_infected,mp.initial_infected,0,0]
    c_inf_results = [mp.population-mp.initial_infected,mp.initial_infected,0,0]
    res.append(results)
    c_inf_res.append(c_inf_results)

    q=queue.PriorityQueue()
    markers=0
    for a in range(int(mp.time/mp.sample_time)):
        q.put((mp.sample_time*a,-1,-1))
    q.put((mp.time,-1,-1))

    #SETUP
    counter=0
    for node in nodes:
        node.set_num(counter)
        e=next_event(node, 0, mp)
        counter+=1
        q.put(e)

    global_time=0
    prev=copy.deepcopy(res[len(res)-1])
    c_inf_prev=copy.deepcopy(res[len(res)-1])

    while (global_time <= mp.time) and prev[1] != 0:
        current_event = q.get()
        global_time = current_event[0]
        if global_time > mp.time:
            break

        #SAMPLING
        if current_event[2] == -1 and current_event[0] != 0:
            res.append(prev)
            prev=copy.deepcopy(res[len(res)-1])

            c_inf_res.append(c_inf_prev)
            c_inf_prev=copy.deepcopy(c_inf_res[len(c_inf_res)-1])
            continue

        old_state = nodes[current_event[2]].comp
        new_state = current_event[1]

        if new_state > old_state and old_state != 2 and nodes[current_event[2]].eventID == current_event[3]:
            #UPDATE THE SIM
            prev[old_state]-=1
            prev[new_state]+=1

            if old_state == 0:
                c_inf_prev[old_state]-=1
            c_inf_prev[new_state]+=1

            nodes[current_event[2]].comp = new_state
            #TRANSMISSION
            if new_state == 1:
                for n in nodes[current_event[2]].neighbors:
                    e=next_event(n, global_time, mp)
                    q.put(e)

        #GENERATE NEW EVENT
        e=next_event(nodes[current_event[2]], global_time, mp)
        q.put(e)
        
    if prev[1] == 0:
        res.append(prev)
        c_inf_res.append(c_inf_prev)

    # sub, c_inf, rec, dead
    return c_inf_res