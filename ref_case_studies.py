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


def cut_to_specific_word(dataframe, specific_word, part_in_bid):
    """
    Takes in a dataframe and a column, and then creates a new dataframe containing only
    the rows from the original dataframe that had the word "software" in that column
    :params: a dataframe and a specific_word to look for in that dataframe
    :return: nothing, but writes lists of case studies with the word in the 
    Title, Summary, etc. to Excel spreadsheets
    """

    # Cut dataframe down to only those rows with a word in the right column
    current_df = dataframe[dataframe[part_in_bid].str.contains(specific_word)]
    # Add a new col to indicate where the specific word was found
    new_col_name = 'Found in ' + part_in_bid
    current_df[new_col_name] = part_in_bid
    # Drop all columns except the case study and the col showing where the word was found
    current_df = current_df[['Case Study Id', new_col_name]]

    return current_df


def merge_search_place(dataframe, df_cut):

    dataframe = pd.merge(left=dataframe,right=df_cut, how='left', left_on='Case Study Id', right_on='Case Study Id')

    return dataframe



#        # Store number of instances in dict
#        how_many[current] = len(current_df)
#        print(current + ": " + str(how_many[current]))
        # Get ready to write to Excel


#    writer = ExcelWriter(EXCEL_RESULT_STORE + str(current) + '.xlsx')
    # Write result to Excel
#    current_df.to_excel(writer, 'Sheet1')
    # Close Excel writer
#    writer.save()


#    # Go through list, look for the word software
#    for current in where_to_look:
#        current_df = dataframe[dataframe[current].str.contains(specific_word)]
#        # Store number of instances in dict
#        how_many[current] = len(current_df)
#        print(current + ": " + str(how_many[current]))
#        # Get ready to write to Excel
#        writer = ExcelWriter(EXCEL_RESULT_STORE + str(current) + '.xlsx')
#        # Write result to Excel
#        current_df.to_excel(writer, 'Sheet1')
#        # Close Excel writer
#        writer.save()


def write_lengths(how_many_found, possible_search_places):

    # Convert the dictionary of how many times the word was found
    # to a dataframe, reorder the columns for prettiness and then write
    # it to an Excel spreadsheet    
    how_many_df = pd.DataFrame(how_many_found, index = [0])
    how_many_df = how_many_df[possible_search_places]
    
    writer = ExcelWriter(EXCEL_RESULT_STORE + 'how_many_times_word_was_found.xlsx')
    how_many_df.to_excel(writer,'Sheet1', index=False)
    writer.save()

    return


def associate_funder(df_studies_by_funder, where_to_look):
    
#    for current in where_to_look:
#        df_current = import_xls_to_df(EXCEL_RESULT_STORE + str(current) + '.xlsx', 'Sheet1')
#        print(df_current)
    
    df_current = import_xls_to_df(EXCEL_RESULT_STORE + 'Title.xlsx', 'Sheet1')
    
    df = pd.merge(left=df_current,right=df_studies_by_funder, how='left', left_on='Case Study Id', right_on='Case Study Id')
    
    writer = ExcelWriter(EXCEL_RESULT_STORE + 'Title.xlsx')
    # Write result to Excel
    df.to_excel(writer, 'Sheet1')
    # Close Excel writer
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

    # The word we're going to look for - in lowercase please
    WORD_TO_SEARCH_FOR = 'software'

    # Import dataframe from original xls
    df = import_xls_to_df(DATAFILENAME, 'CaseStudies')

    # Clean data
    df = clean(df)

    # Import case study ids for each funder
    df_studies_by_funder = import_xls_to_df(STUDIES_BY_FUNDER, 'Sheet1')

    # A list of the different parts of the case study (i.e. columns) in which
    # we want to look
    possible_search_places = ['Title', 'Summary of the impact', 'Underpinning research', 'References to the research', 'Details of the impact']

    # Initialise dict in which to store number of instances of specific_word found
    how_many_found = {}

    # Go through the parts of the bid, and for each one look for the search word, record how
    # case studies were found to match, then add a new column to identify this location
    # in the original dataframe
    for part_in_bid in possible_search_places:
        # Find the word (identified by the second param in the following)
        # in different parts of the dataframe
        df_cut = cut_to_specific_word(df, WORD_TO_SEARCH_FOR, part_in_bid)
        how_many_found[part_in_bid] = len(df_cut)
        df = merge_search_place(df, df_cut)
    
    # Write the times the word was found to Excel for posterity
    write_lengths(how_many_found, possible_search_places)
        
    print(df)

    # Add information about which case studies correspond to which funder
#    associate_funder(df_studies_by_funder, where_to_look)


if __name__ == '__main__':
    main()
