#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
#import matplotlib.pyplot as plt
import math
#import logging


DATAFILENAME = "./data/CaseStudies.xlsx"
STUDIES_BY_FUNDER = "./data/list_of_studies_by_council.xlsx"
EXCEL_RESULT_STORE = "./outputs/"

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



def cut_to_specific_word(dataframe, specific_word):
    """
    Takes in a dataframe and a column, and then creates a new dataframe containing only
    the rows from the original dataframe that had the word "software" in that column
    :params: a dataframe and a specific_word to look for in that dataframe
    :return: nothing, but writes lists of case studies with the word in the 
    Title, Summary, etc. to Excel spreadsheets
    """

    # A list of the different parts of the case study (i.e. columns) in which
    # we want to look
    where_to_look = ['Title', 'Summary of the impact', 'Underpinning research', 'References to the research', 'Details of the impact']

    # Initialise dict in which to store number of instances of specific_word found
    how_many = {}

    print('How many case studies have the word "software" in the...')    

    # Go through list, look for the word software
    for current in where_to_look:
        current_df = dataframe[dataframe[current].str.contains(specific_word)]
        # Store number of instances in dict
        how_many[current] = len(current_df)
        print(current + ": " + str(how_many[current]))
        # Get ready to write to Excel
        writer = ExcelWriter(EXCEL_RESULT_STORE + str(current) + '.xlsx')
        # Write result to Excel
        current_df.to_excel(writer, 'Sheet1')
        # Close Excel writer
        writer.save()

    # Convert the list of how many instances to a dataframe,
    # reorder the columns for prettiness and then write
    # it to an Excel spreadsheet
    how_many_df = pd.DataFrame(how_many, index = [0])
    how_many_df = how_many_df[where_to_look]
    
    writer = ExcelWriter(EXCEL_RESULT_STORE + 'how_many_time_' + specific_word + '_was_found_in_case_studies.xlsx')
    how_many_df.to_excel(writer,'Sheet1', index=False)
    writer.save()

    return


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
    
    # Import dataframe from original xls
    df = import_xls_to_df(DATAFILENAME, 'CaseStudies')

    # Clean data
    df = clean(df)
    
    # Import case study ids for each funder
    df_studies_by_funder = import_xls_to_df(STUDIES_BY_FUNDER, 'Sheet1')

    # Find the word (identified by the second param in the following)
    # in different parts of the dataframe
    cut_to_specific_word(df, 'software')
    
    # Find 



if __name__ == '__main__':
    main()
