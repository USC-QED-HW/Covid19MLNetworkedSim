#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tqdm import trange
from uuid import uuid4
from enum import Enum
import argparse
import sys
import pandas as pd
import random

T_COLUMNS = None
P_COLUMNS = None

class ModelType(Enum):
    EPYDEMIC = 'epydemic'

    def __str__(self):
        return self.value
    
"""
Runs setup code needed depending on the model.
"""
def setup(model):
    global T_COLUMNS, P_COLUMNS
    if model == ModelType.EPYDEMIC:
        import epydemic_model
        T_COLUMNS = ['id'] + epydemic_model.T_COLUMNS
        P_COLUMNS = ['id'] + epydemic_model.P_COLUMNS
        return epydemic_model.setup()
    else:
        raise NotImplementedError('Rest of setup function has not been implemented.')

"""
Returns the time-series data and parameters from a simulation with randomized parameters.
"""
def random_simulation(model):
    if model == ModelType.EPYDEMIC:
        import epydemic_model
        simulation_id = uuid4().hex
        
        # choose a random graph
        graph_type = random.choice(list(epydemic_model.GraphType))
        
        if graph_type == epydemic_model.GraphType.ERDOS_RENYI:
            kmean = random.uniform(5, 7) # choose a random k_mean between 5 and 7
            N = int(random.uniform(3000, 15_000)) # choose a random population between 3K and 15K
            
            # choose a proportion of the population between 0.01% and 1% to be infected
            patients0 = int(random.uniform(0.0001, 0.01) * N)
            
            # choose the recovery rate to be between 0.02% and 10%
            beta = random.uniform(0.002, 0.1)
            
            # choose the infection rate to be between 0.2% and 10%
            alpha = random.uniform(0.02, 0.1)
            
            mp = epydemic_model.ModelParameters(
                population=N,
                graph_type=graph_type,
                graph_params=[kmean/N],
                patients0=patients0,
                alpha=alpha,
                beta=beta
            )
            
            parameters_df = [simulation_id, N, kmean, patients0, beta, alpha, str(graph_type)]
            timeseries_df = [[simulation_id] + t for t in epydemic_model.run_model(mp)]
            
            return (timeseries_df, parameters_df)
    else:
        raise Exception('Unknown simulation type')

"""
Runs if this file is ran as a script (rather than a module).
"""
def main():
    parser = argparse.ArgumentParser(description='''Generate synthetic data using graph-based,
        Monte Carlo epidemic simulations''')

    parser.add_argument('--number', '-n', type=int,
                        help='number of datasets to generate (default is 10000)',
                        default=10_000)

    parser.add_argument('--timeseries', '-t', type=argparse.FileType('w'),
                        help='output csv file for time-series data (default is stdout)',
                        default=sys.stdout)
    
    parser.add_argument('--params', '-p', type=argparse.FileType('w'),
                        help='output csv file for parameters (default is stdout',
                        default=sys.stdout)

    parser.add_argument('--model', '-m', type=ModelType, choices=list(ModelType),
                             default=ModelType.EPYDEMIC,
                             help='which type of model to use (default is epideymic)')

    args = parser.parse_args()

    number = args.number
    output_params = args.params
    output_timeseries = args.timeseries
    model = args.model
    
    if not setup(model):
        raise Exception('Error running setup code for %s model.' % str(model))

    results = [random_simulation(model) for n in trange(number)]
    
    timeseries_df = pd.DataFrame([t for result in results for t in result[0]], columns=T_COLUMNS)
    parameters_df = pd.DataFrame([result[1] for result in results], columns=P_COLUMNS)

    print('Outputting time-series data to %s' % output_timeseries)
    timeseries_df.to_csv(output_timeseries, index=False)
    
    print('Outputting parameter information to %s' % output_params)
    parameters_df.to_csv(output_params, index=False)

if __name__ == "__main__":
    main()
