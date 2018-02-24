#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
import matplotlib.pyplot as plt
import math
import re
# This gets the pre-formatted short chart labels from a lookup file
from chart_label_lookup import short_plot_labels_discipline
from chart_label_lookup import short_plot_labels_funder


# The word we're going to look for - in lowercase please
SEARCH_TERM_LIST = ['software', 'computational', 'computation', 'hpc', 'simulation', 'visualisation', 'visualization', 'python', 'matlab', 'excel', 'github']

# Other global variables
DATAFILENAME = "./data/all_ref_case_study_data.xlsx"
# This is test data set made by randomly deleting 90% of the rows of the real data set
# It makes life faster when prototyping
# DATAFILENAME = "./data/test_data_only.xlsx"
STUDIES_BY_FUNDER = "./data/list_of_studies_by_council.xlsx"
UNITS_OF_ASSESSMENT = "./data/units_of_assessment.xlsx"
EXCEL_RESULT_STORE = "./outputs/"
CHART_RESULT_STORE = "./outputs/charts/"


def import_xls_to_df(filename, name_of_sheet):
    """
    Imports an Excel file into a Pandas dataframe
    :params: get an xls file and a sheetname from that file
    :return: a df
    """
    return pd.read_excel(filename,sheetname=name_of_sheet)


def write_results_to_xls(dataframe, title):
    """
    Takes a dataframe and writes it to an Excel spreadsheet based on a string
    which describes the save location and title
    :params: a dataframe, a string containing desired location and title of a Excel spreadsheet
    :return: nothing (writes an Excel spreadsheet)
    """
    
    filename = title.replace(" ", "_")

    writer = ExcelWriter(EXCEL_RESULT_STORE + filename + '.xlsx')
    # Write result to Excel
    dataframe.to_excel(writer, 'Sheet1')
    # Close Excel writer
    writer.save()

    return


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
    current_df = dataframe[dataframe[part_in_bid].str.contains(r'\b' + specific_word + r'\b', regex=True, na=False)]
    # Add a new col to indicate where the specific word was found
    new_col_name = specific_word +'_found_in_' + part_in_bid
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


def associate_new_data(dataframe, df_studies_by_funder):
    """
    Takes a dataframe with the case study information and merges it with another
    dataframe that contains case study IDs and some other data (e.g. funders, disciplines)
    :params: a dataframe with case study information, a second dataframe with cases study IDs and other information
    :return: a dataframe containing case study information and other information
    """
    
    dataframe = pd.merge(left=dataframe,right=df_studies_by_funder, how='left', left_on='Case Study Id', right_on='Case Study Id')
        
    return dataframe


def get_col_list(df, search_string):
    """
    Find all cols with a specific string in them
    :return: a list of cols
    """
    list_cols = []

    for current in df.columns:
        if search_string in current:
            list_cols.append(current)

    return list_cols


def summarise_search_terms(df, search_places, cols_list, all_case_study_count):
    """
    Summarise the results across all words searched for
    

    :returns: a dataframe with the summary results
    """

    summary_data = {}

    # Go through the parts in the study and for each one create a list of
    # associated columns, then drop any rows where all the columns are NaN
    # then take the length of the resulting df (which represents how many
    # times the any of the words were found in that part of the study)
    for curr_place in search_places:
        matching = [s for s in cols_list if curr_place in s]
        temp_df = df.dropna(subset=[matching], how='all', axis=0)
        summary_data[curr_place] = len(temp_df)
    
    summary_df = pd.DataFrame(list(summary_data.items()), columns=['word location', 'count'])    
    summary_df.set_index('word location', inplace=True)
    summary_df['percentage of all studies'] = round(100 * (summary_df['count']/all_case_study_count),0)
    summary_df.sort_values(['count'], ascending=False, inplace=True)

    return summary_df


def summarise_funders(df, cols_to_search, all_case_study_count):
        
    # Create temp df containing only the cols to be searched and use count() to create a summary series
    temp_df = df[cols_to_search]
    s = temp_df.count()
    
    # Convert summary series into df
    df_summary = pd.DataFrame({'index':s.index, 'count':s.values})
    df_summary.set_index('index', inplace=True)
    df_summary.sort_values(['count'], ascending=False, inplace=True)

    # Add a percentage col
    df_summary['percentage of all studies'] = round((df_summary['count']/all_case_study_count)*100,0)

    return df_summary


