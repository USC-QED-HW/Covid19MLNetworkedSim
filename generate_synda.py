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
def random_simulation(model, network, network_name):
    if model == ModelType.DISCRETE or model == ModelType.CONTINUOUS:
        model_module = discrete

        if model == ModelType.CONTINUOUS:
            model_module = continuous

        # Grossman paper has inf=3.
        inf = random.choice([2, 4, 7, 10])
        mp  = model_module.ModelParameters()

        mp.population       = len(network)
        mp.initial_infected = inf
        mp.infectiousness   = random.uniform(0.01, 0.25)

        if model == ModelType.DISCRETE:
            mp.i_d              = random.uniform(0.0001, 0.25)
            mp.i_r              = random.uniform(0.001, 0.25)
        elif model == ModelType.CONTINUOUS:
            mp.i_out            = random.uniform(0.0001, 1)
            mp.i_rec_prop       = random.uniform(0.85, 1)

        if model == ModelType.DISCRETE:
            mp.delta = 1 # sample every step of the simulation
            mp.maxtime = 500
        elif model == ModelType.CONTINUOUS:
            mp.time = 500
            mp.sample_time = 1/10 # sample every step of the simulation

        timeseries_tbl = model_module.run_model(mp, network)
        reset_network(network)
        parameters_tbl = [None]*len(P_COLUMNS)

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

    for sim in range(N):
        tt, pt = random_simulation(model, graph, graph_type)

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

    print(output_path)

if __name__ == "__main__":
    main()
