#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import pickle
import argparse
from enum import Enum
from tqdm import tqdm
from pathlib import Path
import os
import tempfile
import shutil
import math

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

def gn_setup(n, kmean):
    radius = (kmean/(n*math.pi))**(1/2)
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


def ba_setup(n, k):
    m = k // 2
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

def create_filename(*args):
    s = args[0]
    for arg in args[1:]:
        s += '-' + str(arg)
    return s

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='''Generate pickles for graphs''')

    parser.add_argument('-O','--outdir', type=str, help='output directory for graph')
    parser.add_argument('-G', '--graph', type=str, help='type of network')
    parser.add_argument('-K', '--k', type=int, help='average number of connected nodes')
    parser.add_argument('-N', '--number', type=int, help='population of nodes')

    args = parser.parse_args()

    filename = Path(args.outdir) / create_filename(args.graph,
                                                   args.k,
                                                   '%04d' % args.number)

    adj_list = None
    if args.graph == 'ER':
        adj_list = er_setup(args.number, args.k)
    elif args.graph == 'WS':
        adj_list = ws_setup(args.number, args.k, beta=0.2)
    elif args.graph == 'BA':
        adj_list = ba_setup(args.number, args.k)
    elif args.graph == 'GN':
        adj_list = gn_setup(args.number, kmean=args.k)

    with open(filename, 'wb') as output_file:
        pickle.dump(adj_list, output_file)
    print(filename)
