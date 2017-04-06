#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
#import matplotlib.pyplot as plt
import math
#import logging


DATAFILENAME = "./data/CaseStudies.xlsx"
EXCEL_RESULT_STORE = "./outputs/output.xlsx"

def import_xls_to_df(filename, name_of_sheet):
    """
    Imports an Excel file into a Pandas dataframe
    :params: get an xls file and a sheetname from that file
    :return: a df
    """
    return pd.read_excel(filename,sheetname=name_of_sheet)


def clean(dataframe):

    # Someone thought it would be a good idea to add line breaks to the longer strings in Excel
    # This removes them 
    dataframe = dataframe.replace(to_replace='\n', value='', regex=True)

    # There are also multiple spaces in the strings. This removes them.
    dataframe = dataframe.replace('\s+', ' ', regex=True)
    
    # And now to remove the leading spaces
    # Need the try and except because some of the cols have integers
    for col in dataframe.columns:
        try:
            dataframe[col] = dataframe[col].map(lambda x: x.strip())
        except:
            pass
            
    return dataframe



def cut_to_software(dataframe, colname):
    """
    Cleans the dataframe based on advice we have been given by EPSRC:
    :params: a dataframe and a colname of the column in which the years are stored
    :return: a dataframe with only int years and NaNs
    """

    df_return = dataframe[dataframe[colname].str.contains('software')]
    
    return df_return


def main():
    """
    Main function to run program
    """
    
    # I write back to the original dataframe and pandas warns about that, so turning off the warning    
    pd.options.mode.chained_assignment = None 
    
    # Import dataframe from original xls
    df = import_xls_to_df(DATAFILENAME, 'CaseStudies')

    # Clean data
    df = clean(df)

    df_in_title = cut_to_software(df, 'Title')
    df_in_summary = cut_to_software(df, 'Summary of the impact')
    df_in_underpin = cut_to_software(df, 'Underpinning research')
    df_in_references = cut_to_software(df, 'References to the research')
    df_in_details = cut_to_software(df, 'Details of the impact')
#    df_in_sources = cut_to_software(df, 'Sources to corroborate the impact')

    print('In title:')
    print(len(df_in_title))

    print('In summary:')
    print(len(df_in_summary))

    print('In underpinning:')
    print(len(df_in_underpin))

    print('In references:')
    print(len(df_in_references))

    print('In details:')
    print(len(df_in_details))

#    print('In sources:')
#    print(len(df_in_sources))

#    print(df.columns)

    # Clean the dataframe
#    df = clean_data(df,'Year First Provided')


    # Write results to Excel spreadsheet for the shear hell of it
    writer = ExcelWriter(EXCEL_RESULT_STORE)
    df_in_title.to_excel(writer,'title')
    df_in_summary.to_excel(writer,'summary')
    df_in_underpin.to_excel(writer,'underpin')
    df_in_references.to_excel(writer,'references')
    df_in_details.to_excel(writer,'details')
    writer.save()


if __name__ == '__main__':
    main()