def summarise_uoas(df, df_term_found, list_of_uoas, all_case_study_count):
    """
    Create a summary df of the number of Units of Assessment found in the data
    """
    
    uoa_term_found_dict = {}
    uoa_all_dict = {}

    for current_uoa in list_of_uoas:
        # Cut to only one uoa in the df limited to rows with the search terms found
        temp_df = df_term_found[df_term_found['Unit of Assessment'].str.contains(current_uoa)]
        # Cut to only one uoa in the df with all case studies
        temp_2_df = df[df['Unit of Assessment'].str.contains(current_uoa)]
        uoa_term_found_dict[current_uoa] = len(temp_df)
        uoa_all_dict[current_uoa] = len(temp_2_df)

    summary_df = pd.DataFrame(list(uoa_term_found_dict.items()), columns=['unit of assessment', 'software reliant count'])    
    summary_df['all studies count'] = summary_df['unit of assessment'].map(uoa_all_dict)
    summary_df.set_index('unit of assessment', inplace=True)

    summary_df['percentage of studies in this uoa'] = round(100 * (summary_df['software reliant count']/summary_df['all studies count']),0)
    summary_df['percentage of all studies'] = round(100 * (summary_df['software reliant count']/all_case_study_count),0)
    summary_df.sort_values(['software reliant count'], ascending=False, inplace=True)

    return summary_df


def main():
    """
    Main function to run program
    
    To change the word searched for in the case studies,
    change the global variable found at the very start of
    the program called WORD_TO_SEARCH_FOR
    """
    
    # A list of the different parts of the case study (i.e. columns) in which
    # we want to search. I've removed 'References to the research' from the list
    # because it's too uncoupled from the actual case study content
    possible_search_places = ['Title', 'Summary of the impact', 'Underpinning research', 'Details of the impact']

    # Import dataframe from original xls
    df = import_xls_to_df(DATAFILENAME, 'Sheet1')
    
    # Import dataframe from original xls
    df_studies_by_funder = import_xls_to_df(STUDIES_BY_FUNDER, 'Sheet1')

    # Import units of assessment from original xls
    df_uoas = import_xls_to_df(UNITS_OF_ASSESSMENT, 'Sheet1')

    #Need this list later: used to remove columns relating to original data
    original_cols = list(df.columns)

    # Record length of original df and hence, number of all case studies
    all_case_study_count = len(df)

    # Create a list of the available funders.
    # Easily done by taking the col names of df_studies_by_funder
    # and removing the Case Study Id items
    list_of_funders = list(df_studies_by_funder.columns)
    list_of_funders.remove('Case Study Id')

    # Create a list of the units of assessment
    list_of_uoas = list(df_uoas['Unit of assessment'].str.lower())
    list_of_uoas.sort()

    # Go through the parts of the bid, and for each one look for the search word, record how
    # many case studies were found to match, then add a new column to identify this location
    # in the original dataframe
    for word_to_search_for in SEARCH_TERM_LIST:
        for part_in_bid in possible_search_places:
            df_cut = cut_to_specific_word(df, word_to_search_for.lower(), part_in_bid)
            df = merge_search_place(df, df_cut)

    # Get a list of all columns with data related to funders
    funder_cols = get_col_list(df, 'funder')

    # Get a list of all columns with data related to where a term was found
    found_in_cols = get_col_list(df, 'found_in')

    # For ease of calculation later, create a new column which is a summary of the
    # other found in locations (i.e. found in anywhere)
    df.loc[df[found_in_cols].notnull().any(1), 'found_in_anywhere'] = 'anywhere'

    # Count the number of terms found in each record
    df['search terms found'] = df[found_in_cols].apply(lambda x: x.count(), axis=1)

    temp = df['search terms found'].unique().tolist()
    temp.sort()

    print(temp)
    # 
    print(len(df[df['search terms found']>=1]))
    print(len(df[df['search terms found']>=2]))


    # Add anywhere to the search places, because it's an addition that's not in
    # the original list
    found_in_cols.append('found_in_anywhere')
    possible_search_places.append('anywhere')

    # Limit to only rows where search term(s) was found
    df_term_identified = df.dropna(axis=0, subset=found_in_cols, how='all')

    # Summarise the data across search terms or where they were found
    df_summary_terms = summarise_search_terms(df_term_identified, possible_search_places, found_in_cols, all_case_study_count)
    
    # Get a summary of the data across funders
    df_summary_funders = summarise_funders(df_term_identified, funder_cols, all_case_study_count)

    # Get a summary of the data across UOAs
    # NOTE: this uses the full dataframe not the df_term_identified one
    df_summary_uoas = summarise_uoas(df, df_term_identified, list_of_uoas, all_case_study_count)

    # Write out to Excel
    write_results_to_xls(df_term_identified, 'only_case_studies_with_search_term_identified')    
    write_results_to_xls(df_summary_terms, 'summary_of_terms_found')
    write_results_to_xls(df_summary_funders, 'summary_of_funders')
    write_results_to_xls(df_summary_uoas, 'summary_of_uoas')




