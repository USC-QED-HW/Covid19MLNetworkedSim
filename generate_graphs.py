#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import pickle
from uuid import uuid4
from enum import Enum

class Compartment(Enum):
    SUSCEPTIBLE = 0
    EXPOSED = 1
    CARRIER = 2
    INFECTED = 3
    HOSPITALIZED = 4
    ICU = 5
    DEAD = 6
    RECOVERED = 7

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


def gn_setup(n, radius):
    nodes = [None] * n
    for i in range(n):
        nodes[i] = GN_Node(random.random(), random.random(), 0)
    for i in range(n):
        node1 = nodes[i]
        for node2 in nodes[i+1:]:
            if (node1.dist(node2) < radius):
                node1.add_edge(node2)
    return nodes

def cg_setup(n):
    nodes = [None] * n
    for i in range(n):
        nodes[i] = Node(0)
    for i in range(n):
        for node2 in nodes[i+1:]:
            nodes[i].add_edge(node2)
    return nodes

def er_setup(n, k_mean):
    nodes = [None] * n
    for i in range(n):
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

def ws_setup(n, k, beta):
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
    return nodes


def ba_setup(n, m):
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
    return nodes

if __name__ == "__main__":
    POPULATION_SIZES = [300, 600, 1000, 2000, 4000, 7000, 10000]
    KMEAN = 6
    R = 0.1
    K = 4
    BETA = 0.2
    M = 2
    NETWORK_FOLDER = "networks"

    for size in POPULATION_SIZES:
        er = er_setup(size, KMEAN)

        with open(f"{NETWORK_FOLDER}/er_{size}-{uuid4().hex}", 'wb') as output_file:
            pickle.dump(er, output_file)
