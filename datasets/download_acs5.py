#!/usr/bin/env python3

import requests
import os
import unicodedata
import os.path as path
import pandas as pd
from os.path import join, dirname
from tqdm import tqdm

VARIABLE_NAMES = {
    'median_income': 'S1901_C01_012E',
    'name': 'NAME',
    'white_population': 'DP05_0037PE',
    'total_population': 'B01003_001E',
    'male_population': 'DP05_0002PE',
    'median_age': 'B01002_001E',
    'persons_per_household': 'B25010_001E',
    'persons_in_poverty': 'DP03_0128PE',
    'high_school_graduate': 'DP02_0066PE',
    'bachelors': 'DP02_0067PE',
    'married_female': 'DP02_0032PE',
    'married_male': 'DP02_0026PE'
}

"""
Fix Puerto Rican accents
"""
def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text)\
        .encode('ascii', 'ignore')\
        .decode("utf-8")

    return str(text)

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
            VARIABLE_NAMES['white_population'],
            VARIABLE_NAMES['male_population'],
            VARIABLE_NAMES['persons_in_poverty'],
            VARIABLE_NAMES['high_school_graduate'],
            VARIABLE_NAMES['bachelors'],
            VARIABLE_NAMES['married_female'],
            VARIABLE_NAMES['married_male'],
        ),
        'for': 'county:*'
    })

    r3 = requests.get(detailed_url, params={
        # 'key': CENSUS_KEY,
        'get': ljoin(
            VARIABLE_NAMES['name'],
            VARIABLE_NAMES['total_population'],
            VARIABLE_NAMES['median_age'],
            VARIABLE_NAMES['persons_per_household']
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
        county              = county.replace(' Municipality', '')
        county              = county.replace(' Municipio', '')
        county              = strip_accents(county)

        median_income       = none_cast(raw_subject[i + 1][1], int)

        total_population    = none_cast(raw_detailed[i + 1][1], int)
        median_age          = none_cast(raw_detailed[i + 1][2], float)
        household_size      = none_cast(raw_detailed[i + 1][3], float)

        white_population    = none_cast(raw_profile[i + 1][1], float)
        male_population     = none_cast(raw_profile[i + 1][2], float)
        poverty_percent     = none_cast(raw_profile[i + 1][3], float)
        highschool          = none_cast(raw_profile[i + 1][4], float)
        bachelors           = none_cast(raw_profile[i + 1][5], float)
        married_female      = none_cast(raw_profile[i + 1][6], float)
        married_male        = none_cast(raw_profile[i + 1][7], float)

        raw_list[i] = [fips, state, county,
                       total_population, median_income, white_population, male_population,
                       median_age, household_size, poverty_percent, highschool, bachelors,
                       married_female, married_male]

    df = pd.DataFrame(raw_list, columns=['fips',
                                         'state',
                                         'county',
                                         'total population',
                                         'median income (household)',
                                         'white population (%)',
                                         'male population (%)',
                                         'median age',
                                         'persons per household',
                                         'persons in poverty (%)',
                                         'high school graduates (%)',
                                         'bachelor\'s degrees (%)',
                                         'married female population (%)',
                                         'married male population (%)'])

    df = df.sort_values(by=['state', 'county'])

    return df

if __name__ == "__main__":
    acs5 = retrieve_acs5()
    acs5.to_csv('acs5.csv', index=False)
