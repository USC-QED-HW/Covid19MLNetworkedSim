#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tqdm import trange
from uuid import uuid4
from enum import Enum
from deserialize_network import deserialize_network
import argparse
import sys
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
def setup(network_dir, results_dir):
    global T_COLUMNS, P_COLUMNS
    T_COLUMNS = discrete.T_COLUMNS
    P_COLUMNS = discrete.P_COLUMNS
    graphs = dict()

    # Load in all the graphs
    for file in os.listdir(network_dir):
        filepath = os.path.join(network_dir, file)

        with open(filepath, 'rb') as f:
            graphs[file] = deserialize_network(pickle.load(f))

    if len(graphs) == 0:
        raise Exception(f"No graphs found in {network_dir}")

    # Create a results directory if it does not exist
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    return graphs

def random_fsm_prob():
    return max(0.0001, random.uniform(0.0, 0.5))

"""
Returns the time-series data and parameters from a simulation with randomized parameters.
"""
def random_simulation(model, graphs):
    if model == ModelType.DISCRETE or model == ModelType.CONTINUOUS:
        simulation_id = uuid4().hex

        model_module = discrete

        if model == ModelType.CONTINUOUS:
            model_module = continuous

        network_name, network = random.choice(list(graphs.items()))

        # Grossman paper has inf=3.
        inf = random.randint(1, 10)

        infectiousness = random.uniform(0.01, 0.12)

        gamma = random.uniform(0.1, 1.0)

        mp = model_module.ModelParameters()
        mp.population = len(network)
        mp.initial_infected = inf
        mp.infectiousness = infectiousness
        mp.gamma = gamma
        mp.e_c = random_fsm_prob()
        mp.c_i = random_fsm_prob()
        mp.c_r = random_fsm_prob()
        mp.i_h = random_fsm_prob()
        mp.h_u = random_fsm_prob()
        mp.u_d = random_fsm_prob()
        mp.i_r = random_fsm_prob()
        mp.h_r = random_fsm_prob()
        mp.u_r = random_fsm_prob()

        if model == ModelType.DISCRETE:
            mp.delta = 1 # sample every step of the simulation
            mp.maxtime = 10_000
        elif model == ModelType.CONTINUOUS:
            mp.time = 10_000
            mp.sample_time = 10

        timeseries_tbl = model_module.run_model(mp, network)
        parameters_tbl = [None]*len(P_COLUMNS)

        if model == ModelType.CONTINUOUS:
            n = len(timeseries_tbl)
            dt = mp.sample_time

            for i in range(n):
                timeseries_tbl[i].insert(1, dt * i)

        mp.network_name = network_name

        for idx, col in enumerate(P_COLUMNS):
            parameters_tbl[idx] = getattr(mp, col)

        return (timeseries_tbl, parameters_tbl, simulation_id)

    else:
        raise Exception('Unknown simulation type')

"""
Runs if this file is ran as a script (rather than a module).
"""
def main():
    parser = argparse.ArgumentParser(description='''Generate synthetic data using graph-based,
        Monte Carlo epidemic simulations''')

    parser.add_argument('--number', '-n', type=int,
                        help='number of datasets to generate (default is 1)',
                        default=1)

    parser.add_argument('--model', '-m', type=ModelType, choices=list(ModelType),
                        default=ModelType.DISCRETE,
                        help='which type of model to use (default is discrete)')

    parser.add_argument('--network-dir', type=str, default='networks/',
                        help='directory which networks are stored in (default is networks/)')

    parser.add_argument('--results-dir', type=str, default='datasets/synthetic/',
                        help='directory which simulation results are stored in (default is datasets/synthetic/)')

    args = parser.parse_args()

    N = args.number
    model = args.model
    network_dir = args.network_dir
    results_dir = args.results_dir

    graphs = setup(network_dir, results_dir)

    for i in trange(N):
        tt, pt, sim_id = random_simulation(model, graphs)

        subdir = os.path.join(results_dir, sim_id)

        # Create subdirectory (wont exist because UUID collisions are neigh impossible)
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


if __name__ == "__main__":
    main()
