#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import tarfile
import numpy as np
import pandas as pd

"""
Represents a split of a synthetic dataset.
"""
class SyntheticSplit:
    def __len__(self):
        return len(self.y)

    """
    Returns an np.array of one-hot encoded vectors based on column name.

    column_name: Name of column to return as one-hot encoded vectors.
    """
    def categorical_tensor(self, column_name: str) -> np.ndarray:
        assert(column_name in self.parent.categorical_vars)
        assert(column_name in self.parent.variables)

        column_idx = self.column_index[column_name]

        a = self.y[:, column_idx].astype(int)
        b = np.zeros((a.size, self.column_lengths[column_idx]))

        b[np.arange(a.size), a] = 1

        return b

    """
    Returns an np.array based on column name.
    Column must be a quantitative variable.

    column_name: Name of column to return.
    """
    def quantitative_tensor(self, column_name: str) -> np.ndarray:
        assert(column_name not in self.parent.categorical_vars)
        assert(column_name in self.parent.variables)

        column_idx = self.column_index[column_name]

        return self.y[:, column_idx]

    """
    Returns both the X and y tensors for given column name.

    column_name: Name of column to return.
    """
    def tensors(self, column_name: str = None) -> np.ndarray:
        if column_name is None:
            return self.X, self.y

        return self.X, self.feature_tensor(column_name)

    """
    Returns an np.array based on column name.
    Column can either be quantitative or categorical.

    column_name: Name of column to return.
    """
    def feature_tensor(self, column_name: str) -> np.ndarray:
        if column_name in self.parent.categorical_vars:
            return self.categorical_tensor(column_name)
        return self.quantitative_tensor(column_name)

    def __init__(self, split, parent):
        self.parent = parent

        self.X = np.array([list(row) for row in split[:, 0]])
        self.y = np.array([list(row) for row in split[:, 1]])

        self.column_index = {v: k for k, v in enumerate(parent.variables)}

        self.column_lengths = [
            len(parent.y[v].cat.categories) if v in parent.categorical_vars else None
            for v in parent.variables
        ]

"""
Represents a synthetic dataset used for training.
"""
class SyntheticDataset:
    """
    Returns the X (data) and y (features) from the dataset by case.

    case: Case identifier (e.g. BA-10000100).
    """
    def get_by_case(self, case: str) -> (pd.DataFrame, pd.DataFrame):
        return self.X[self.X.case == case], self.y[self.y.case == case]

    def __iter__(self):
        self.current = 0
        return self

    def __next__(self):
        if (self.current >= len(self)):
            raise StopIteration
        self.current += 1
        return self[self.current - 1]

    """
    Returns the list of variables in the dataset.
    """
    @property
    def variables(self) -> list:
        return self.y.columns[1:]

    """
    Returns the list of categorical variables in the dataset.
    """
    @property
    def categorical_vars(self) -> list:
        return list(filter(lambda x: self.y[x].dtype.name == 'category' , self.variables))

    """
    Preprocess and split dataset to be used by a machine learning library.

    train: Percentage of dataset to split into training data. (default=0.7)
    test: Percentage of dataset to split into testing data. (default=0.2)
    valid: If True, split dataset into validation as well (default=False)

    Returns: A tuple of three SyntheticSplits (train, test, validation)
    """
    def split(self, train: float = 0.7, test: float = 0.2, valid: bool = False):
        assert(train + test <= 1)

        y = self.y.copy()
        X = self.X.copy()

        y = y[self.variables]

        y['network'] = y['network'].cat.codes
        y['k'] = y['k'].cat.codes
        y['population'] = y['population'].cat.codes
        y['initial_infected'] = y['initial_infected'].cat.codes

        yn = y.to_numpy()
        Xn = [x.to_numpy()[:, 1:].astype(float) for _, x in X.groupby(['case'])]
        Xn = SyntheticDataset.__resample(Xn)
        Xn = SyntheticDataset.__fraction(Xn)

        whole = list(zip(Xn, yn))
        l = len(whole)

        split = np.split(whole, [int(l*train), int(l*test + l*train)])
        split = tuple(SyntheticSplit(x, self) for x in split)

        if valid:
            return split

        return split[:-1]

    """
    Returns the X (data) and y (features) from the dataset by index.
    """
    def __getitem__(self, index: int) -> (pd.DataFrame, pd.DataFrame):
        return self.X_index[index], self.y.iloc[index]

    """
    Returns the length of the dataset.
    """
    def __len__(self) -> int:
        return len(self.y)

    """
    Returns the name of the category given the cateogrical code.

    column_name: Name of categorical variable ('k', 'network', 'initial_infected', population')
    code: The code corresponding to a categorical variable (e.g. BA = 0, ER = 1, etc.)

    e.g.
        a = SyntheticDataset()
        print(a.get_category_by_code['network', 0])

        > 'BA'
    """
    def get_category_by_code(self, column_name: str, code: int) -> str:
        return self.y[column_name].cat.categories[code]

    """
    Resamples time-series data so that they are all the same duration.

    X: list of ndarrays that represent time-series data
    """
    def __resample(X: list) -> np.ndarray:
        longest = max(X, key=lambda xn: xn.shape[0]).shape[0]
        new_Xn = np.zeros((len(X), longest, X[0].shape[1]))

        for k, xn in enumerate(X):
            old_ax = np.linspace(0, xn.shape[0], xn.shape[0])
            new_ax = np.linspace(0, xn.shape[0], longest)

            for i in range(xn.shape[1]):
                new_Xn[k, :, i] = np.interp(new_ax, old_ax, xn[:, i])

        return new_Xn

    """
    Converts each timeseries data to fractions.
    """
    def __fraction(X: np.ndarray) -> np.ndarray:
        Xf = X.copy()
        for n in range(X.shape[0]):
            divisor = np.sum(X[n][0])
            X[n, :, 1:] /= divisor

        return X

    """
    Initializes the synthetic dataset.

    archive: Path to archive file that holds synthetic dataset.
    cumulative: If false, sets the timeseries data to be new infected/dead/recovered by step rather than cumulative.
    """
    def __init__(self, archive: str = None, cumulative: bool = True):
        if archive is None:
            archive = os.path.join(os.path.dirname(__file__), 'synthetic-1595799389.927907.tar.gz')

        with tarfile.open(archive, 'r:gz') as tb:
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

            self.y = features
            self.X = timeseries

            self.X_index = [v for k, v in timeseries.groupby(['case'])]

            if not cumulative:
                for i in range(len(self)):
                    x, y = self[i]
                    x['c_infected'] = x['c_infected'].diff()
                    x['recovered']  = x['recovered'].diff()
                    x['dead']       = x['dead'].diff()

                    x.loc[0, 'c_infected'] = y['initial_infected']
                    x.loc[0, 'recovered']  = 0
                    x.loc[0, 'dead']       = 0

            timeseries.index = timeseries.step
