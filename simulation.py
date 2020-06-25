import random

COMPARTMENTS = ['susceptible', 'exposed', 'carrier', 'infected', 'hospitalized', 'intensive care unit', 'recovered', 'dead']

nodes = None

#SIMULATION PARAMETERS
NUM_NODES = 1000
STEPS = 100
INITIAL_INFECTED = 3


#GN PARAMETERS - geometric random network
RADIUS = 0.1 

#ER PARAMETERS - erdos-renyi 
K_MEAN = 6

#WS PARAMETERS - watts strogatz
WS_K = 4
WS_BETA = 0.2

#INFECTION PARAMETERS
GAMMA = 0.2
LAMBDA = 0.03 #NOT AT ALL CORRECT THIS REQUIRES MATHS
U_E = 1/5.2
R_C = 0.08
U_C = 1/5
R_I = 0.8
U_I = 1/5
R_H = 0.74
U_H = 1/10
R_U = 0.46
U_U = 1/8

class Node:
    def __init__(self, comp):
        self.comp = comp
        self.next_comp = comp
        self.neighbors = []

    def add_edge(self, other):
        if (self.neighbors.count(other) > 0 or other.neighbors.count(self) > 0):#TEMP
            print ("uhoh double edge")
        if (self == other): #TEMP
            print ("UH OH NODE HAS EDGE TO ITSELF") #TEMP
        self.neighbors.append(other)
        other.neighbors.append(self)
        
    ''' unnecessary    
    def del_edge(self, other):
        if (self.neighbors.count(other) == 0 or other.neighbors.count(other) == 0):#TEMP
            print ("uh oh neighbors not mutual") #TEMP
        else:
            self.neighbors.remove(other)
            other.neighbors.remove(self)
    '''

    def num_neighbors(self, compartment):
        out = 0
        for other in self.neighbors:
            if (other.comp == compartment):
                out += 1
        return out

    def has_neighbor(self, other):
        return self.neighbors.count(other) > 0


class GN_Node(Node):
    def __init__(self, x, y, comp):
        super().__init__(comp)
        self.x = x
        self.y = y
       
    def dist(self, other):
        return ((self.x-other.x)**2 + (self.y-other.y)**2)**(1/2)

class WS_Node(Node):
    def __init__(self, comp):
        super().__init__(comp)
        self.extra_edges = 0


def GN_setup():
    for i in range(NUM_NODES):
        if (i < INITIAL_INFECTED):
           nodes[i] = GN_Node(random.random(), random.random(), 2)
        else:
           nodes[i] = GN_Node(random.random(), random.random(), 0)
    for i in range(len(nodes)):
        node1 = nodes[i]
        for node2 in nodes[i+1:]:
            if (node1.dist(node2) < RADIUS):
                node1.add_edge(node2)

def CG_setup():
    for i in range(NUM_NODES):
        if (i < INITIAL_INFECTED):
            nodes[i] = Node(2)
        else:
            nodes[i] = Node(0)
    for i in range(len(nodes)):
        for node2 in nodes[i+1:]:
            nodes[i].add_edge(node2)

def ER_setup():
    for i in range(NUM_NODES):
        if (i < INITIAL_INFECTED):
            nodes[i] = Node(2)
        else:
            nodes[i] = Node(0)
    for i in range((int)(K_MEAN*len(nodes)/2)):
        node1 = nodes[random.randint(0, NUM_NODES-1)]
        node2 = nodes[random.randint(0, NUM_NODES-1)]
        while (node1 == node2 or node1.has_neighbor(node2)):
            node2 = nodes[random.randint(0, NUM_NODES-1)]
        node1.add_edge(node2)

