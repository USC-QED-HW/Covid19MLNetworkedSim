#!/usr/bin/env python3

import requests
import os
import os.path as path
import pandas as pd
# from dotenv import load_dotenv
from os.path import join, dirname
from tqdm import tqdm

VARIABLE_NAMES = {
    'median_income': 'S1901_C01_012E',
    'name': 'NAME',
    'white_population': 'DP05_0064PE',
    'total_population': 'B01003_001E'
}

def ljoin(*args):
    return ','.join(list(args))

def none_cast(a, cast):
    if a is None:
        return cast()
    return cast(a)

def retrieve_acs5():
    # CENSUS_KEY = os.environ.get("CENSUS_KEY")

    subject_url     = "https://api.census.gov/data/2018/acs/acs5/subject"
    profile_url     = "https://api.census.gov/data/2018/acs/acs5/profile"
    detailed_url    = "https://api.census.gov/data/2018/acs/acs5/"

    r1 = requests.get(subject_url, params={
        # 'key': CENSUS_KEY,
        'get': ljoin(
            VARIABLE_NAMES['name'],
            VARIABLE_NAMES['median_income']),
        'for': 'county:*'
    })

    r2 = requests.get(profile_url, params={
        # 'key': CENSUS_KEY,
        'get': ljoin(
            VARIABLE_NAMES['name'],
            VARIABLE_NAMES['white_population']
        ),
        'for': 'county:*'
    })

    r3 = requests.get(detailed_url, params={
        # 'key': CENSUS_KEY,
        'get': ljoin(
            VARIABLE_NAMES['name'],
            VARIABLE_NAMES['total_population']
        ),
        'for': 'county:*'
    })

    raw_subject = r1.json()
    raw_profile = r2.json()
    raw_detailed = r3.json()

    entries = len(raw_subject) - 1
    raw_list = [None]*entries

    for i in tqdm(range(entries)):
        fips                = raw_subject[i + 1][2] + raw_subject[i + 1][3]
        county, state       = raw_subject[i + 1][0].split(', ')
        county              = county.replace(' County', '')
        median_income       = none_cast(raw_subject[i + 1][1], int)
        white_population    = none_cast(raw_profile[i + 1][1], float)
        total_population    = int(raw_detailed[i + 1][1])

        raw_list[i] = [fips, state, county, total_population, median_income, white_population]

    df = pd.DataFrame(raw_list, columns=['fips', 'state', 'county', 'total_population',
        'median_income (household)', 'white_population (proportion)'])
    
    df = df.sort_values(by=['state', 'county'])

    return df

# def load_environment():
#     dotenv_path = join(dirname(dirname(path.abspath(__file__))), '.env')
#     load_dotenv(dotenv_path)

if __name__ == "__main__":
    # load_environment()
    acs5 = retrieve_acs5()
    acs5.to_csv('acs5.csv', index=False)
