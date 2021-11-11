[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-f059dc9a6f8d3a56e377f745f24479a46679e63a5d9fe6f495e02850cd0d8118.svg)](https://classroom.github.com/online_ide?assignment_repo_id=6163542&assignment_repo_type=AssignmentRepo)
# COVID DATA API
The Covid Data API is able to do the following for updating, summarizing and viewing covid data by calling the specific requests which will be described below in details. This API can be used for any web applications, and are able to be generated as csv files for users to export, a status of 400 will be retruned for any invalid input regarding to data format and unrealistic data (i.e. active cases of -1). 

## Functionalities and Constraints
More information for testing format can be checked via test/test.py
### Time Series Description (/time_series): 
GET method which returns a json instruction telling the user the steps to follow to begin with using time_series data.

### Time Series Header Update (/time_series/header): 
GET: Display the current header of a timeseries table
POST: User can update the column names following the format of time series csv, the update will be done for all recovered, death, confirmed tables 

    header: {Province/State, Country/Region, Lat, Long, Start_Date, End_Date}
    csv: either empty string or '{filename}.csv' which indicates name of csv to output to
Note: Start_Date and End_Date must be following M/D/YY format

### Time Series Data Body Update (/time_series/add_data):
POST: users can parse in either one row data, or multiple row data as long as matching the validity with valid header, users are expected to call this request multiple times for each row the data consists
    (can be updated and checked in /time_series/header)
    the post request will be ask for 3 fields where matching confirmed, death, recovered respectively
    if you do not have anything to update for one field, write 'noupdate'.

    confirmed: one line data body to input in confirmed table storing number of confirmed cases follwing the header format
    death: one line data body to input in death table storing number of death cases follwing the header format
    recovered: one line data body to input in recovered table storing number of recovered cases follwing the header format

### Time Series View Data (/time_series/view_data):
POST: Input a table name, return the data body of that table (confirmed, death, recovered)

    data: table name, in (confirmed, death or recovered)
    csv: csv file name that to store with, or empty string indicating not to store as csv

### Time Series Summary (/time_series/interval):
POST: Given any one day or period of time interval of a list of locations tuples, return the number of total confirmed cases, deaths, recovered, and active cases among that interval

    locations: a string representation of tuples including province, country indicate the location, province can be emptry, then it will return for whole countries, countries can not be none
    start: start dates of the interval
    end: end dates of the interval, if start = end, then it represent one day
    csv: csv file name that to store with, or empty string indicating not to store as csv

### Daily Report Instruction (/daily_report):
GET method which returns a json instruction telling the user the steps to follow to begin with using daily_report data.

### Daily Report Update Data (/daily_report/update_data):
POST: user input the data date, data body and wether or whether or not to turn it into a csv output,
    note the the data date has to be format of MM-DD-YYYY, and data body has to have valid row in each line
    if the date already exsists, the new update will overwrite/replace the change if and only if the combined key are the same

    date: string indicates the name of the date the data is describing, in format of MM-DD-YYYY
    data: data body for daily report format, with combined key in (), and /n for new line, following the header format {FIPS,Admin2,Province_State,Country_Region,Last_Update,Lat,Long,Confirmed,Deaths,Recovered,Active,Combined_Key,Incidence_Rate,Case-Fatality_Ratio}

### Daily Report View Data (/daily_report/view_data):
POST: view a table for the given date

    date: table name which indicates which date for daily report to view, the table must be a valid date users had added previously, or status 400 for invalid dates
    csv: csv file name that to store with, or empty string indicating not to store as csv

### Daily Report Summary (/daily_report/interval):
POST: Given any one day or period of time interval of a list of locations tuples, return the number of total confirmed cases, deaths, recovered, and active cases among that interval

    locations: a string representation of tuples including admin 2, province, country indicate the location, province and admin2 can be emptry, then it will return for whole countries, countries can not be none
    start: start dates of the interval
    end: end dates of the interval, if start = end, then it represent one day
    csv: csv file name that to store with, or empty string indicating not to store as csv

## About the team
This project is 

