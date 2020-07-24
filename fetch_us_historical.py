#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import pandas as pd

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

def retrieve_tracking(uri="https://covidtracking.com/api/v1/states/daily.csv"):
    df = pd.read_csv(uri)

    keep_columns = [
        'date',
        'state',
        'positive',
        'negative',
        'totalTestResults',
    ]

    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    return df[keep_columns].sort_values(by=['state', 'date'])

def retrieve_nytimes(uri="https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"):
    df = pd.read_csv(uri)

    keep_columns = [
        'date',
        'state',
        'cases',
        'deaths'
    ]

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df['state'] = df['state'].apply(lambda x: us_state_abbrev[x])
    return df[keep_columns].sort_values(by=['state', 'date'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch COVID-19 historical data for US states/territories')
    parser.add_argument('outpath', nargs='?', metavar='O', type=argparse.FileType('w'), default=sys.stdout)

    args = parser.parse_args()
    outdir = args.outpath

    tracking = retrieve_tracking()
    nytimes = retrieve_nytimes()

    merged = pd.merge(tracking, nytimes, on=['date', 'state'])
    merged.rename({'cases': 'casesCumulative', 'deaths': 'deathsCumulative'}, axis='columns', inplace=True)

    merged.to_csv(outdir, index=False)
