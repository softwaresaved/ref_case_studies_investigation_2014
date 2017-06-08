# Investigation of REF case studies

The idea behind this code is to investigate the REF case studies that were recorded in 2014 to find how many reference software and then cross-section the resulting data based on aspects like which funder was involved and what field the research derived from.

# TOC
[Running the analysis](#running-the-analysis)
[Main files and dirs](#main-files-and-dirs)
[About the data](#about-the-data)
[Data origin](#data-origin)
[Problem number 1](#problem-number-1)
[Problem number 2](#problem-number-2)

## Running the analysis

The code runs is based on python 3.5 and is easiet to run in a virtual environment.

1. Clone this repo
1. Install a virtual environment [by following this guide](http://docs.python-guide.org/en/latest/dev/virtualenvs/). This will also install [pip](https://pip.pypa.io/en/stable/user_guide/) which is needed later.
1. Activate the virual environment using the command:
```source venv/bin/activate```
1. Install the libraries:
```pip install -r requirements.txt```
1. Now run the analysis code:
```python ref_case_studies.py```

## Main files and dirs

The main directory contains:

1. LICENSE: The licence for the python scripts in this repo
1. LICENSE_FOR_DATA: The licence for the data related to the case studies (imposed by the REF)
1. requirements.txt: used for easy import of the necessary libraries into the virtual environment (see [above](#running-the-analysis))
1. chart_label_lookup.py: used to swap out prettier versions of label names for the charts
1. ref_case_studies.py: the main script for conducting the analysis
1. organise_studies_by_funder.py: script for including funder details in analysis (see [below](#problem-number-1))
1. organise_studies_by_discipline.py: script for including Research Subject Area details in analysis (see [below](#problem-number-1))
1. data: directory in which all original data is stored
1. outputs: directory for storing all analysis outputs (charts and suchlike)

The data directory contains:

1. CaseStudies.xlsx: the case study data downloaded from the REF website (see [below](#data-origin))
1. studies_by_council: a directory storing spreadsheets each of which lists the case studies from a specific funder
1. list_of_studies_by_council.xlsx: all the data from the spreadsheets in "studies_by_council" directory merged into one spreadsheet
1. studies_by_research_subject_area: a directory storing spreadsheets each of which lists the case studies from a specific "Research Subject Area"
1. list_of_studies_by_discipline.xlsx: all the data from the spreadsheets in "research_subject_area" directory merged into one spreadsheet
1. universities_address.csv: plan is to use this to associate a university name with a postcode for easy map plotting

## About the data

### Data origin

The data is available from the the [REF website](http://impact.ref.ac.uk/CaseStudies/Results.aspx?val=Show%20All#)

The data used in the study (CaseStudies.xlsx) was downloaded on 6 April 2017 from [REF2014 case studies](http://impact.ref.ac.uk/CaseStudies/Results.aspx?val=Show%20All#). It includes all 6637 case studies available from REF 2014. The data was downloaded in Excel format and in the section entitled "Sections to include in download:" the "Select all" option was seleted.

### Problem number 1

There's an annoying issue with the REF data. You can query the case studies through the web interface to find all case studies by a specific funder, or all case studies from a specific research "Research Subject Area", and you will be presented with a list of case studies. However, the information is not included explicitly in the downloaded summary of the results. In other words, the Excel spreadsheet does not include a column entitle "Funder" or "Research Subject Area".

To counter this problem, I used the web interface and methodically downloaded Excel spreadsheets to detail the case studies for each funder (see data/studies_by_council) and each Research Subject Area (see data/studies_by_research_subject_area). I then used two scripts to identify the case studies that relate to a particular funder (organise_studies_by_funder.py) or Research Software Area (organise_studies_by_discipline.py) and identify this in the data by adding in new columns added to the CaseStudies.xlsx spreadsheet. The result is written to outputs/all_ref_case_study_data.xlsx. 

### Problem number 2

There's a mistake on the [REF website](http://impact.ref.ac.uk/CaseStudies/Results.aspx?val=Show%20All#). In the drop down for "Project Funders:" it states the name of the funder alongside a number in brackets that shows how many case studies are availabile from that funder. The number in the brackets for the EPSRC is wrong! It says 945, but if you select that option it shows that there are actually only 944 case studies available for the EPSRC. The numbers for the other funders are correct.
