#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tarfile
import numpy as np
import pandas as pd

def length_distribution(Xn):
    return np.array([x.shape[0] for x in Xn])

def synthetic_numpy(X, y):
    y = y.copy()

    y['network'] = y['network'].cat.codes
    y['k'] = y['k'].cat.codes
    y['population'] = y['population'].cat.codes
    y['initial_infected'] = y['initial_infected'].cat.codes

    return [x.loc[:, 'step':].to_numpy() for x in X], y.loc[:, 'population':].to_numpy()

def import_synthetic(archive='synthetic-1595799389.927907.tar.gz', relative=False):
    fn = archive

    if not relative:
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

        features['network'] = features.apply(lambda row: row['case'].split('-')[0], axis=1)
        features['k']       = features.apply(lambda row: row['case'].split('-')[1], axis=1)

        features['network']          = pd.Categorical(features['network'])
        features['k']                = pd.Categorical(features['k'])
        features['population']       = pd.Categorical(features['population'])
        features['initial_infected'] = pd.Categorical(features['initial_infected'])

    return [v for k, v in timeseries.groupby(['case'])], features
