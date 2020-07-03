import random
import time
import queue
import numpy as np
import copy
from enum import Enum
import pandas
import multiprocessing
from multiprocessing import *

class Compartment(Enum):
    SUSCEPTIBLE = 0
    EXPOSED = 1
    CARRIER = 2
    INFECTED = 3
    HOSPITALIZED = 4
    ICU = 5
    DEAD = 6
    RECOVERED = 7

class GraphType(Enum):
    GEOMATRIC_RANDOM = 0 #GN
    ERDOS_RENYI = 1 #ER
    WATTS_STROGATZ = 2 #WS
    BARABASI_ALBERT = 3 #BA
    COMPLETE_GRAPH = 4 #CG

class ModelParameters:
    #number of nodes in the network (10^2, 10^5)
    population: int

    #number of infected nodes at the beginning of the simulation (0,small)
    initial_infected: int

    #type of network [0-3]
    graph_type: GraphType

    #variables specific to each graph type
    graph_specific_variables: list

    #probability of infection per infected neighbor (0,1)
    infectiousness: float

    #ratio of contact maintianed when infected (0-1)
    gamma: float

    #probability of moving from exposed to carrier (0-1)
    e_c: float

    #probability of moving from carrier to infected (0-1)
    c_i: float

    #probability of moving from infected to hospitalized (0-1)
    i_h: float

    #probability of moving from hospitalized to ICU (0-1)
    h_u: float

    #probability of moving from ICU to dead (0-1)
    u_d: float

    #probability of moving from carrier to recovered (0-1)
    c_r: float

    #probability of moving from infected to recovered (0-1)
    i_r: float

    #probability of moving from hospitalized to recovered (0-1)
    h_r: float

    #probability of moving from ICU to recovered (0-1)
    u_r: float



class Node:
    def __init__(self, comp: Compartment):
        self.comp = comp
        self.next_comp = comp
        self.neighbors = []
        self.time = 99999999999999999999999 #KEEP LARGER THAN THE TOTAL SIM TIME
        self.num = 0

    def add_edge(self, other):
        if (self.neighbors.count(other) > 0 or other.neighbors.count(self) > 0): #TEMP
            print ("uhoh double edge") #TEMP
        if (self == other): #TEMP
            print ("UH OH NODE HAS EDGE TO ITSELF") #TEMP
        self.neighbors.append(other)
        other.neighbors.append(self)

    def num_neighbors(self, comp: Compartment):
        out = 0
        for other in self.neighbors:
            if (other.comp == comp):
                out += 1
        return out

    def has_neighbor(self, other):
        return self.neighbors.count(other) > 0

    def set_comp(self, comp: Compartment):
        self.comp = comp
        self.next_comp = comp

    #def set_next_time(self, time):


class GN_Node(Node):
    def __init__(self, x: float, y: float, comp: Compartment):
        super().__init__(comp)
        self.x = x
        self.y = y

    def dist(self, other):
        return ((self.x-other.x)**2 + (self.y-other.y)**2)**(1/2)

class WS_Node(Node):
    def __init__(self, comp):
        super().__init__(comp)
        self.extra_edges = 0

class State_Info():
    def __init__(self, inf_rate, state):
        self.inf_rate = inf_rate
        self.state = state
    def __lt__(self, other):
        selfPriority = (self.inf_rate, self.state)
        otherPriority = (other.inf_rate, other.state)
        return selfPriority < otherPriority

def gn_setup(n, inf, radius):
    nodes = [None] * n
    for i in range(n):
        if (i < inf):
            nodes[i] = GN_Node(random.random(), random.random(), 2)
        else:
            nodes[i] = GN_Node(random.random(), random.random(), 0)
    for i in range(n):
        node1 = nodes[i]
        for node2 in nodes[i+1:]:
            if (node1.dist(node2) < radius):
                node1.add_edge(node2)
    return nodes

def cg_setup(n, inf):
    nodes = [None] * n
    for i in range(n):
        if (i < inf):
            nodes[i] = Node(2)
        else:
            nodes[i] = Node(0)
    for i in range(n):
        for node2 in nodes[i+1:]:
            nodes[i].add_edge(node2)
    return nodes

