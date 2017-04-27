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
STUDIES_BY_DISCIPLINE = "./data/list_of_studies_by_discipline.xlsx"
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
    new_col_name = 'found_in_' + part_in_bid
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


def associate_new_data(dataframe, df_studies_by_funder):
    """
    Takes a dataframe with the case study information and merges it with another
    dataframe that contains case study IDs and some other data (e.g. funders, disciplines)
    :params: a dataframe with case study information, a second dataframe with cases study IDs and other information
    :return: a dataframe containing case study information and other information
    """
    
    dataframe = pd.merge(left=dataframe,right=df_studies_by_funder, how='left', left_on='Case Study Id', right_on='Case Study Id')
        
    return dataframe


def col_locator(dataframe, search_term):

    located_cols = []
    term_length = len(search_term)
    for current in dataframe.columns:
        if current[:term_length] == search_term:
            located_cols.append(current)
    return located_cols



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


def convert_to_df(dict, index_name, value_name):

    dataframe = pd.DataFrame(list(dict.items()), columns=[index_name, value_name])
    dataframe.set_index([index_name], inplace=True)
    dataframe.sort_values([value_name], inplace=True)

    return dataframe


def add_percent(dataframe, colname):

    dataframe['percentage'] = round(100 * (dataframe[colname]/dataframe[colname].sum()),1)

    return dataframe


def add_relative_percentage(dataframe, col_for_calc, df_master_values, col_for_relative):

    dataframe['relative percentage'] = round(100 * (dataframe[col_for_calc]/df_master_values[col_for_relative]),1)    

    return dataframe


def plot_bar_from_df(dataframe, y_col, title):
    """
    :params: 
    :return: 
    """

    dataframe.plot(y = y_col, kind='bar', legend=None)
    plt.title(title)
#    if xaxis != None:
#        plt.xlabel(xaxis)
#    if yaxis != None:
#        plt.ylabel(yaxis)
    # This provides more space around the chart to make it prettier        
    plt.tight_layout(True)
#    plt.savefig(CHART_RESULT_STORE + filename + '.png', format = 'png', dpi = 150)
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
    # we want to search
    possible_search_places = ['Title', 'Summary of the impact', 'Underpinning research', 'References to the research', 'Details of the impact']

    # Import dataframe from original xls
    df = import_xls_to_df(DATAFILENAME, 'CaseStudies')

    # Clean data
    df = clean(df)

    #Need this list later: used to remove columns relating to original data
    original_cols = list(df.columns)

    # Import case study ids for each funder
    df_studies_by_funder = import_xls_to_df(STUDIES_BY_FUNDER, 'Sheet1')
    
    # Import case study ids for each funder
    df_studies_by_discipline = import_xls_to_df(STUDIES_BY_DISCIPLINE, 'Sheet1')
    
    # Associate case study IDs with specific funders
    df = associate_new_data(df, df_studies_by_funder)

    # Associate case study IDs with specific disciplines
    df = associate_new_data(df, df_studies_by_discipline)

    # Create a list of the available funders.
    # Easily done by taking the col names of df_studies_by_funder
    # and removing the Case Study Id item
    list_of_funders = list(df_studies_by_funder.columns)
    list_of_funders.remove('Case Study Id')

    # Go through the parts of the bid, and for each one look for the search word, record how
    # many case studies were found to match, then add a new column to identify this location
    # in the original dataframe
    for part_in_bid in possible_search_places:
        df_cut = cut_to_specific_word(df, WORD_TO_SEARCH_FOR, part_in_bid)
        df = merge_search_place(df, df_cut)

    # Create a list of the cols that hold location data in them
    found_in_cols = col_locator(df, 'found_in_')

    # For ease of calculation later, create a new column which is a summary of the
    # other location
    df.loc[df[found_in_cols].notnull().any(1), 'found_in_anywhere'] = 'anywhere'

    # In the step above, we've added another location column, so add
    # this to the list
    found_in_cols.append('found_in_anywhere')

    # Create a list of the cols that hold discipline data in them
    discipline_cols = col_locator(df, 'discipline_')

    # Create a list of the cols that hold funder data in them
    funder_cols = col_locator(df, 'funder_')


    ########## Now to start getting some data about funders ########## 

    # Remove all col names except those relating to those that identify where
    # the word was found (i.e. "Found in Title, Found in...")
    location_cols = get_col_names(df, original_cols, list_of_funders)

    # Make new dataframes corresponding to case studies that mention the word
    # anywhere or just those that mention it in the title, or those that mention
    # it just in the title or summary of impact
#    df_software_anywhere = df.dropna(subset=[location_cols], how='all')
#    df_software_title = df.dropna(subset=['Search word found in Title'], how='all')
#    df_software_summary = df.dropna(subset=['Search word found in Summary of the impact'], how='all')


'''''
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

    ########### What values do we want to print? ################

   #list = [dict name, name of measurement, values, title of chart]
    master_values = [funder_all_studies, 'Funder of case study', 'Number', 'Number of REF case studies registered by funder']
    calc1 = [how_many_found, 'Where word was found', 'Number', 'Where "' + WORD_TO_SEARCH_FOR + '" was found in case study']
    calc2 = [funder_software_anywhere, 'Funder', 'Number', 'Number of REF case studies mentioning"'
            + WORD_TO_SEARCH_FOR + '" anywhere in the case study']
    calc3 = [funder_software_title, 'Funder', 'Number', 'Number of REF case studies mentioning"'
            + WORD_TO_SEARCH_FOR + '" in the title']
    calc4 = [funder_software_summary, 'Funder', 'Number','Number of REF case studies mentioning"'
            + WORD_TO_SEARCH_FOR + '" in the summary']
    
    things_to_plot = [calc1, calc2, calc3, calc4]
    things_to_add_relative_percentage = [calc2, calc3, calc4]

    df_master_values = convert_to_df(master_values[0],master_values[1], master_values[2])
    df_master_values = add_percent(df_master_values, master_values[2])
    plot_bar_from_df(df_master_values, master_values[2], master_values[3])

    for count in range(0,len(things_to_plot)):
        df_current = convert_to_df(things_to_plot[count][0],things_to_plot[count][1], things_to_plot[count][2])
        df_current = add_percent(df_current, things_to_plot[count][2])
#        plot_bar_from_df(df_current, things_to_plot[count][2], things_to_plot[count][3])
        for count2 in range(0,len(things_to_add_relative_percentage)):
            if things_to_plot[count] == things_to_add_relative_percentage[count2]:
                df_current = add_relative_percentage(df_current, things_to_plot[count][2], df_master_values, master_values[2])
                plot_bar_from_df(df_current, 'relative percentage', 'Case studies relative to funder')
                print(df_current)'''

if __name__ == '__main__':
    main()
