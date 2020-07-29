#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tarfile
import numpy as np
import pandas as pd
from typing import List
from sklearn.model_selection import train_test_split

# Get list of X values from dataset
def getX(dataset: np.ndarray) -> np.ndarray:
    return np.array(list(dataset[:, 0]))

# Get list of y values from dataset
def getY(dataset: np.ndarray) -> np.ndarray:
    return np.array(list(dataset[:, 1]))

# Split dataset into train, test, and validation
# Dataset is split into ratio (50% train, 40% test, 10% validation)
def split_dataset(Xn: np.ndarray, yn: np.ndarray, train=0.5, test=0.4) -> (np.ndarray, np.ndarray, np.ndarray):
    # Train and test must be less than 100% of the dataset
    assert(train + test < 1)

    X_train, X_test, y_train, y_test = train_test_split(Xn, yn, test_size=1-train)
    X_test, X_valid, y_test, y_valid = train_test_split(X_test, y_test, test_size=1-(test/train))

    return np.array(list(zip(X_train, y_train))), np.array(list(zip(X_test, y_test))), np.array(list(zip(X_valid, y_valid)))
def to_compartment_fraction(Xn: np.ndarray) -> np.ndarray:
    Xf = Xn.copy()
    for n in range(Xf.shape[0]):
        divisor = np.sum(Xf[n][0])
        Xf[n, :, 1:] /= divisor

    return Xf

def resample_lengths(Xn: List[np.ndarray]) -> np.ndarray:
    longest = max(Xn, key=lambda xn: xn.shape[0]).shape[0]
    new_Xn = np.zeros((len(Xn), longest, Xn[0].shape[1]))

    for k, xn in enumerate(Xn):
        old_ax = np.linspace(0, xn.shape[0], xn.shape[0])
        new_ax = np.linspace(0, xn.shape[0], longest)

        for i in range(xn.shape[1]):
            new_Xn[k, :, i] = np.interp(new_ax, old_ax, xn[:, i])

    return new_Xn

def synthetic_numpy(X: List[pd.DataFrame], y: pd.DataFrame) -> (np.ndarray, np.ndarray):
    y = y.copy()

    y['network'] = y['network'].cat.codes
    y['k'] = y['k'].cat.codes
    y['population'] = y['population'].cat.codes
    y['initial_infected'] = y['initial_infected'].cat.codes

    yn = y.loc[:, 'population':].to_numpy()
    Xn = [x.loc[:, 'step':].to_numpy() for x in X]

    return resample_lengths(Xn), yn

def import_synthetic(archive='synthetic-1595799389.927907.tar.gz', relative=False) -> (pd.DataFrame, pd.DataFrame):
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

        timeseries.index = timeseries.step

    return [v for k, v in timeseries.groupby(['case'])], features
