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
        
    dataframe.sort_values(by='Case Study Id', ascending=0, inplace = True)

    return dataframe

def clean(dataframe):
    """
    Cleans the imported data for easy processing
    :params: a dataframe
    :return: a dataframe with clean data
    """

    # Someone thought it would be a good idea to add line breaks to the longer strings in Excel
    # This removes them 
    dataframe = dataframe.replace(to_replace='\n', value='', regex=True)

    # There are also multiple spaces in the strings. This removes them.
    dataframe = dataframe.replace('\s+', ' ', regex=True)
    
    # And now to remove the leading spaces and lowercase everything
    # Need the try and except because some of the cols have integers
    for col in dataframe.columns:
        try:
            dataframe[col] = dataframe[col].map(lambda x: x.strip())
            dataframe[col] = dataframe[col].str.lower()
        except:
            pass
            
    return dataframe



def main():
    """
    Main function to run program
    """
    
    # Import dataframe from original xls
    df = read_data()

    # Clean data
#    df = clean(df)

    # Write results to Excel spreadsheet for the shear hell of it
    writer = ExcelWriter(OUTPUT)
    df.to_excel(writer,'Sheet1')
#    df_in_summary.to_excel(writer,'summary')
#    df_in_underpin.to_excel(writer,'underpin')
#    df_in_references.to_excel(writer,'references')
#    df_in_details.to_excel(writer,'details')
    writer.save()


if __name__ == '__main__':
    main()