def WS_setup():
    for i in range(NUM_NODES):
        nodes[i] = WS_Node(0)
    for i in range (NUM_NODES):
        for j in range ((int) (WS_K/2)):
            if (random.random() > WS_BETA):
                nodes[i].add_edge(nodes[(i+1+j)%NUM_NODES])
            else:
                nodes[i].extra_edges += 1
    for node1 in nodes:
        for j in range (nodes[i].extra_edges):
            node2 = nodes[random.randint(0, NUM_NODES-1)]
            while (node1 == node2 or node1.has_neighbor(node2)):
                node2 = nodes[random.randint(0, NUM_NODES-1)]
            node1.add_edge(node2)  
    set_initial_infected()
    
def set_initial_infected():
    i = INITIAL_INFECTED
    while (i > 0):
        num = random.randint(0, NUM_NODES-1)
        if (nodes[num].comp == 0):
            nodes[num].comp = 2
            nodes[num].next_comp = 2
            i -= 1

def step():
    for node in nodes:
        if (node.comp == 0):
            if (random.random() < (LAMBDA * node.num_neighbors(2) + LAMBDA * GAMMA * node.num_neighbors(3))):
                node.next_comp = 1
        elif (node.comp == 1):
            if (random.random() < U_E):
                node.next_comp = 2
        elif (node.comp == 2):
            if (random.random() < U_C):
                if (random.random() < R_C):
                    node.next_comp = 6
                else:
                    node.next_comp = 3
        elif (node.comp == 3):
            if (random.random() < U_I):
                if (random.random() < R_I):
                    node.next_comp = 6
                else:
                    node.next_comp = 4
        elif (node.comp == 4):
            if (random.random() < U_H):
                if (random.random() < R_H):
                    node.next_comp = 6
                else:
                    node.next_comp = 5
        elif (node.comp == 5):
            if (random.random() < U_U):
                if (random.random() < R_U):
                    node.next_comp = 6
                else:
                    node.next_comp = 7
    for node in nodes:
        node.comp = node.next_comp

def run(NUM_NODES_P, INITIAL_INFECTED_P, RADIUS_P, K_MEAN_P, WS_K_P, WS_BETA_P, GAMMA_P, LAMBDA_P, U_E_P, R_C_P, U_C_P, R_I_P, U_I_P, U_H_P, R_H_P, R_U_P, U_U_P, SIM_TYPE):
    global nodes, NUM_NODES, INITIAL_INFECTED, RADIUS, K_MEAN, WS_K, WS_BETA, GAMMA, LAMBDA, U_E, R_C, U_C, R_I, U_I, R_H, U_H, R_U, U_U 
    SIMS = ["GN", "ER",  "CG", "WS"]
    NUM_NODES = NUM_NODES_P
    INITIAL_INFECTED = INITIAL_INFECTED_P
    RADIUS = RADIUS_P
    K_MEAN = K_MEAN_P
    WS_K = WS_K_P
    WS_BETA = WS_BETA_P
    GAMMA = GAMMA_P
    LAMBDA = LAMBDA_P
    U_E = U_E_P
    R_C = R_C_P
    U_C = U_C_P
    R_I = R_I_P
    U_I = U_I_P
    R_H = R_H_P
    U_H = U_H_P
    R_U = R_U_P
    U_U = U_U_P

    nodes = [None] * (NUM_NODES)
    if (SIM_TYPE == 0):
        GN_setup()
    elif (SIM_TYPE == 1):
        ER_setup()
    elif (SIM_TYPE == 2):
        CG_setup()
    elif (SIM_TYPE == 3):
        WS_setup()
    else:
        print("uhoh not a sim type")
    results = [1]*8
    while (not(results[1] == 0 and results[2] == 0 and results[3] == 0 and results[4] == 0 and results[5] == 0)):
        results = [0]*8
        for node in nodes:
            results[node.comp]+=1
        print(results)
        step()
    print("done")

run(1000, 3, 0.1, 6, 4, 0.2, 0.2, 0.03, 1/5.2, 0.08, 1/5, 0.8, 1/5, 0.74, 1/10, 0.46, 1/8, 0)