'''

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

    return dataframe


def relative_percentages(dataframe, df_summary, subject):

    Takes a dataframe and a dataframe with summary data, then creates relative percentages
    in the first dataframe. In other words, what percentage of case studies from a specific
    funder included the search term?
    :params: a dataframe, a dataframe with summary data, a subject that is used to name
             one of the relative percentages
    :return: a dataframe with relative percentages


    sum_value = df_summary['How many'].sum()
    dataframe['percentage relative to all case studies'] = round(100 * (dataframe['How many']/sum_value),1)
    dataframe['percentage relative to case studies from each ' + subject] = round(100 * (dataframe['How many']/df_summary['How many']),1)

    return dataframe


def plot_bar_from_df(dataframe, y_col, title, y_axis_title):
    """
    :params: 
    :return: 
    """
    dataframe.plot(y = y_col, kind='bar', legend=None)
    plt.title(title)
    plt.ylabel(y_axis_title)
    # This provides more space around the chart to make it prettier        
    plt.tight_layout(True)
    filename = title.replace(" ", "_")
    print(filename)
    plt.savefig(CHART_RESULT_STORE + filename + '.png', format = 'png', dpi = 150)
#    plt.show()
    
    return
    
    
    
    # Create some names that will be used to represent strings that are used
    # to identify columns in the analysis
    found_in = 'found_in_'
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

    # Create a list of the cols that hold funder data in them
    funder_cols = col_locator(df, funder)

    # Create a dict of dataframes, each of which holds the data
    # related to a specific found_in, or funder
    # Start by adding the three locator lists together
    all_locator_cols = found_in_cols + funder_cols
    dict_of_dfs = {}
    
    # Drop all columns that aren't related to the found_in or funder
    #  in which we're interested, and store them in a dict of dataframes for later processing
    for name in all_locator_cols:
        dict_of_dfs[name] = df.dropna(subset=[name], how='all')

    # Create summaries of the data based on where the term was found
    # and by who funded it
    df_summary_found_in = summarise_dfs(dict_of_dfs, found_in_cols, found_in)
    df_summary_funder = summarise_dfs(dict_of_dfs, funder_cols, funder)

    # Now do the same, but based on the df that contains only
    # case studies related to software
    dict_of_software_dfs = {}
    for name in funder_cols:
        dict_of_software_dfs[name] = df_software.dropna(subset=[name], how='all')

    # Create summaries of the df that contains only case studies
    # related to software
    df_summary_software_by_funder = summarise_dfs(dict_of_software_dfs, funder_cols, funder)
    df_summary_software_by_funder = relative_percentages(df_summary_software_by_funder, df_summary_funder, 'funder')


    ########## Prepping for plotting ###############
        
    for index_name in df_summary_funder.index.values:
        df_summary_funder.rename(index={index_name: short_plot_labels_funder[index_name]}, inplace=True)
        df_summary_software_by_funder.rename(index={index_name: short_plot_labels_funder[index_name]}, inplace=True)

    ############ Plotting #############

    # Add a new sublist to add a new plot
    # list should be of the form: [df name, values column, title of chart]
#    vanilla_plots = [
#       [df_summary_funder, 'all ref case studies by funder'],
#       [df_summary_found_in, 'ref case studies including the word ' + WORD_TO_SEARCH_FOR + ' by location of word'],
#       [df_summary_software_by_funder, 'ref case studies including the word ' + WORD_TO_SEARCH_FOR + ' by funder']
#    ]


    vanilla_plots = [
       [df_summary_funder, 'all ref case studies by funder'],
       [df_summary_found_in, 'located ref case studies by location of word'],
       [df_summary_software_by_funder, 'located ref case studies by funder']
    ]
    
    for count in range(0,len(vanilla_plots)):
        plot_bar_from_df(vanilla_plots[count][0], 'How many', vanilla_plots[count][1], 'Number')
        plot_bar_from_df(vanilla_plots[count][0], 'percentage', vanilla_plots[count][1] + ' (percentage)', 'Percentage')
        write_results_to_xls(vanilla_plots[count][0], vanilla_plots[count][1])
'''

if __name__ == '__main__':
    main()
