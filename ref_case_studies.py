#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
import matplotlib.pyplot as plt
import math
import re

# The word we're going to look for - in lowercase please
SEARCH_TERM_LIST = ['software', 'computational', 'computation', 'computed', 'hpc', 'simulation', 'simulated', 'visualisation', 'visualization', 'python', 'matlab', 'git', 'spss', 'excel', 'nvivo', 'imagej', 'stata', 'fortran', 'modelling', 'model', 'r language']

# Other global variables
DATAFILENAME = "./data/all_ref_case_study_data.csv"
# This is test data set made by randomly deleting 90% of the rows of the real data set
# It makes life faster when prototyping
#DATAFILENAME = "./data/test_data_only.csv"
STUDIES_BY_FUNDER = "./data/list_of_studies_by_council.xlsx"
UNITS_OF_ASSESSMENT = "./data/units_of_assessment.xlsx"
RESULT_STORE = "./outputs/"
CHART_RESULT_STORE = "./outputs/charts/"


def import_xls_to_df(filename, name_of_sheet):
    """
    Imports an Excel file into a Pandas dataframe
    :params: get an xls file and a sheetname from that file
    :return: a df
    """
    return pd.read_excel(filename,sheetname=name_of_sheet)


def import_csv_to_df(filename):
    """
    Imports a csv file into a Pandas dataframe
    :params: a csv file
    :return: a df
    """
    
    return pd.read_csv(filename)


def export_to_csv(df, location, filename):
    """
    Exports a df to a csv file
    :params: a df and a location in which to save it
    :return: nothing, saves a csv
    """

    return df.to_csv(location + filename + '.csv')


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
        # Get list of cols that match the curr_place
        matching = [s for s in cols_list if curr_place in s]
        # Drop all rows where NaN across the "matching" list
        temp_df = df.dropna(subset=[matching], how='all', axis=0)
        summary_data[curr_place] = len(temp_df)
    
    summary_df = pd.DataFrame(list(summary_data.items()), columns=['word location', 'count matching 1 word'])    
    summary_df['% of all studies'] = round(100 * (summary_df['count matching 1 word']/all_case_study_count),0)
    summary_df.sort_values(['count matching 1 word'], ascending=False, inplace=True)

    # Now that we've sorted the count for a single word found in the df
    # see how many words have multiple matches
    for i in range(2, len(SEARCH_TERM_LIST)+1):
        shortened_df = df[df['search terms found'] == i]
        count_plus_i_word = {}
        for curr_place in search_places:
            matching = [s for s in cols_list if curr_place in s]
            temp_df = shortened_df.dropna(subset=[matching], how='all', axis=0)
            count_plus_i_word[curr_place] = len(temp_df)
        summary_df['count matching ' + str(i) + ' words'] = summary_df['word location'].map(count_plus_i_word)
        summary_df['% all studies ' + str(i) + ' words'] = round(100 * (summary_df['count matching ' + str(i) + ' words']/all_case_study_count),0)
        
    summary_df.set_index('word location', inplace=True)
    
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

    # Create a df from the dict
    summary_df = pd.DataFrame(list(uoa_term_found_dict.items()), columns=['unit of assessment', 'software reliant count'])    
    # Add a column to the summary from the uoa_all_dict
    summary_df['all studies count'] = summary_df['unit of assessment'].map(uoa_all_dict)
    summary_df.set_index('unit of assessment', inplace=True)

    summary_df['percentage of studies in this uoa'] = round(100 * (summary_df['software reliant count']/summary_df['all studies count']),0)
    summary_df['percentage of all studies'] = round(100 * (summary_df['software reliant count']/all_case_study_count),0)
    summary_df.sort_values(['software reliant count'], ascending=False, inplace=True)

    return summary_df

def summarise_word_popularity(df, all_case_study_count):
    
    # Get a list of all the found_in columns
    matching = [s for s in df.columns if 'found_in' in s]
    # Remove the any_term part, because it's a summary that we don't need
    matching.remove('any_term_found_in_anywhere')
    
    matches_to_search_term = {}
    
    for curr_term in SEARCH_TERM_LIST:
        curr_term_match = [s for s in matching if curr_term in s]
        temp_df = df.dropna(subset=[curr_term_match], how='all', axis=0)
        matches_to_search_term[curr_term] = len(temp_df)

    summary_df = pd.DataFrame(list(matches_to_search_term.items()), columns=['search term', 'count'])    
    summary_df['% of all studies'] = round(100 * (summary_df['count']/all_case_study_count),0)
    summary_df.sort_values(['count'], ascending=False, inplace=True)
    summary_df.set_index('search term', inplace=True)

    return summary_df


def plot_bar_from_df(df, y_col, title, x_axis_title, y_axis_title):
    """
    Plot a functional, rather than a pretty, chart
    Pretty charts can be made in the "graphing for presentations code" repo in Github
    """


    ax = df.plot(y = y_col, kind='bar', legend=None)
    for i, each in enumerate(df.index):
        y = df.ix[each][y_col]
        ax.text(i-0.3, y+0.2, int(y))

    plt.tick_params(top='off', bottom='off', left='off', right='off')

    plt.title(title)
    plt.xlabel(x_axis_title)
    plt.ylabel(y_axis_title)

    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


    labels = df[y_col].tolist()
    
    # This provides more space around the chart to make it prettier        
    plt.tight_layout(True)
    filename = title.replace(" ", "_")
    plt.savefig(CHART_RESULT_STORE + filename + '.png', format = 'png', dpi = 150)
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
    # we want to search. I've removed 'References to the research' from the list
    # because it's too uncoupled from the actual case study content
    possible_search_places = ['Title', 'Summary of the impact', 'Underpinning research', 'Details of the impact']

    # Import dataframe from original xls
    df = import_csv_to_df(DATAFILENAME)
    
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
    df.loc[df[found_in_cols].notnull().any(1), 'any_term_found_in_anywhere'] = 'anywhere'

    # Count the number of terms found in each record
    df['search terms found'] = df[found_in_cols].apply(lambda x: x.count(), axis=1)

    temp = df['search terms found'].unique().tolist()
    temp.sort()


    # Add anywhere to the search places, because it's an addition that's not in
    # the original list
    found_in_cols.append('any_term_found_in_anywhere')
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

    df_summary_popularity = summarise_word_popularity(df, all_case_study_count)

    # Write out to Excel
    export_to_csv(df_term_identified, RESULT_STORE, 'only_case_studies_with_search_term_identified')   
    export_to_csv(df_summary_terms, RESULT_STORE, 'summary_of_terms_found')
    export_to_csv(df_summary_funders, RESULT_STORE, 'summary_of_funders')
    export_to_csv(df_summary_uoas, RESULT_STORE, 'summary_of_uoas')
    export_to_csv(df_summary_popularity, RESULT_STORE, 'summary_of_word_popularity')

    plot_bar_from_df(df_summary_popularity, '% of all studies', 'Incidence of search words in REF 2014 case studies', '', 'As percentage of all case studies')


if __name__ == '__main__':
    main()
