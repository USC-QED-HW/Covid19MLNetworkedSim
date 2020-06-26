#!/usr/bin/env python3

import requests
import time
from tqdm import tqdm
import os.path as path
import pandas as pd

def retrieve_nyt_dataset():
    r = requests.get('https://disease.sh/v2/nyt/counties')
    raw = r.json()

    l = len(raw)

    row_list = [None]*l

    for i in tqdm(range(l)):
        entry = raw[i]
        if "Unknown" not in entry['county']:
            row_list[i] = [entry['fips'], pd.to_datetime(entry['date']),
                                            entry['state'], entry['county'],
                                            entry['cases'], entry['deaths']]
    
    row_list = [x for x in row_list if x is not None]

    df = pd.DataFrame(row_list, columns=['fips', 'date', 'state', 'county', 'cases', 'deaths'])
    df = df.sort_values(by=['state', 'county', 'date'])
    return df

if __name__ == "__main__":
    nyt_dataset = retrieve_nyt_dataset()
    nyt_dataset.to_csv('nyt.csv', index=False)
