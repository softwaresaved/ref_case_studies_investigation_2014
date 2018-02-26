# Investigation of REF case studies

The idea behind this code is to investigate the REF case studies that were recorded in 2014 to find how many reference software by looking for software-related terms in the case studies. The results of this analysis are then summarised to find how many case studies are related to software, which funder was involved and what field the research is derived from.

I'm making the code open mainly so that the results I publish can be reproduced. However, the code could also be re-used if someone is interested in investigating other keywords that appear in the REF case studies.

# TOC

[Prerequisites](#prerequisites)

[Licences](#licences)

[Inputs, outputs, scripts and other files](#inputs-outputs-and-operation)

[Operation](#operation)

[About the data](#about-the-data)

[Notes](#notes)

# Prerequisites
The code requires Python 3. The libraries needed are described in the requirements.txt file.

# Licences

Details of licences can be found here:

1. LICENSE: The licence for the python scripts in this repo
1. LICENSE_FOR_DATA: The licence for the data related to the case studies (imposed by the REF)

# Inputs, outputs and operation

## Inputs

All inputs are stored in the data dir

1. CaseStudies.xlsx: the case study data available for download from the REF website (see [below](#data-origin))
1. studies_by_council dir: a series of xlsx files downloaded from the REF website, one for each funder covered in the REF case studies, which links that funder to a series of case studies (identified by their "Case study ID").
1. list_of_studies_by_council.csv: a list of each case study and its relevant funder
1. all_ref_case_study_data.csv: a new file, created by joining the above data, which contains all case study data and the relevant funding council
1. test_data_only.csv: a smaller data set used only whilst testing the code, which was derived by randomly dropping 90% of the all_ref_case_study_data file
1. units_of_assessment.csv: a list of the units of assessment (i.e. discipline areas) contained in the REF case studies saved from the [REF website](http://www.ref.ac.uk/2014/panels/unitsofassessment/) 

## Outputs

All outputs are stored in outputs dir

1. charts dir: store for all charts as pngs
1. only_case_studies_with_search_term_identified.csv: derived from all_ref_case_study_data.csv, but only containing the software-related case studies (i.e. the case studies where at least one search term was matched)
1. summary_of_funders.csv: a count of software-related case studies split by funder
1. summary_of_where_terms_found.csv: a count of software-related case studies split by which part of the case study matched the search term
1. summary_of_uoas.csv: a count of software-related case studies split by unit of assessment (i.e. discipline)
1. summary_of_word_popularity.csv: a count of how many times each search term was matched to the case studies

## Scripts

Two scripts were written to include funder data in the case studies. The reason why this is necessary is described [below](#note-1).

1. organise_studies_by_funder.py: runs through the files in studies_by_council dir to create list_of_studies_by_council.csv
1. merge_studies_with_funder.py: combines the CaseStudies.xlsx and list_of_studies_by_council.csv to produce all_ref_case_study_data.csv
1. reduce_df_for_test.py: reduces all_ref_case_study_data.csv by a fraction (set in FRACTION_TO_REDUCE) to produce an appropriately smaller data set (test_data_only.csv) for faster execution of scripts whislt testing changes
1. ref_case_studies.py: the main script. Finds the search terms in the case studies and produces the summary data and charts
requirements.txt

## Other files

1. requirements.txt: contains the libraries needed by the scripts

# Operation

1. Set the list of words you want to find in the case studies in in the SEARCH_TERM_LIST variable
1. Data is cleaned (made lower case, line breaks within cells are removed, multiple spaces replaced with single space)
1. The SEARCH_TERM_LIST are searched for in the different parts of each case study as listed in the possible_search_places variable (I don't include the "References" section because it's not directly linked to the case study and hence is likely to create false positives). Matching case studies are identified in new columns added to the dataframe
1. A new dataframe containing only case studies in which the SEARCH_TERM_LIST has been found is created and saved as only_case_studies_with_search_term_identified.csv
1. The data is summarised and the summaries are saved.

## Running the analysis

The code runs is based on python 3 and is easiest to run in a virtual environment.

The main analysis is run as follows:

1. Clone this repo
1. Install a virtual environment [by following this guide](http://docs.python-guide.org/en/latest/dev/virtualenvs/). This will also install [pip](https://pip.pypa.io/en/stable/user_guide/) which is needed later.
1. Activate the virual environment using the command:
```source venv/bin/activate```
1. Install the libraries:
```pip install -r requirements.txt```
1. Now run the analysis code:
```python ref_case_studies.py```

If you wish to verify the creation of the data used in the main analysis, you can also download the original data from the REF website and then run organise_studies_by_funder.py and then merge_studies_with_funder.py before running the main analysis. (For those particularly thorough people, you can also run the reduce_df_for_test.py to understand the test data creation if you intend to use it whilst editing the main analysis script.)

# About the data

## Data origin

The data is available from the the [REF website](http://impact.ref.ac.uk/CaseStudies/Results.aspx?val=Show%20All#)

The data used in the study (CaseStudies.xlsx) was downloaded on 6 April 2017 from [REF2014 case studies](http://impact.ref.ac.uk/CaseStudies/Results.aspx?val=Show%20All#). It includes all 6637 case studies available from REF 2014. The data was downloaded in Excel format and in the section entitled "Sections to include in download:" the "Select all" option was selected.

# Notes

There's a couple of foibles.

## Note 1

There's an annoying issue with the REF data: you can query the case studies through the web interface to find all case studies by a specific funder and you will be presented with a list of case studies. However, the information is not included explicitly in the downloaded summary of all case studies. However, you can download a spreadsheet for each funder that details the case study IDs of case studies that were funded by that funder. Hence, I used the web interface and methodically downloaded Excel spreadsheets for each funder and then used the scripts discussed above to include the funder data alongside the other case study data.

## Note 2

There's a mistake on the [REF website](http://impact.ref.ac.uk/CaseStudies/Results.aspx?val=Show%20All#). In the drop down for "Project Funders:" it states the name of the funder alongside a number in brackets that shows how many case studies are availabile from that funder. The number in the brackets for the EPSRC is wrong! It says 945, but if you select that option it shows that there are actually only 944 case studies available for the EPSRC. This seems like a data entry problem. The numbers for the other funders are correct.
