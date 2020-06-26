#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tqdm import trange
from uuid import uuid4
from enum import Enum
import argparse
import sys
import pandas as pd
import random

class ModelType(Enum):
    EPYDEMIC = 'epydemic'

    def __str__(self):
        return self.value
    
"""
Runs setup code needed depending on the model.
"""
def setup(model):
    if model == ModelType.EPYDEMIC:
        from ..epydemic_model import setup
        return setup()
    else:
        raise NotImplementedError('Rest of setup function has not been implemented.')

"""
Returns the time-series data and parameters from a simulation with randomized parameters.
"""
def random_simulation(model):
    if model == ModelType.EPYDEMIC:
        from ..epydemic_model import ModelParameters, run_model
        simulation_id = uuid4().hex
        # TODO(kosi): Implement more fine-tuned methods to generate randomized data.
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
    
    timeseries_df = pd.concat([result[0] for result in results])
    parameters_df = pd.concat([result[1] for result in results])

    print('Outputting time-series data to %s' % output_timeseries)
    timeseries_df.to_csv(output_timeseries, index=False)
    
    print('Outputting parameter information to %s' % output_params)
    parameters_df.to_csv(output_params, index=False)

if __name__ == "__main__":
    main()