def er_setup(n, inf, k_mean):
    nodes = [None] * n
    for i in range(n):
        if (i < inf):
            nodes[i] = Node(2)
        else:
            nodes[i] = Node(0)
    for node1 in nodes:
        node2 = nodes[random.randint(0, n - 1)]
        while (node1 == node2 or node1.has_neighbor(node2)):
            node2 = nodes[random.randint(0, n - 1)]
        node1.add_edge(node2)
    for i in range((int) ((k_mean - 2) * n / 2)):
        node1 = nodes[random.randint(0, n - 1)]
        node2 = nodes[random.randint(0, n - 1)]
        while (node1 == node2 or node1.has_neighbor(node2)):
            node2 = nodes[random.randint(0, n - 1)]
        node1.add_edge(node2)
    return nodes

def ws_setup(n, inf, k, beta):
    nodes = [None] * n
    for i in range(n):
        nodes[i] = WS_Node(0)
    for i in range (n):
        for j in range ((int) (k / 2)):
            if (random.random() > beta):
                nodes[i].add_edge(nodes[(i + j + 1) % n])
            else:
                nodes[i].extra_edges += 1
    for node1 in nodes:
        for i in range (node1.extra_edges):
            node2 = nodes[random.randint(0, n - 1)]
            while (node1 == node2 or node1.has_neighbor(node2)):
                node2 = nodes[random.randint(0, n - 1)]
            node1.add_edge(node2)
    while (inf > 0):
        i = random.randint(0, n - 1)
        if (nodes[i].comp == 0):
            nodes[i].set_comp(2)
            inf -= 1
    return nodes

def ba_setup(n, inf, m):
    nodes = [None] * n
    total_edges = 0
    for i in range(n):
        nodes[i] = Node(0)
    for i in range(len(nodes[:m])):
        node1 = nodes[i]
        for node2 in nodes[i+1:m]:
            node1.add_edge(node2)
            total_edges += 1
    for i in range(m, n):
        count = 0
        while (count < m):
            edge = random.randint(0, total_edges * 2)
            for node in nodes[:i]:
                edge -= len(node.neighbors)
                if (edge <= 0):
                    if (not node.has_neighbor(nodes[i])):
                        node.add_edge(nodes[i])
                        count += 1
                        total_edges += 1
                    break
                else:
                    continue
                break
            else:
                continue
    while (inf > 0):
        i = random.randint(0, n - 1)
        if (nodes[i].comp == 0):
            nodes[i].set_comp(2)
            inf -= 1
    return nodes


def generate_time(state_list, start_time, num):
    #DEAD OR RECOVERED

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
    #print(smallest_time+start_time, " ", smallest_state)
    return smallest_time+start_time, smallest_state, num

def next_event(node, start_time, mp):
    state_list = []
    if node.comp == 0:
        if node.num_neighbors(2) + node.num_neighbors(3) == 0:
            return 99999999999999999999999, 0
        inf_rate = mp.infectiousness * node.num_neighbors(2) + mp.infectiousness * mp.gamma * node.num_neighbors(3)
        state_list.append(State_Info(inf_rate, 1))
    elif node.comp == 1:
        #print("here")
        state_list.append(State_Info(mp.e_c, 2))
    elif node.comp == 2:
        state_list.append(State_Info(mp.c_i, 3))
        state_list.append(State_Info(mp.c_r, 7))
    elif node.comp == 3:
        state_list.append(State_Info(mp.i_h, 4))
        state_list.append(State_Info(mp.i_r, 7))
    elif node.comp == 4:
        state_list.append(State_Info(mp.h_u, 5))
        state_list.append(State_Info(mp.h_r, 7))
    elif node.comp == 5:
        state_list.append(State_Info(mp.u_d, 6))
        state_list.append(State_Info(mp.u_r, 7))
    else:
        #print("DEAD OR RECOVERED")
        state_list.append(State_Info(-1, node.comp))

    return generate_time(state_list, start_time, node.num)


