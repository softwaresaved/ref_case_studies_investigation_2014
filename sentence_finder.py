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

    for index, row in df.iterrows():
        for current in search_places:
            col_to_check = term_of_focus + '_found_in_' + current
            if isinstance(row[col_to_check], str):
                print()
                print(term_of_focus + ' found in ' + current)
                print()
                print(row[current])


    
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
