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



def cut_to_software(dataframe, colname):
    """
    Takes in a dataframe and a column, and then creates a new dataframe containing only
    the rows from the original dataframe that had the word "software" in that column
    :params: a dataframe and a colname of the column in which the word software is to be found
    :return: a dataframe with rows 
    """

    df_return = dataframe[dataframe[colname].str.contains('software')]
    
    return df_return


def plot_bar_charts(dataframe,filename,title,xaxis,yaxis):
    """
    Takes a two-column dataframe and plots it
    :params: a dataframe with two columns (one labels, the other a count), a filename for the resulting chart, a title, and titles for the
    two axes (if title is None, then nothing is plotted))
    :return: Nothing, just prints a chart
    """

    # For each one, interested in the count, the count for each research council, 


    dataframe.plot(kind='bar', legend=None)
    plt.title(title)
    if xaxis != None:
        plt.xlabel(xaxis)
    if yaxis != None:
        plt.ylabel(yaxis)
    # This provides more space around the chart to make it prettier        
    plt.tight_layout(True)
    plt.savefig(CHART_STORE_DIR + filename + '.png', format = 'png', dpi = 150)
    plt.show()
    return


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

    # Create dataframes pertaining to the workd "software" used in different bits of the case study
    # then find how many case studies each one relates to (hence the len() bit)
    df_in_title = cut_to_software(df, 'Title')
    num_software_in_title = len(df_in_title)
    
    df_in_summary = cut_to_software(df, 'Summary of the impact')
    num_software_in_summary = len(df_in_summary)
    
    df_in_underpin = cut_to_software(df, 'Underpinning research')
    num_software_in_underpin = len(df_in_underpin)
    
    df_in_references = cut_to_software(df, 'References to the research')
    num_software_in_references = len(df_in_references)
    
    df_in_details = cut_to_software(df, 'Details of the impact')
    num_software_in_details = len(df_in_details)




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