def run_model(mp: ModelParameters):
    graph_params = mp.graph_specific_variables
    if (mp.graph_type == 0):
        nodes = gn_setup(mp.population, mp.initial_infected, *graph_params)
    elif (mp.graph_type == 1):
        nodes = er_setup(mp.population, mp.initial_infected, *graph_params)
    elif (mp.graph_type == 2):
        nodes = ws_setup(mp.population, mp.initial_infected, *graph_params)
    elif (mp.graph_type == 3):
        nodes = ba_setup(mp.population, mp.initial_infected, *graph_params)
    elif (mp.graph_type == 4):
        nodes = cg_setup(mp.population, mp.initial_infected, *graph_params)
    else:
        print("uhoh not a sim type")
    res = []
    results = [mp.population-mp.initial_infected,0,mp.initial_infected,0,0,0,0,0]
    res.append(results)
    q=queue.PriorityQueue() #MIGHT NOT BE PROCESS SAFE - TEST!!
    markers=0
    for a in range(int(mp.time/mp.sample_time)):
        q.put((mp.sample_time*a,-1,-1))
    q.put((mp.time,-1,-1))

    #SETUP
    counter=0
    initial=[]
    for node in nodes:
        if node.comp == 2:
            node.time = 0
            #print(counter)
            initial.append(counter)
        else:
            node.time = mp.time+1
        node.num=counter
        e=next_event(node, 0, mp)
        counter+=1
        q.put(e)

    #GENERATE FOR INITIAL NEIGHBORS
    for i in initial:
        e=next_event(nodes[i], 0, mp)
        q.put(e)

    global_time=0
    prev=copy.deepcopy(res[len(res)-1])

    while global_time <= mp.time:
        current_event = q.get()

        global_time = current_event[0]
        if global_time > mp.time:
            break

        #SAMPLING
        #print(current_event)
        if current_event[2] == -1 and current_event[0] != 0:
            res.append(prev)
            prev=copy.deepcopy(res[len(res)-1])
            continue

        old_state = nodes[current_event[2]].comp
        new_state = current_event[1]

        if new_state > old_state:
            #UPDATE THE SIM
            prev[old_state]-=1
            prev[new_state]+=1

            nodes[current_event[2]].comp = new_state
            #IF YOU ARE A CARRIER, YOU HAVE ENTERED THE TRANSMISSION STAGE
            if new_state == 2:
                for n in nodes[current_event[2]].neighbors:
                    e=next_event(n, global_time, mp)
                    q.put(e)

        #GENERATE NEW EVENTS
        e=next_event(nodes[current_event[2]], global_time, mp)
        q.put(e)
    return res

def start(mp: ModelParameters):
    total=[]
    #counter=0
    for a in range(40):
        total.append(mp)

    final = []
    with Pool(40) as p:
        final.append(p.map(run_model, total))
    
    return final[0]

if __name__ == "__main__":

    mp = ModelParameters()
    mp.population = 1000 #CHANGE BACK
    mp.initial_infected = 3
    mp.graph_type = 3
    mp.graph_specific_variables = (0.1)
    mp.infectiousness = 0.05
    mp.gamma = 0.2
    mp.e_c = 0.45
    mp.c_i = 0.17
    mp.i_h = 0.1
    mp.h_u = 0.12
    mp.u_d = 0.12
    mp.c_r = 0.06
    mp.i_r = 0.15
    mp.h_r = 0.2
    mp.u_r = 0.2
    mp.time = 100
    #don't make larger than 99999999999999999999999
    mp.sample_time = 10


    #distance between nodes for edge to be added (0, 1)
    #gn_radius = 0.1

    #mean degree of network [2, small) 
    #er_k_mean = 6

    #number of neighbors per node initially (even positive int)
    #ws_k = 4 
    #probability to rewire each edge (0, 1)
    #ws_beta = 0.2 

    #amount of edges added to existing nodes for each node added
    ba_m = 2

    mp.graph_specific_variables = [ba_m]

    start(mp)