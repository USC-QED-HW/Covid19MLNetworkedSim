#!/usr/bin/env python3

import pandas as pd
from tqdm import tqdm

def main():
    # Read in life expectancy table
    le = pd.read_excel('ihme.xlsx', 'Life Expectancy')

    # Remove the last two columns
    le.drop(le.columns[[14, 15]], inplace=True, axis=1)

    # Remove all the columns except the first two and last two
    le.drop(le.iloc[:, 2:-2], inplace=True, axis=1)

    # Remove all rows with NA
    le = le.dropna()

    # Rename the column names
    le.columns = ['state', 'county', 'male life expectancy', 'female life expectancy']

    # Write life expectancy into csv
    le.to_csv('ihme_le.csv', index=False)

    # Read in obesity table
    ob = pd.read_excel('ihme.xlsx', 'Obesity')

    # Remove the last two columns
    ob.drop(ob.iloc[:, -4:], inplace=True, axis=1)

    # Remove the third to sixth columns
    ob.drop(ob.iloc[:, 2:6], inplace=True, axis=1)

    # Remove all rows with NA
    ob = ob.dropna()

    # Rename the columns
    ob.columns = ['state', 'county', 'male obesity prevalence (%)', 'female obesity prevalence (%)']

    # Write obesity data into csv
    ob.to_csv('ihme_ob.csv', index=False)


if __name__ == "__main__":
    main()
