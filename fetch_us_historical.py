#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import pandas as pd

def retrieve_tracking(uri="https://covidtracking.com/api/v1/states/daily.csv"):
    df = pd.read_csv(uri)

    keep_columns = [
        'date',
        'state',
        'positive',
        'negative',
        'totalTestResults',
        'death',
    ]

    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df.fillna(0, inplace=True)
    df[['positive', 'negative', 'death', 'totalTestResults']] = df[['positive', 'negative', 'death', 'totalTestResults']].astype(int)
    return df[keep_columns].sort_values(by=['state', 'date'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch COVID-19 historical data for US states/territories')
    parser.add_argument('outpath', nargs='?', metavar='O', type=argparse.FileType('w'), default=sys.stdout)

    args = parser.parse_args()
    outdir = args.outpath

    tracking = retrieve_tracking()
    tracking.to_csv(outdir, index=False)
