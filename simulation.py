import random
from enum import Enum

T_COLUMNS = ['timestamp', 'susceptible', 'exposed', 'carrier', 'infected', 'hospitalized', 'icu', 'dead', 'recovered']
P_COLUMNS = ['population', 'initial_infected', 'graph_type', 'graph_specific_variables', 'infectiousness',
             'gamma', 'e_c', 'i_c', 'i_h', 'h_u', 'u_d', 'c_r', 'i_r', 'h_r', 'u_r']

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

    def __str__(self):
        return self.name

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

    # maximum number of steps the epidemic will run for (in case it never terminates)
    maxtime: int

    # determines the sample rate of the simulation, time_series information should only be captured every delta steps of the simulation
    delta: int

    def __init__(self):
        self.maxtime = 10_000
        self.delta = 10



class Node:
    def __init__(self, comp: Compartment):
        self.comp = comp
        self.next_comp = comp
        self.neighbors = []

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
                for j in node.neighbors:
                    if (edge == 0):
                        if (not node.has_neighbor(nodes[i])):
                            node.add_edge(nodes[i])
                            count += 1
                            total_edges += 1
                        break
                    else:
                        edge -= 1
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


def step(mp: ModelParameters, nodes):
    for node in nodes:
        if (node.comp == 0):
            if (random.random() < (mp.infectiousness * node.num_neighbors(2) + mp.infectiousness * mp.gamma * node.num_neighbors(3))):
                node.next_comp = 1
        elif (node.comp == 1):
            if (random.random() < mp.e_c):
                node.next_comp = 2
        elif (node.comp == 2):
            x = random.random()
            if (x < mp.c_i):
                node.next_comp = 3
            elif (x < mp.c_i + mp.c_r):
                node.next_comp = 7
        elif (node.comp == 3):
            x = random.random()
            if (x < mp.i_h):
                node.next_comp = 4
            elif (x < mp.i_h + mp.i_r):
                node.next_comp = 7
        elif (node.comp == 4):
            x = random.random()
            if (x < mp.h_u):
                node.next_comp = 5
            elif (x < mp.h_u + mp.h_r):
                node.next_comp = 7
        elif (node.comp == 5):
            x = random.random()
            if (x < mp.u_d):
                node.next_comp = 6
            elif (x < mp.u_d + mp.u_r):
                node.next_comp = 7
    for node in nodes:
        node.comp = node.next_comp


def run_model(mp: ModelParameters):
    graph_params = mp.graph_specific_variables
    maxtime, time_left = mp.maxtime, mp.maxtime
    delta = mp.delta
    timeseries_info = [None]*(maxtime // delta)

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
        # print("uhoh not a sim type")
        raise Exception("Not a valid simulation type")
    results = [-1]*8
    while (not(results[1] == 0 and results[2] == 0 and results[3] == 0 and results[4] == 0 and results[5] == 0) and time_left > 0):
        results = [0]*8
        for node in nodes:
            results[node.comp]+=1
        # print(results)
        if (maxtime - time_left) % delta == 0:
            idx = (maxtime - time_left) // delta
            timeseries_info[idx] = [maxtime - time_left] + results
        time_left -= 1
        step(mp, nodes)
    # print("done")
    timeseries_info = [inf for inf in timeseries_info if inf is not None]
    return timeseries_info

# mp = ModelParameters()
# mp.population = 1000
# mp.initial_infected = 3
# mp.graph_type = 3
# mp.graph_specific_variables = (0.1)
# mp.infectiousness = 0.05
# mp.gamma = 0.2
# mp.e_c = 0.45
# mp.c_i = 0.17
# mp.i_h = 0.1
# mp.h_u = 0.12
# mp.u_d = 0.12
# mp.c_r = 0.06
# mp.i_r = 0.15
# mp.h_r = 0.2
# mp.u_r = 0.2

#distance between nodes for edge to be added (0, 1)
# gn_radius = 0.1

#mean degree of network [2, small) 
# er_k_mean = 6

#number of neighbors per node initially (even positive int)
# ws_k = 4
#probability to rewire each edge (0, 1)
#ws_beta = 0.2

#amount of edges added to existing nodes for each node added
# ba_m = 2

# mp.graph_specific_variables = [ba_m]

# results = run_model(mp)
# print(results)


''' testing that graphs are correct
nodes = gn_setup(20, 3, 0.1)
for node1 in nodes:
    print("--------")
    print(node1.x)
    print(node1.y)
    for node2 in node1.neighbors:
        print("-")
        print(node2.x)
        print(node2.y)

nodes = er_setup(10, 3, 4)
total = 0
for node1 in nodes:
    x = len(node1.neighbors)
    total += x
    print(x)
print("---")
print(total/10)

nodes = ws_setup(10, 3, 4, 0.1)
for node1 in nodes:
    for node2 in nodes:
        if (node1.has_neighbor(node2)):
            print (str(nodes.index(node1)) + "-" + str(nodes.index(node2)))

nodes = ba_setup(10, 3, 2)
for node1 in nodes:
    for node2 in nodes:
        if (node1.has_neighbor(node2)):
            print (str(nodes.index(node1)) + "-" + str(nodes.index(node2)))
'''


#WE ARE GETTING ISOLATES ON ER SHIT SHIT SHIT
'''
nodes = er_setup(10000, 3, 6)
x = 0
for node in nodes:
    if (len(node.neighbors)==0):
        x+=1
print(x)
nodes = gn_setup(1000, 3, 0.1)
x = 0
for node in nodes:
    if (len(node.neighbors)==0):
        x+=1
print(x)

nodes = ws_setup(10000, 3, 4, 0.2)
x = 0
for node in nodes:
    if (len(node.neighbors)==0):
        x+=1
print(x)

nodes = ba_setup(1000, 3, 2)
x = 0
for node in nodes:
    if (len(node.neighbors)==0):
        x+=1
print(x)
'''
