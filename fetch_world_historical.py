#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import pandas as pd

def retrieve_owid(uri='https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'):
    df = pd.read_csv(uri)

    keep_columns = [
        'date',
        'iso_code',
        'total_cases',
        'total_tests',
        'total_deaths'
    ]

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df = df[df['iso_code'].notna()]
    return df[keep_columns].sort_values(by=['iso_code', 'date'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch COVID-19 historical data for all countries')
    parser.add_argument('outpath', nargs='?', metavar='O', type=argparse.FileType('w'), default=sys.stdout)

    args = parser.parse_args()
    outdir = args.outpath

    owid = retrieve_owid()
    owid.rename(columns={'iso_code': 'country', 'total_cases': 'positive', 'total_tests': 'totalTestResults', 'total_deaths': 'death'}, inplace=True)

    owid.to_csv(outdir, index=False)
