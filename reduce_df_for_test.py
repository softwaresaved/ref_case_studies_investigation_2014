#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np

# Other global variables
DATAFILENAME = "./data/all_ref_case_study_data.csv"
RESULT_STORE = "./data/"
FRACTION_TO_REDUCE = 0.9

def import_csv_to_df(filename):
    """
    Imports a csv file into a Pandas dataframe
    :params: a csv file
    :return: a df
    """
    
    return pd.read_csv(filename)


def export_to_csv(df, location, filename):
    """
    Exports a df to a csv file
    :params: a df and a location in which to save it
    :return: nothing, saves a csv
    """

    return df.to_csv(location + filename + '.csv')


def main():
    
    # Read in the data
    df = import_csv_to_df(DATAFILENAME)
    
    # Knock out a fraction (denoted by 'frac') of the rows of the dataframe
    df2 = df.drop(df.sample(frac=FRACTION_TO_REDUCE, axis=0).index)

    # Save the data
    export_to_csv(df2, RESULT_STORE, 'test_data_only')
    
if __name__ == '__main__':
    main()