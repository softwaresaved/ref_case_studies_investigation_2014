#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
#import matplotlib.pyplot as plt
import math


DATA_FILE_DIR = "./data/studies_by_council/"
OUTPUT = "./data/list_of_studies_by_council.xlsx"


def read_data():
    """
    Read in spreadsheets of case studies for each council. Knock out all information
    except the case study ID. Combine this information into a dataframe of case
    study ID and associated funder
    :params: none
    :return: a dataframe with case study IDs and associated funder
    """

    # Create a list of the funders available in the data, which corresponds
    # to the names of the spreadsheets that hold the data from each funder
    funder_list = ['ahrc', 'bbsrc', 'british_academy', 'cclrc', 'epsrc', 'esrc',
                   'mrc', 'nerc', 'pparc', 'rcuk', 'royal_academy_engineering', 
                   'royal_society', 'stfc', 'uk_space_agency', 'wellcome']

    # Initiate a dataframe in which to store the results
    dataframe = pd.DataFrame(np.nan, index=[0], columns=['Case Study Id'])

    # Cycle through the funder spreadsheets and create a main dataframe containing
    # all case studies and the associated funder(s)
    for current in funder_list:
        df = pd.read_excel(DATA_FILE_DIR + current + '.xlsx', sheetname='CaseStudies')
        # Knock out everything except the case study
        df = pd.DataFrame(df['Case Study Id'])
        # Add a column which is the name of the funder
        df[current] = current
        # Use concat to add current dataframe onto end of the main dataframe 
        dataframe = pd.concat([dataframe, df])

    return dataframe


def clean(dataframe):
    """
    Collapses the rows to produce a clean dataframe. There will be one only instance
    of each Case Id and in that row there will be at least one funder identified
    :params: a dataframe with - potentially - multiple instances of a Case Id each
    corresponding to a funder
    :return: a dataframe with only one instance of each Case Id
    """

    # Fill na's as blanks, because the .agg part of the function won't accept
    # other ways of expressing na
    dataframe = dataframe.fillna('')
    # Collapse the rows
    dataframe = dataframe.groupby('Case Study Id').agg(''.join)
            
    return dataframe


def main():
    """
    Main function to run program
    """
    
    # Import dataframe from original xls
    df = read_data()

    # Clean data
    df = clean(df)

    # Write results to Excel spreadsheet for the shear hell of it
    writer = ExcelWriter(OUTPUT)
    df.to_excel(writer,'Sheet1')
    writer.save()


if __name__ == '__main__':
    main()
