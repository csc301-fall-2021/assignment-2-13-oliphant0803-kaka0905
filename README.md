[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-f059dc9a6f8d3a56e377f745f24479a46679e63a5d9fe6f495e02850cd0d8118.svg)](https://classroom.github.com/online_ide?assignment_repo_id=6163542&assignment_repo_type=AssignmentRepo)
# COVID DATA API
The Covid Data API is able to do the following for updating, summarizing and viewing covid data by calling the specific requests which will be described below in details. This API can be used for any web applications, and are able to be generated as csv files for users to export, a status of 400 will be retruned for any invalid input regarding to data format and unrealistic data (i.e. active cases of -1). The formats can be found on:


https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data


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
    end: end dates of the interval, if start = end, then it represent one day, if from start to end one date is not found in our database, status 400.
    csv: csv file name that to store with, or empty string indicating not to store as csv

## About the team
This project is done in group of 2 (Haoze Huang and Zewen Ma). We first started by considering the tech stacks that we will be using for the COVID-19 API, we processed with Python flask with Sqlite3 database for this project as both of us are familer with the sql queries as well as we had experienced with Flask App as API in Checkout Calculator. Therefore, we decided to work on the tech stacks that we both confident with.

Then, we talked about we will represent the objects in covid data in tables or csv files for both timeseries and daily report format. Where there are 3 tables timeseries, namely confirmed, death, recovered, which are responsible to store the confirmed cases, number of deaths and number of recovered cases in timeseries format. Regarding to daily report tables, we presents each day as a seperate table which stores the daily summaries of confirmed, death and recovered cases. We also have a dates table for daily report database to track which days have being stored.

The coding of this project is done on basis of pair programming with a driver and a naviagtor, Haoze Huang is responsible as a role of driver which code the solution for functionalies and design patterns the navigator (Zewen Ma) has come up with. The navigator was also responsible for writing out sample test json data for input to test by the driver. At the end, testing are done on postman (from driver's side) and pytest (from navigator's side). 

The experience of we pair programmed the way we described above instead of doing seperate parts (i.e. One does time_series and the other do daily_report) is that there are some shared logic for implementing these two different formats, as well as there are some common helper functions one can be used. With two people working on different parts, there might be some duplicated codes which is not ideally the most effective. With pair programming in driver and navigator way, we are able to solve the problems together and chat about the possible solutions which are better to solve the problem alone. Also, what we like about the driver and navigator approach is that we find out when bugs are easier to fix or detected when someone else is monitoring the code. However, there is also tradeoffs is that it is more time consuming, since we spend time solving the problems one by one instead of dividing and counquering the problems. 

Overall, we both enjoyed the pair programming for COVID-19 API, and we both gained valuable experience working together such as collabration and communication skills.

