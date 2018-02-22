#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
from pandas import ExcelWriter
import numpy as np

# Other global variables
DATAFILENAME = "./data/all_ref_case_study_data.xlsx"
EXCEL_RESULT_STORE = "./data/"

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


def main():
    
    # Read in the data
    df = import_xls_to_df(DATAFILENAME, 'Sheet1')
    
    # Knock out a fraction (denoted by 'frac') of the rows of the dataframe
    df2 = df.drop(df.sample(frac=0.9, axis=0).index)

    # Save the data
    write_results_to_xls(df2, 'test_data_only')
    
if __name__ == '__main__':
    main()