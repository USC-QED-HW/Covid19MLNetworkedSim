#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import zlib
import pickle
import base64
from collections import namedtuple

from typing import *


class Split(namedtuple('Split', 'X y')):
    __slots__ = ()
    """
    Returns y but only for the specified variable.

    var_name: Valid variable name
    """

    def variable(self, var_name: str) -> np.ndarray:
        return self.y.loc[:, var_name].to_numpy()


def serialize_np(x):
    return base64.b64encode(zlib.compress(pickle.dumps(x)))


def deserialize_np(x):
    return pickle.loads(zlib.decompress(base64.b64decode(x)))

# NOTE(kosi): Assume that first column is STEP in timeseries data


def preprocess_timeseries(ts: np.ndarray, incidences: int) -> np.ndarray:
    ts[:, 1:] = ts[:, 1:] / ts[0, 1:].sum()

    old_ax = np.linspace(0, ts.shape[0], ts.shape[0])
    new_ax = np.linspace(0, ts.shape[0], incidences)

    z = np.zeros((incidences, ts.shape[1]))

    for compartment in range(ts.shape[1]):
        z[:, compartment] = np.interp(new_ax, old_ax, ts[:, compartment])

    return z


class SyntheticDataset:
    @property
    def variables(self):
        return self.y.columns

    @property
    def compartments(self):
        return ['susceptible', 'c_infected', 'recovered', 'dead']

    """
    Returns the corresponding X (timeseries data) and y (features) based on index.

    Index can either be an integer (representing position in dataset)
    or it can be a string (representing the case id.)
    """

    def __getitem__(self, index) -> Tuple[pd.Series, pd.Series]:
        if type(index) is int:
            return self.X.iloc[index], self.y.iloc[index]
        elif type(index) is str:
            return self.X.loc[index], self.y.loc[index]
        return None, None

    def __len__(self) -> int:
        return len(self._internal)

    """
    Returns a list of splits (X and y pairs).

    partition: list of fraction each split should be
    shuffle: whether or not the list should be in random order

    e.g.

    train, test = synda.split([0.7, 0.2])
    (train will be 70% of dataset, test will be 20%, rest is thrown away)
    """

    def split(self, partition: List[int] = [0.7, 0.3], shuffle: bool = True) -> List[Split]:
        remainder = 1 - sum(partition)
        assert(remainder >= 0)

        def __transform(df):
            X = df.timeseries.apply(deserialize_np)
            y = df.drop('timeseries', axis=1)

            y.network = y.network.cat.codes
            y.k = y.k.cat.codes
            y.population = y.population.cat.codes
            y.initial_infected = y.initial_infected.cat.codes

            return Split(np.array(X.tolist(), dtype=np.float), y)

        previous = 0
        length = len(self)
        for i in range(len(partition)):
            previous += partition[i]
            partition[i] = int(length*previous)

        splittable = self._internal
        if shuffle:
            splittable = splittable.sample(frac=1)

        splits = list(map(__transform, np.split(splittable, partition)))

        return splits[:len(partition)]

    # TODO(kosi): Implement chunking for larger CSVs.

    def __init__(self, csv: str = None, chunked: bool = False):
        assert(not chunked)
        if csv is None:
            csv = os.path.join(os.path.dirname(__file__),
                               'synthetic-dataset-100.csv.gz')

        df = pd.read_csv(csv, compression='gzip')

        df.network = pd.Categorical(df.network)
        df.k = pd.Categorical(df.k)
        df.population = pd.Categorical(df.population)
        df.initial_infected = pd.Categorical(df.initial_infected)

        df.set_index(["case"], inplace=True, drop=True)

        self._internal = df

        self.X = df.timeseries.apply(deserialize_np)
        self.y = df.drop('timeseries', axis=1)
