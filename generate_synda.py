#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
from pathlib import Path
from deserialize_network import deserialize_network
from datasets import preprocess_timeseries, serialize_np
import argparse
import pickle
import random
import sqlite3
import numpy as np
import pandas as pd
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
    network_dir = args.network_dir
    graph_type = args.graph_type
    # T_COLUMNS = model_module.T_COLUMNS
    # P_COLUMNS = model_module.P_COLUMNS

    # T_COLUMNS.insert(0, "step")

    fn = Path(network_dir) / graph_type

    with open(fn, 'rb') as f:
        graph = deserialize_network(pickle.load(f))

    return graph


"""
Resets the network
"""


def reset_network(graph):
    for node in graph:
        node.comp = 0


"""
Returns the time-series data and parameters from a simulation with randomized parameters.
"""


def random_simulation(args, graph, X):
    model = args.model
    network_name = args.graph_type
    index = args.index
    incidences = args.incidences

    model_module = discrete

    if model == ModelType.CONTINUOUS:
        model_module = continuous

    # Grossman paper has inf=3.
    inf = random.choice([2, 4, 7, 10])
    mp = model_module.ModelParameters()

    mp.population = len(graph)
    mp.initial_infected = inf
    mp.infectiousness = np.random.uniform(0.01, 0.25)

    # https://rt.live/ - based on lower and upper bounds from website
    # Based on data last collected from 7/21/20 at 5:55AM
    # lower bound (lowest estimate for utah)
    # upper bound (highest esimate for kentucky)
    r0 = np.random.uniform(0.72, 1.64)

    # R0 = k_mean * (infectiousness / (infectiousness + i_out))
    # i_out = infectiousness * ((kmean - r0) / r0)
    k = int(network_name.split('-')[1])
    network = network_name.split('-')[0]

    if model == ModelType.DISCRETE:
        mp.i_d = np.random.uniform(0.0001, 0.25)
        mp.i_r = np.random.uniform(0.001, 0.25)
    elif model == ModelType.CONTINUOUS:
        # mp.i_out            = np.random.uniform(0.0001, 1)
        mp.i_out = mp.infectiousness * ((k - r0) / r0)
        # probability that when a person leaves the infected compartment they recover
        mp.i_rec_prop = X.rvs()

    if model == ModelType.DISCRETE:
        mp.delta = 1  # 1 step = 1 day
        mp.maxtime = 500  # at most simulation will run 500 steps
    elif model == ModelType.CONTINUOUS:
        mp.sample_time = 1/10  # 1/10 steps = 1 day
        # at most simulation will run 40 steps (maximum of 400 samples)
        mp.time = int(mp.sample_time * incidences)

    timeseries = model_module.run_model(mp, graph)
    reset_network(graph)

    for i, r in enumerate(timeseries):
        r.insert(0, i)
    
    timeseries = np.array(timeseries, np.float64)
    timeseries = preprocess_timeseries(timeseries, incidences)
    timeseries = serialize_np(timeseries)

    ret = pd.Series({
        "case": network_name + "-" + str(index),
        "population": mp.population,
        "backend": str(model),
        "initial_infected": mp.initial_infected,
        "network": network,
        "k": k,
        "infectiousness": mp.infectiousness,
        "i_out": mp.i_out,
        "i_rec_prop": mp.i_rec_prop,
        "timeseries": timeseries
    })

    ret.name = ret.case

    return ret


"""
Runs if this file is ran as a script (rather than a module).
"""


def main():
    parser = argparse.ArgumentParser()

    # parser.add_argument('--n', '-N', type=int, help='number of datasets to generate')
    # parser.add_argument('--network-dir', '-W', type=str, default='networks/')
    # parser.add_argument('--results-dir', '-R', type=str, default='datasets/synthetic/')

    parser.add_argument('--model', type=ModelType,
                        default=ModelType.CONTINUOUS)
    parser.add_argument('--network-dir', '-W', type=str, default='networks/')
    parser.add_argument('--graph-type', type=str)
    parser.add_argument('--index', type=int)
    parser.add_argument('--database-name', type=str)
    parser.add_argument('--table-name', type=str)
    parser.add_argument('--incidences', type=int)
    parser.add_argument('--batch_size', type=int)
    parser.add_argument('--max', type=int, default=None)

    args = parser.parse_args()

    tb_name = args.table_name
    db_name = args.database_name
    batch_size = args.batch_size

    graph = setup(args)

    mu = 0.94
    upper = 1
    lower = 0
    sigma = 0.02

    X = stats.truncnorm((lower - mu) / sigma,
                        (upper - mu) / sigma, loc=mu, scale=sigma)

    table = []
    index = args.index

    for _ in range(index, min(args.max, index + batch_size)):
        series = random_simulation(args, graph, X)
        table.append(series)
        args.index += 1
    
    table = pd.concat(table, axis=1).T

    conn = sqlite3.connect(db_name)
    table.to_sql(tb_name, con=conn, index=False, if_exists='append')

    conn.close()


if __name__ == "__main__":
    main()
