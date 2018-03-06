#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np
import matplotlib.pyplot as plt
import math
import re

from search_terms import SEARCH_TERM_LIST

# Other global variables
DATAFILENAME = "./outputs/only_case_studies_with_search_term_identified.csv"
RESULT_STORE = "./outputs/"
CHART_RESULT_STORE = "./outputs/charts/"


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

def term_of_interest(terms):

    for current in terms:
        print(str(terms.index(current)) + ': ' + current)

    term_index = int(input('What term shall we look for? '))
    choice = terms[term_index]
    print()
    print('Okay, looking for: ' + choice)

    return choice


def find_terms_and_context(df, term_of_focus, search_places):

    # Find cols that have the term_of_focus in them
    matching = [s for s in df.columns if term_of_focus in s]
    
    if len(matching) == 0:
        print('No matches for that term in the data')
        return
    else:
        cols_to_keep = matching + search_places

    
    # Limit df to just the rows where a term_of_focus has been found
    focus_df = df.dropna(subset=[cols_to_keep], how='all', axis=0)

    # Go through each row of the df
    for index, row in focus_df.iterrows():
        # Construct a col header in which we will find a word if that word exists in that col
        for current in search_places:
            col_to_check = term_of_focus + '_found_in_' + current
            # If the entry in the col_to_check row is not nan, then investigate further
            if isinstance(row[col_to_check], str):
                # Set variable to change how much text should be printed
                # around term of focus
                offset = 70
                # Get the actual text
                whole_string = row[current]
                how_many = whole_string.split().count(term_of_focus)
                print(whole_string)
                print()
                print(term_of_focus + ' found in ' + current + ' ' + str(how_many) + ' times')
                print()
                start_index = whole_string.find(term_of_focus)
                end_index = start_index + len(term_of_focus)
                print('...' + whole_string[(start_index-offset):(end_index+offset)] + '...')
#                print(str(start_index) + ' ' + str(end_index))
#                print(row[current])


    
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

    # Import case study data
    df = import_csv_to_df(DATAFILENAME)
    
    term_of_focus = term_of_interest(SEARCH_TERM_LIST)

    find_terms_and_context(df, term_of_focus, possible_search_places)
    


if __name__ == '__main__':
    main()
