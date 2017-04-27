#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
import os.path
#import matplotlib.pyplot as plt
import math


DATA_FILE_DIR = "./data/studies_by_council/"
OUTPUT = "./data/list_of_studies_by_council.xlsx"


def read_data():
    '''
    Goes through all the xlsx files in the appropriate dir, converts each
    one to a df and concatenates successively into a super df with all
    the data
    :params: none
    :return: a dataframe formed from multiple dataframes
    '''
    new = True
    for file in os.listdir(DATA_FILE_DIR):
        if file.endswith('.xlsx'):
            # Create the col name by dropping the file extension from the filename,
            # and then adding the keyword "funder_"
            new_col = 'funder_' + str(file)[:-5]

            #Need this if loop because the first iternation has to be a straight read rather than a concatenation
            if new == True:
                dataframe = pd.read_excel(DATA_FILE_DIR + str(file), sheetname='CaseStudies')
                dataframe = pd.DataFrame(dataframe['Case Study Id'])
                dataframe[new_col] = new_col
                new = False
            else:
                temp_df = pd.read_excel(DATA_FILE_DIR + str(file), sheetname='CaseStudies')
                # Knock out everything except the case study
                temp_df = pd.DataFrame(temp_df['Case Study Id'])
                temp_df[new_col] = new_col
                # Use concat to add temp dataframe onto end of the main dataframe 
                dataframe = pd.concat([dataframe, temp_df])

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
