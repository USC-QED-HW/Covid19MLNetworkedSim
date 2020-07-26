#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import tarfile
import os
import time
import tempfile
import pandas as pd
from pathlib import Path
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='''Aggregates synthetic data into two files (in an tarball''')

    parser.add_argument('directory', metavar='D', nargs='?', type=str,
                        default='datasets/synthetic/', help='synthetic data directory')

    parser.add_argument('output', metavar='O', nargs='?', type=str,
                        default='datasets/', help='output directory')

    features = []
    timeseries = []
    args = parser.parse_args()

    print('Aggregating data...')
    for graph_type in tqdm(os.listdir(args.directory)):
        for id in os.listdir(Path(args.directory) / graph_type):
            case = graph_type + id

            parent = Path(args.directory) / graph_type / id

            fcsv = parent / 'features.csv'
            tcsv = parent / 'timeseries.csv'

            fdf = pd.read_csv(fcsv)
            fdf.insert(0, 'case', case)

            tdf = pd.read_csv(tcsv)
            tdf.insert(0, 'case', case)

            features.append(fdf)
            timeseries.append(tdf)

    features = pd.concat(features)
    timeseries = pd.concat(timeseries)

    features.sort_values(by=['case'], inplace=True)
    timeseries.sort_values(by=['case', 'step'], inplace=True)

    outtar = Path(args.output) / f'synthetic-{time.time()}.tar.gz'

    with tarfile.open(outtar, mode='w:gz') as archive:
        with tempfile.NamedTemporaryFile() as tf:
            timeseries.to_csv(tf.name, index=False)
            archive.add(tf.name, arcname='timeseries.csv')

        with tempfile.NamedTemporaryFile() as ff:
            features.to_csv(ff.name, index=False)
            archive.add(ff.name, arcname='features.csv')

    print("Done!")
