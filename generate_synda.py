#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
from pathlib import Path
from deserialize_network import deserialize_network
import argparse
import os
import pickle
import random
import csv
import math
import numpy as np
import scipy.stats as stats
import continuous_sim as continuous
import discrete_sim as discrete

T_COLUMNS = None
P_COLUMNS = None

class ModelType(Enum):
    DISCRETE = 'DISCRETE'
    CONTINUOUS = 'CONTINUOUS'

    def __str__(self):
        return self.name

"""
Runs setup code needed depending on the model.
"""
def setup(args):
    global T_COLUMNS, P_COLUMNS

    model_module = continuous if args.model == ModelType.CONTINUOUS else discrete
    network_dir  = args.network_dir
    graph_type   = args.graph_type
    results_dir  = args.results_dir
    T_COLUMNS    = model_module.T_COLUMNS
    P_COLUMNS    = model_module.P_COLUMNS

    T_COLUMNS.insert(0, "step")

    fn = Path(network_dir) / graph_type

    with open(fn, 'rb') as f:
        graph = deserialize_network(pickle.load(f))

    output_path = Path(results_dir) / os.path.basename(fn)

    os.makedirs(output_path)

    return graph, output_path

"""
Resets the network
"""
def reset_network(graph):
    for node in graph:
        node.comp = 0

"""
Returns the time-series data and parameters from a simulation with randomized parameters.
"""
def random_simulation(model, network, network_name, X):
    if model == ModelType.DISCRETE or model == ModelType.CONTINUOUS:
        model_module = discrete

        if model == ModelType.CONTINUOUS:
            model_module = continuous

        # Grossman paper has inf=3.
        inf = random.choice([2, 4, 7, 10])
        mp  = model_module.ModelParameters()

        mp.population       = len(network)
        mp.initial_infected = inf
        mp.infectiousness   = np.random.uniform(0.01, 0.25)

        # https://rt.live/ - based on lower and upper bounds from website
        # Based on data last collected from 7/21/20 at 5:55AM
        # lower bound (lowest estimate for utah)
        # upper bound (highest esimate for kentucky)
        r0 = np.random.uniform(0.72, 1.64)

        # R0 = k_mean * (infectiousness / (infectiousness + i_out))
        # i_out = infectiousness * ((kmean - r0) / r0)
        kmean = int(network_name.split('-')[1])

        if model == ModelType.DISCRETE:
            mp.i_d              = np.random.uniform(0.0001, 0.25)
            mp.i_r              = np.random.uniform(0.001, 0.25)
        elif model == ModelType.CONTINUOUS:
            # mp.i_out            = np.random.uniform(0.0001, 1)
            mp.i_out            = mp.infectiousness * ((kmean - r0) / r0)
            mp.i_rec_prop       = X.rvs() # probability that when a person leaves the infected compartment they recover

        if model == ModelType.DISCRETE:
            mp.delta = 1 # 1 step = 1 day
            mp.maxtime = 500 # at most simulation will run 500 steps
        elif model == ModelType.CONTINUOUS:
            mp.sample_time = 1/10 # 1/10 steps = 1 day
            mp.time = 40 # at most simulation will run 40 steps (maximum of 400 samples)

        timeseries_tbl = model_module.run_model(mp, network)
        reset_network(network)
        parameters_tbl = [None]*len(P_COLUMNS)

        for i, r in enumerate(timeseries_tbl):
            r.insert(0, i)

        mp.network_name = network_name
        mp.backend = model

        for idx, col in enumerate(P_COLUMNS):
            parameters_tbl[idx] = getattr(mp, col)

        return (timeseries_tbl, parameters_tbl)

    else:
        raise Exception('Unknown simulation type')

"""
Runs if this file is ran as a script (rather than a module).
"""
def main():
    parser = argparse.ArgumentParser(description='''Generate synthetic data using simulation''')

    parser.add_argument('--model', '-M', type=ModelType, choices=list(ModelType),
                        default=ModelType.CONTINUOUS,
                        help='which type of model to use (default is discrete)')

    parser.add_argument('--n', '-N', type=int, help='number of datasets to generate')

    parser.add_argument('--network-dir', '-W', type=str, default='networks/',
                        help='directory which networks are stored in (default is networks/)')

    parser.add_argument('--graph-type', '-G', type=str, help='what type of graph to use')

    parser.add_argument('--results-dir', '-R', type=str, default='datasets/synthetic/',
                        help='directory which simulation results are stored in (default is datasets/synthetic/)')

    args = parser.parse_args()

    model      = args.model
    N          = args.n
    graph_type = args.graph_type

    graph, output_path = setup(args)
    l = len(str(N))

    mu = 0.94
    upper = 1
    lower = 0
    sigma = 0.02

    X = stats.truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)

    for sim in range(N):
        tt, pt = random_simulation(model, graph, graph_type, X)

        subdir = os.path.join(output_path, f"%0{l}d" % sim)

        os.makedirs(subdir)

        timeseries_path = os.path.join(subdir, 'timeseries.csv')
        features_path = os.path.join(subdir, 'features.csv')

        with open(timeseries_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(T_COLUMNS)

            for row in tt:
                writer.writerow(row)

        with open(features_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(P_COLUMNS)
            writer.writerow(pt)

    # print(output_path)

if __name__ == "__main__":
    main()
