#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
import random
import pickle
from uuid import uuid4
from enum import Enum
from tqdm import tqdm
import os
import tempfile
import shutil

def replace_dir(dir_name):
    # Remove directory if it exists and create it
    if (os.path.exists(dir_name)):
        # `tempfile.mktemp` Returns an absolute pathname of a file that 
        # did not exist at the time the call is made. We pass
        # dir=os.path.dirname(dir_name) here to ensure we will move
        # to the same filesystem. Otherwise, shutil.copy2 will be used
        # internally and the problem remains.
        tmp = tempfile.mktemp(dir=os.path.dirname(dir_name))
        # Rename the dir.
        shutil.move(dir_name, tmp)
        # And delete it.
        shutil.rmtree(tmp)


    # At this point, even if tmp is still being deleted,
    # there is no name collision.
    os.makedirs(NETWORK_FOLDER)
def dist(node1: tuple, node2: tuple):
    return ((node1[0] - node2[0])**2 + (node1[1] - node2[1])**2)**(1/2)

def gn_setup(n, radius):
    adj_list = setup_adj_list(n)
    nodes = [None] * n
    for i in range(n):
        nodes[i] = random.random(), random.random()
    for i in range(n):
        for j in range(i+1, n):
            if (dist(nodes[i], nodes[j]) < radius):
                adj_list[i].append(j)
    return adj_list

def cg_setup(n):
    adj_list = setup_adj_list(n)
    for i in range(n):
        for j in range(i+1, n):
            adj_list[i].append(j)
    return adj_list

def er_setup(n, k_mean):
    adj_list = setup_adj_list(n)
    edges = (int) (k_mean * n / 2)
    count = 0
    for i in range(n):
        j = random.randint(0, n - 1)
        while (i == j or adj_list[j].count(i) > 0):
            j = random.randint(0, n - 1)
        adj_list[i].append(j)
        count += 1
    while (count < edges):
        i = random.randint(0, n - 1)
        j = random.randint(0, n - 1)
        if (not(i == j or adj_list[i].count(j) > 0 or adj_list[j].count(i) > 0)):
            adj_list[i].append(j)
            count += 1
    return adj_list

def ws_setup(n, k, beta):
    adj_list = setup_adj_list(n)
    extra_edges = [0] * n
    for i in range (n):
        for j in range ((int) (k / 2)):
            if (random.random() > beta):
                adj_list[i].append((i + j + 1) % n)
            else:
                extra_edges[i] += 1
    for i in range(n):
        for x in range(extra_edges[i]):
            j = random.randint(0, n - 1)
            while(i == j or adj_list[i].count(j) > 0 or adj_list[j].count(i) > 0):
                j = random.randint(0, n - 1)
            adj_list[i].append(j)
    return adj_list


def ba_setup(n, m):
    adj_list = setup_adj_list(n)
    edges = [0] * n
    total_edges = 0
    for i in range(m):
        for j in range(i+1,m):
            adj_list[i].append(j)
            edges[i] += 1
            edges[j] += 1
            total_edges += 1
    for i in range(m, n):
        count = 0
        while (count < m):
            edge = random.randint(0, total_edges * 2)
            for j in range(i):
                edge -= edges[j]
                if (edge <= 0):
                    if (not(i == j or adj_list[i].count(j) > 0 or adj_list[j].count(i) > 0)):
                        adj_list[i].append(j)
                        edges[i] += 1
                        edges[j] += 1
                        count += 1
                        total_edges += 1
                    break
                else:
                    continue
                break
            else:
                continue
    return adj_list

def setup_adj_list(n):
    adj_list = [None] * n
    for i in range(n):
        adj_list[i] = []
    return adj_list

if __name__ == "__main__":
    POPULATION_SIZES = [300, 600, 1000, 2000, 4000, 7000, 10000]
    KMEAN = 6
    R = 0.1
    K = 4
    BETA = 0.2
    M = 2
    NETWORK_FOLDER = "networks"
    graphs = ['ERDOS-RENYI', 'GEOMETRIC-RANDOM', 'BARABASI-ALBERT', 'WATTS-STROGATZ']

    N = len(POPULATION_SIZES) * len(graphs)

    replace_dir(NETWORK_FOLDER)

    for i in tqdm(range(N)):
        size = POPULATION_SIZES[i // len(graphs)]
        graph = graphs[i % len(graphs)]

        adj_list = None

        if graph == 'ERDOS-RENYI':
            adj_list = er_setup(size, KMEAN)
        elif graph == 'GEOMETRIC-RANDOM':
            adj_list = gn_setup(size, R)
        elif graph == 'BARABASI-ALBERT':
            adj_list = ba_setup(size, M)
        elif graph == 'WATTS-STROGATZ':
            adj_list = ws_setup(size, K, BETA)
        else:
            raise Exception('Invalid graph')

        with open(f"{NETWORK_FOLDER}/{graph}-{size:05}--{uuid4().hex}", 'wb') as output_file:
            pickle.dump(adj_list, output_file)