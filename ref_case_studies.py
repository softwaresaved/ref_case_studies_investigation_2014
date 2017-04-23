#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
import matplotlib.pyplot as plt
import math
#import logging

# The word we're going to look for - in lowercase please
WORD_TO_SEARCH_FOR = 'software'
DATAFILENAME = "./data/CaseStudies.xlsx"
STUDIES_BY_FUNDER = "./data/list_of_studies_by_council.xlsx"
EXCEL_RESULT_STORE = "./outputs/"
CHART_RESULT_STORE = "./outputs/charts/"

def import_xls_to_df(filename, name_of_sheet):
    """
    Imports an Excel file into a Pandas dataframe
    :params: get an xls file and a sheetname from that file
    :return: a df
    """
    return pd.read_excel(filename,sheetname=name_of_sheet)


def clean(dataframe):
    """
    Cleans the imported data for easy processing by removing end of lines chars, multiple spaces,
    and lowercasing everying
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
    the rows from the original dataframe that had the search word in that column
    :params: a dataframe, a specific_word to look for, and a column name relating to
             a part in a case study in which the specific_word should be searched for
    :return: a dataframe containing only the case studies which had specific word in 
             the column of interest
    """

    # Cut dataframe down to only those rows with a word in the right column
    current_df = dataframe[dataframe[part_in_bid].str.contains(specific_word)]
    # Add a new col to indicate where the specific word was found
    new_col_name = 'Search word found in ' + part_in_bid
    current_df[new_col_name] = part_in_bid
    # Drop all columns except the case study and the col showing where the word was found
    current_df = current_df[['Case Study Id', new_col_name]]

    return current_df


def merge_search_place(dataframe, df_cut):
    """
    Takes in a dataframe with all case studies information, and a second that contains the case
    study IDs that relate to a search word found in a specific part of the case study,
    the Title, for example. These are merged to produce a dataframe with all the case
    study information and where a specific word was found in the case study
    :params: two dataframes
    :return: a dataframe created by merging the two dataframes
    """

    dataframe = pd.merge(left=dataframe,right=df_cut, how='left', left_on='Case Study Id', right_on='Case Study Id')

    return dataframe


def write_lengths(how_many_found, possible_search_places):
    """
    Takes in a dict containing places in the bid that were searched for a word, and a number
    of times the word was found in that place. Reorders things based on a list of names that
    relate to col names. Writes the result to Excel.
    :params: a dict and a list
    :return: nothing (writes the result to Excel)
    """
    
    # Convert the dictionary of how many times the word was found
    # to a dataframe, reorder the columns for prettiness and then write
    # it to an Excel spreadsheet    
    how_many_df = pd.DataFrame(how_many_found, index = [0])
    how_many_df = how_many_df[possible_search_places]
    
    #Write the result to Excel
    writer = ExcelWriter(EXCEL_RESULT_STORE + 'how_many_times_word_was_found.xlsx')
    how_many_df.to_excel(writer,'Sheet1', index=False)
    writer.save()

    return


def associate_funders(dataframe, df_studies_by_funder):
    """
    Takes a dataframe with the case study information and merges it with another
    dataframe that contains case study IDs and who funded them
    :params: a dataframe with case study information, a second dataframe with cases study IDs and funder information
    :return: a dataframe containing case study information and funder information
    """
    
    dataframe = pd.merge(left=dataframe,right=df_studies_by_funder, how='left', left_on='Case Study Id', right_on='Case Study Id')
        
    return dataframe

def get_col_names(df, cols_to_remove_1, cols_to_remove_2):

    # Get all names in the dataframe
    all_col_names = list(df.columns)
    # Remove the first list of col names
    temp_list = [x for x in all_col_names if x not in cols_to_remove_1]
    # Remove the second list of col names
    remaining_cols = [x for x in temp_list if x not in cols_to_remove_2]
    
    return remaining_cols


def write_results_to_xls(dataframe, loc_and_title):
    """
    Takes a dataframe and writes it to an Excel spreadsheet based on a string
    which describes the save location and title
    :params: a dataframe, a string containing desired location and title of a Excel spreadsheet
    :return: nothing (writes an Excel spreadsheet)
    """
    
    writer = ExcelWriter(loc_and_title)
    # Write result to Excel
    dataframe.to_excel(writer, 'Sheet1', index=False)
    # Close Excel writer
    writer.save()

    return


def collapse_df(dataframe, colname):
    '''
    Takes a dataframe and a colname, then drops all rows in that colname
    that are NaN
    :params: a dataframe and column from that dataframe
    :return: a dataframe with all rows removed that have an NaN in the identified column
    '''

    dataframe = dataframe.dropna(subset=[colname], how='all')
    number_found = len(dataframe)

    return number_found


def convert_to_df(dict, add_percent, index_name, value_name):


    dataframe = pd.DataFrame(list(dict.items()), columns=[index_name, value_name])
    dataframe.set_index([index_name], inplace=True)
    dataframe.sort_values([value_name], inplace=True)

    if add_percent == True:
        dataframe['percentage']= round(100 * (dataframe[value_name]/dataframe[value_name].sum()),1)

    print(dataframe)

    return


