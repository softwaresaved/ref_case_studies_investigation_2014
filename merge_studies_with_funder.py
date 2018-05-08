#!/usr/bin/env python
# encoding: utf-8

import pandas as pd

# Other global variables
DATAFILENAME = "input/raw/CaseStudies.xlsx"
STUDIES_BY_FUNDER = "input/generated/list_of_studies_by_council.csv"
RESULT_STORE = "input/generated/"


def import_xls_to_df(filename, name_of_sheet):
    """Imports an Excel file into a Pandas dataframe.

    :params: get an xls file and a sheetname from that file
    :return: a df
    """
    return pd.read_excel(filename, sheetname=name_of_sheet)


def import_csv_to_df(filename):
    """Imports a csv file into a Pandas dataframe.

    :params: a csv file
    :return: a df
    """

    return pd.read_csv(filename)


def export_to_csv(df, location, filename):
    """Exports a df to a csv file.

    :params: a df and a location in which to save it
    :return: nothing, saves a csv
    """

    return df.to_csv(location + filename + '.csv')


def clean(dataframe):
    """Cleans the imported data for easy processing.

    Removes end of lines chars, multiple spaces, and lowercases everything

    :params: a dataframe
    :return: a dataframe with clean data
    """

    # Someone thought it would be a good idea to add line breaks
    # to the longer strings in Excel - this removes them
    dataframe = dataframe.replace(to_replace='\n', value=' ', regex=True)

    # There are also multiple spaces in the strings - this removes them
    dataframe = dataframe.replace('\s+', ' ', regex=True)

    # And now to remove the leading spaces and lowercase everything
    # Need to do this conditionally since some of the cols have integers
    for col in dataframe.columns:
        dataframe[col] = dataframe[col].map(lambda x: x.strip().lower() if isinstance(x, str) else x)

    return dataframe


def associate_new_data(dataframe, df_studies_by_funder):
    """Merge two dataframes based on Case Study ID.

    Takes a dataframe with the case study information and merges it with another
    dataframe that contains case study IDs and some other data (e.g. funders, disciplines)

    :params: a dataframe with case study information, a second dataframe with cases study IDs and other information
    :return: a dataframe containing case study information and other merged information
    """

    dataframe = pd.merge(left=dataframe, right=df_studies_by_funder, how='left', left_on='Case Study Id', right_on='Case Study Id')

    return dataframe


def main():
    # Import dataframe from original xls
    df = import_xls_to_df(DATAFILENAME, 'CaseStudies')

    # Clean data
    df = clean(df)

    # Import case study ids for each funder
    df_studies_by_funder = import_csv_to_df(STUDIES_BY_FUNDER)

    # Associate case study IDs with specific funders
    df = associate_new_data(df, df_studies_by_funder)

    # Export results
    export_to_csv(df, RESULT_STORE, 'all_ref_case_study_data')


if __name__ == '__main__':
    main()
