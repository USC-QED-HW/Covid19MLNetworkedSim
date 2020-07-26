#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tarfile
import pandas as pd
from tqdm import tqdm

def import_synthetic(archive='synthetic-1595746230.3535712.tar.gz'):
    X = []
    fn = os.path.join(os.path.dirname(__file__), archive)

    with tarfile.open(fn, 'r:gz') as tb:
        features = tb.extractfile('features.csv')
        timeseries = tb.extractfile('timeseries.csv')

        features = pd.read_csv(features)
        timeseries = pd.read_csv(timeseries)

        remove_cols = [
            'backend',
            'network_name'
        ]

        features.drop(columns=remove_cols, inplace=True)

        features['network'] = None
        features['k']       = None

        for case in tqdm(features['case'].unique()):
            network, k, _ = case.split('-')

            features.loc[features['case'] == case, 'network'] = network
            features.loc[features['case'] == case, 'k']       = k

            tdf = timeseries.loc[timeseries['case'] == case].sort_values(by=['step'])

            X.append(tdf)

        features['network']          = pd.Categorical(features['network'])
        features['k']                = pd.Categorical(features['k'])
        features['population']       = pd.Categorical(features['population'])
        features['initial_infected'] = pd.Categorical(features['initial_infected'])

    return X, features
