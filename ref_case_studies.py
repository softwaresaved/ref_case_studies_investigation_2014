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
EXCEL_RESULT_CHART_STORE = "./outputs/chart_data/"
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


def summarise_dfs(dict_of_dfs, col_list, remove_string):
    """
    Takes a dictionary of dataframes, each of which corresponds to a search term stored in the col_list.
    Each dataframe has been collapsed so the only rows that exist are ones that include the search term
    in the appropriate column. This means that the length of the dataframe corresponds to the number
    of times that search term was found in the super dataframe which was its parent
    see - cut_to_specific_word
    Combines the search terms and lengths into a dict which is transformed into a dataframe to make
    later processing easier. Adds a percentage columns and then sorts the dataframe into ascending order
    :params: a dict of dfs and a list of columns, a string used to form a name for the resulting dataframe
    :return: a sorted dataframe
    """
    # Need this for later string manipulation
    length = len(remove_string)
    
    dictionary ={}
    for current in col_list:
        name = current[length:]
        df_name = remove_string[:length-1]
        df_value_name = 'How many'
        # Length of df corresponds to number of times the search word was found
        dictionary[name] = len(dict_of_dfs[current])
            
    dataframe = pd.DataFrame(list(dictionary.items()), columns=[df_name, df_value_name])
    # Use the names as the index column rather than the numeric one that's created in
    # the step above
    dataframe.set_index([df_name], inplace=True)
    dataframe['percentage'] = round(100 * (dataframe[df_value_name]/dataframe[df_value_name].sum()),1)
    dataframe.sort_values([df_value_name], inplace=True)
    
    print(dataframe)

    return dataframe


def write_results_to_xls(dataframe, title):
    """
    Takes a dataframe and writes it to an Excel spreadsheet based on a string
    which describes the save location and title
    :params: a dataframe, a string containing desired location and title of a Excel spreadsheet
    :return: nothing (writes an Excel spreadsheet)
    """
    
    filename = title.replace(" ", "_")

    writer = ExcelWriter(EXCEL_RESULT_CHART_STORE + filename + '.xlsx')
    # Write result to Excel
    dataframe.to_excel(writer, 'Sheet1')
    # Close Excel writer
    writer.save()

    return

def relative_percentages(dataframe, df_summary, subject):
    '''
    Takes a dataframe and a dataframe with summary data, then creates relative percentages
    in the first dataframe. In other words, what percentage of case studies from a specific
    funder included the search term?
    :params: a dataframe, a dataframe with summary data, a subject that is used to name
             one of the relative percentages
    :return: a dataframe with relative percentages
    '''

    sum_value = df_summary['How many'].sum()
    dataframe['percentage relative to all case studies'] = round(100 * (dataframe['How many']/sum_value),1)
    dataframe['percentage relative to case studies from each ' + subject] = round(100 * (dataframe['How many']/df_summary['How many']),1)

    return dataframe


def plot_bar_from_df(dataframe, y_col, title):
    """
    :params: 
    :return: 
    """

    dataframe.plot(y = y_col, kind='bar', legend=None)
    plt.title(title)
    # This provides more space around the chart to make it prettier        
    plt.tight_layout(True)
    filename = title.replace(" ", "_")
    print(filename)
    plt.savefig(CHART_RESULT_STORE + filename + '.png', format = 'png', dpi = 150)
#    plt.show()
    
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

    # This is the super dataframe with all information in it. Might be handy
    # to other people in this form, so let's save it
    # Write out to Excel
#    write_results_to_xls(df, 'all_ref_case_study_data')

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

    # Create some names that will be used to represent strings that are used
    # to identify columns in the analysis
    found_in = 'found_in_'
    discipline = 'discipline_'
    funder = 'funder_'

    # Create a list of the cols that hold location data in them
    found_in_cols = col_locator(df, found_in)

    # For ease of calculation later, create a new column which is a summary of the
    # other location
    df.loc[df[found_in_cols].notnull().any(1), 'found_in_anywhere'] = 'anywhere'

    # In the step above, we've added another location column, so add
    # this to the list
    found_in_cols.append('found_in_anywhere')

    # Create a new dataframe that only contains case studies that include
    # the search term in them somewhere
    df_software = df.dropna(subset=['found_in_anywhere'], how='all')
    
    # Write out to Excel
#    write_results_to_xls(df_software, WORD_TO_SEARCH_FOR + '_case_studies_only')

    # Create a list of the cols that hold discipline data in them
    discipline_cols = col_locator(df, discipline)

    # Create a list of the cols that hold funder data in them
    funder_cols = col_locator(df, funder)

    # Create a dict of dataframes, each of which holds the data
    # related to a specific found_in, funder or discipline
    # Start by adding the three locator lists together
    all_locator_cols = found_in_cols + discipline_cols + funder_cols
    dict_of_dfs = {}
    
    # Drop all columns that aren't related to the found_in, funder
    # or discipline in which we're interested, and store them in
    # a dict of dataframes for later processing
    for name in all_locator_cols:
        dict_of_dfs[name] = df.dropna(subset=[name], how='all')

    # Create summaries of the data based on where the term was found,
    # in which discipline it was basde, and by who funded it
    df_summary_found_in = summarise_dfs(dict_of_dfs, found_in_cols, found_in)
    df_summary_funder = summarise_dfs(dict_of_dfs, funder_cols, funder)
    df_summary_discipline = summarise_dfs(dict_of_dfs, discipline_cols, discipline)

    # Now do the same, but based on the df that contains only
    # case studies related to software
    dict_of_software_dfs = {}
    for name in discipline_cols + funder_cols:
        dict_of_software_dfs[name] = df_software.dropna(subset=[name], how='all')

    # Create summaries of the df that contains only case studies
    # related to software
    df_summary_software_by_funder = summarise_dfs(dict_of_software_dfs, funder_cols, funder)
    df_summary_software_by_discipline = summarise_dfs(dict_of_software_dfs, discipline_cols, discipline)

    df_summary_software_by_funder = relative_percentages(df_summary_software_by_funder, df_summary_funder, 'funder')
    df_summary_software_by_discipline = relative_percentages(df_summary_software_by_discipline, df_summary_discipline, 'discipline')


    ############ Plotting #############

   #list = [df name, values column, title of chart]
    plot1 = [df_summary_funder, 'All REF case studies by funder']
    plot2 = [df_summary_discipline, 'All REF case studies by discipline']
    plot3 = [df_summary_found_in, 'REF case studies including the word ' + WORD_TO_SEARCH_FOR]
    plot4 = [df_summary_software_by_funder, 'REF case studies including the word ' + WORD_TO_SEARCH_FOR + ' by funder']
    plot5 = [df_summary_software_by_discipline, 'REF case studies including the word ' + WORD_TO_SEARCH_FOR + ' by discipline']

    vanilla_plots = [plot1, plot2, plot3, plot4, plot5]
    
    for count in range(0,len(vanilla_plots)):
        plot_bar_from_df(vanilla_plots[count][0], 'How many', vanilla_plots[count][1])
        plot_bar_from_df(vanilla_plots[count][0], 'percentage', vanilla_plots[count][1] + ' by percentage')
        write_results_to_xls(vanilla_plots[count][0], vanilla_plots[count][1])


if __name__ == '__main__':
    main()