def plot_bar_from_df(dataframe,filename,title,xaxis,yaxis):
    """
    :params: 
    :return: 
    """

    dataframe.plot(kind='bar', legend=None)
    plt.title(title)
    if xaxis != None:
        plt.xlabel(xaxis)
    if yaxis != None:
        plt.ylabel(yaxis)
    # This provides more space around the chart to make it prettier        
    plt.tight_layout(True)
    plt.savefig(CHART_RESULT_STORE + filename + '.png', format = 'png', dpi = 150)
    plt.show()
    return

def plot_bar_from_dict(dict):

    plt.bar(range(len(dict)), dict.values(), align='center')
    plt.xticks(range(len(dict)), list(dict.keys()))
    plt.show()

    return
    

def main():
    """
    Main function to run program
    
    To change the word searched for in the case studies,
    change the global variable found at the very start of
    the program called WORD_TO_SEARCH_FOR
    """
    
    # A list of the different parts of the case study (i.e. columns) in which
    # we want to look
    possible_search_places = ['Title', 'Summary of the impact', 'Underpinning research', 'References to the research', 'Details of the impact']

    # Import dataframe from original xls
    df = import_xls_to_df(DATAFILENAME, 'CaseStudies')

    # Clean data
    df = clean(df)

    #Need this list later: used to remove columns relating to original data
    original_cols = list(df.columns)

    # Import case study ids for each funder
    df_studies_by_funder = import_xls_to_df(STUDIES_BY_FUNDER, 'Sheet1')

    # Create a list of the available funders.
    # Easily done by taking the col names of df_studies_by_funder
    # and removing the Case Study Id item
    list_of_funders = list(df_studies_by_funder.columns)
    list_of_funders.remove('Case Study Id')

    # Go through the parts of the bid, and for each one look for the search word, record how
    # many case studies were found to match, then add a new column to identify this location
    # in the original dataframe
    how_many_found = {}
    for part_in_bid in possible_search_places:
        # Find the word (identified by the second param in the following)
        # in different parts of the dataframe
        df_cut = cut_to_specific_word(df, WORD_TO_SEARCH_FOR, part_in_bid)
        how_many_found[part_in_bid] = len(df_cut)
        df = merge_search_place(df, df_cut)
    
    ########## This next bit saves the number of times the term was found
    ########## in each part of the case study

    # Write the times the word was found to Excel for posterity
    write_lengths(how_many_found, possible_search_places)

    # Associate case study IDs with specific funders
    df = associate_funders(df, df_studies_by_funder)

    # Write super dataframe that now contains all information to an Excel spreadsheet
#    write_results_to_xls(df, EXCEL_RESULT_STORE + 'processed_case_studies.xlsx')

    ########## Now to start getting some data about funders ########## 

    # Remove all col names except those relating to those that identify where
    # the word was found (i.e. "Found in Title, Found in...")
    location_cols = get_col_names(df, original_cols, list_of_funders)

    # Make new dataframes corresponding to case studies that mention the word
    # anywhere or just those that mention it in the title, or those that mention
    # it just in the title or summary of impact
    df_software_anywhere = df.dropna(subset=[location_cols], how='all')
    df_software_title = df.dropna(subset=['Search word found in Title'], how='all')
    df_software_summary = df.dropna(subset=['Search word found in Summary of the impact'], how='all')

    # Go through all the funders to see how many case studies come from each one
    funder_all_studies = {}
    funder_software_anywhere = {}
    funder_software_title = {}
    funder_software_summary = {}
    for funder in list_of_funders:
        # Creat dict showing how many case studies - of any type - registered by each funder
        funder_all_studies[funder] = collapse_df(df, funder)
        # Creat dicts for each funder showing how many case studies included the search word
        # 1. anywhere, 2. just in title, 3. just in the title or summary
        funder_software_anywhere[funder] = collapse_df(df_software_anywhere, funder)
        funder_software_title[funder] = collapse_df(df_software_title, funder)
        funder_software_summary[funder] = collapse_df(df_software_summary, funder)

    ########### Time for some plotting ################
    
    df_how_many_found = convert_to_df(how_many_found, True, 'Where word was found', 'How many times "' + WORD_TO_SEARCH_FOR + '" was found in case studies')
    df_funder_all_studies = convert_to_df(funder_all_studies, True, 'Funder', 'Number of case studies')
    df_funder_software_anywhere = convert_to_df(funder_software_anywhere, True, 'Funder', 'Number with "' + WORD_TO_SEARCH_FOR + '" anywhere in case study')
    df_funder_software_title = convert_to_df(funder_software_title, True, 'Funder', 'Number with "' + WORD_TO_SEARCH_FOR + '" in title')
    df_funder_software_summary = convert_to_df(funder_software_summary, True, 'Funder', 'Number with "' + WORD_TO_SEARCH_FOR + '" in summary')

    
#    plot_bar_from_dict(where_term_was_found)


if __name__ == '__main__':
    main()
