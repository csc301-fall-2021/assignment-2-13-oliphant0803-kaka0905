import datetime
from sqlite3.dbapi2 import IntegrityError
from flask import Flask, request, jsonify, json, Response
import pandas as pd
import sqlite3
import pandas
import json
import csv
import os
import re

"""
Users are allow to have csv options for each of the GET or POST call of the API
"""

def write_csv(rows, csv_name,header):
    path = os.path.join('../timecsv/', csv_name)
    fp = open(path, 'w')
    myFile = csv.writer(fp)
    if header:
        myFile.writerow(rows)
    else:
        myFile.writerows(rows)
    fp.close()

#################################################################################################################
#                                                                                                               #
#                                             Time Series                                                       #
#                                                                                                               #
#################################################################################################################

def timeseries_connection():
    conn = None
    try:
        conn = sqlite3.connect("databases/timeseries.db")
    except sqlite3.Error as e:
        return Response(str(e), status=400,)
    return conn

def clear_timeseries():
    try:
        conn = timeseries_connection()
        cursor = conn.cursor()

        sql_query = """DROP TABLE IF EXISTS confirmed"""
        cursor.execute(sql_query)

        sql_query = """DROP TABLE IF EXISTS death"""
        cursor.execute(sql_query)

        sql_query = """DROP TABLE IF EXISTS recovered"""
        cursor.execute(sql_query)
    except sqlite3.Error as e:
        return Response(str(e), status=400,)

def timeseries_init():
    try:
        conn = timeseries_connection()
        cursor = conn.cursor()

        sql_query = """CREATE TABLE IF NOT EXISTS confirmed (
            'Province/State' text,
            'Country/Region' text NOT NULL,
            Lat real NOT NULL,
            Long real NOT NULL,
            UNIQUE('Province/State', 'Country/Region')
        )"""
        cursor.execute(sql_query)
        sql_query = """CREATE TABLE IF NOT EXISTS death (
            'Province/State' text,
            'Country/Region' text NOT NULL,
            Lat real NOT NULL,
            Long real NOT NULL,
            UNIQUE('Province/State', 'Country/Region')
        )"""
        cursor.execute(sql_query)
        sql_query = """CREATE TABLE IF NOT EXISTS recovered (
            'Province/State' text,
            'Country/Region' text NOT NULL,
            Lat real NOT NULL,
            Long real NOT NULL,
            UNIQUE('Province/State', 'Country/Region')
        )"""
        cursor.execute(sql_query)
    except sqlite3.Error as e:
        return Response(str(e), status=400,)

app = Flask(__name__)

def dateformat(date):
    date = str(date).split('-')
    return date[1] + '/' + date[2] + '/' + date[0]

def addCol(colName):
    try:
        conn = timeseries_connection()
        cursor = conn.cursor()
        cursor.execute('ALTER TABLE confirmed ADD COLUMN "{}" integer'.format(colName))
        cursor.execute('ALTER TABLE death ADD COLUMN "{}" integer'.format(colName))
        cursor.execute('ALTER TABLE recovered ADD COLUMN "{}" integer'.format(colName))
    except sqlite3.Error as e:
        return Response(str(e), status=400,)

@app.route('/time_series', methods=['GET'])
def instruction():
    return jsonify({"response": "In /time_series/header, you will be entering data format for time series, please enter the header seperated by commas" + 
                                " expected format: Province/State,Country/Region,Lat,Long, 1/22/20(start date), 10/06/21(end date)" +
                                "where date year must be 2020 or 2021"}) 
@app.route('/time_series/header', methods=['GET', 'POST'])
def headerInfo():
    """
    GET: Show the list of column names to the users
    POST: User can update the column names following the format of time series csv, the update will be done for all recovered, death, confirmed tables 
    """
    if request.method == "GET":
        conn = timeseries_connection()
        cursor = conn.cursor()
        tableQuery = "select * from confirmed"  
        cursor.execute(tableQuery)

        names = [description[0] for description in cursor.description]
        return jsonify({"Header": str(names)}) 
    elif request.method == "POST":
        req_Json = request.json
        header = req_Json['header'].split(',')
        if not (header[0] == "Province/State" and 
                header[1] == "Country/Region" and
                header[2] == "Lat" and header[3] == "Long"):
                return jsonify({"valid": "Not valid header"})
        #check wether header[4] and header[5] are valid date format and end date is after start date
        try:
            start_check, end_check = header[4].split('/'), header[5].split('/')
            if not int(start_check[0]) in list(range(1, 13)) or not int(end_check[0]) in list(range(1, 13)):
                return Response("Invalid header, wrong date format in month",
                    status=400,
                )
            elif not int(start_check[1]) in list(range(1, 32)) or not int(end_check[1]) in list(range(1, 32)):
                return Response("Invalid header, wrong date format in day",
                    status=400,
                )
            elif not int(start_check[2]) in [20,21] or not int(end_check[2]) in [20,21]:
                return Response("Invalid header, wrong date format in year",
                    status=400,
                )
        except ValueError:
            return Response("Invalid input",
                    status=400,
                )
        #all the date are correct, start to generate header from start date to end date
        start_check[2], end_check[2] = "20" + str(start_check[2]), "20" + str(end_check[2])
        #convert into panda datetime
        s_date, e_date = '-'.join(start_check), '-'.join(end_check)
        for d in pd.date_range(s_date, e_date).tolist():
            addCol(dateformat(str(d.date())))
        conn = timeseries_connection()
        cursor = conn.cursor()
        tableQuery = "select * from confirmed"  
        cursor.execute(tableQuery)

        names = [description[0] for description in cursor.description]
        
        #if csv option is true
        path = req_Json['csv']
        if path != '':
            write_csv(names, path,True)
        return jsonify({"Success": "header is generated, can process to /time_series/input to input csv body"+str(names)})

@app.route('/time_series/view_data', methods=['POST'])

def view():
    """
    Input a table name, return the data body of that table (confirmed, death, recovered)
    """
    req_Json = request.json
    if req_Json['data'] not in ('confirmed', 'death', 'recovered'):
        return Response("Invalid table name", status=400,)
    try:
        conn = timeseries_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * from {}'.format(req_Json['data']))
        data = cursor.fetchall()
    except sqlite3.Error as e:
        return Response(str(e), status=400,)

    path = req_Json['csv']
    if path != '':
        write_csv(data, path,False)
    
    return jsonify({req_Json['data']: data})

@app.route('/time_series/add_data', methods=['POST'])
    # the given csv body only accepts comma-separated body
    # the input can contain one or more lines
def input():
    """
    users can parse in either one row data, or multiple row data as long as matching the validity with valid header 
    (can be updated and checked in /time_series/header)
    the post request will be ask for 3 fields where matching confirmed, death, recovered respectively
    if you do not have anything to update for one field, write 'noupdate'.
    """
    req_Json = request.json
    if not inputone(req_Json['confirmed'], 'confirmed'):
        return Response("Invalid data for confirmed", status=400,)
    if not inputone(req_Json['death'], 'death'):
        return Response("Invalid data for death", status=400,)
    if not inputone(req_Json['recovered'], 'recovered'):
        return Response("Invalid data for recovered", status=400,)
    return jsonify({"response": "update successfully"})

def inputone(data, tablename):
    """
    Given a row of data for a table, input the data into that table
    """
    try:
        if not checkvalid(data):
            return False
        conn = timeseries_connection()
        cursor = conn.cursor()
        data = data.split(",")
        data[0] = '"{}"'.format(data[0])
        data[1] = '"{}"'.format(data[1])
        data = ",".join(data)
        cursor.execute('INSERT or REPLACE INTO {} VALUES ({})'.format(tablename, data))
        conn.commit()
        return True
    except sqlite3.Error as e:
        return Response(str(e), status=400,)

def checktype(row):
    """
    Given a row of data, seperate the row by comma and check if each type are corresponding correctly
    """
    try:
        row = row.split(',')
        if not type(row[0]) == str or not type(row[1]) == str:
            return False
        elif not type(float(row[2])) == float or not type(float(row[3])) == float:
            return False
        for r in row[4:]:
            if not r.isnumeric():
                return False
            if int(r) < 0:
                return False
        return True
    except (ValueError, TypeError, NameError):
        return False

def checkvalid(data):
    """
    - The file received might not be a proper csv file 
    (i.e., comma-separated, newlines etc);
    - The file received might not follow the naming convention;
    - The file received might miss any of the fields;
    - The file received might contain invalid values for any of the fields, 
    such as a non-numeric value of deaths, or any negative numbers.
    """
    #check comma separated:
    if not "," in data:
        return False
    #check if one line with valid data:

    if not checktype(data):
        return False

    #check if the number of commas matches the number of entries
    try:
        conn = timeseries_connection()
        cursor = conn.cursor()
        tableQuery = "select * from confirmed"  
        cursor.execute(tableQuery)
        names = [description[0] for description in cursor.description]
        #the number of columns does not match the number of entries
        if len(names) != len(data.split(",")):
            return False
        return True
    except sqlite3.Error as e:
        return Response(str(e), status=400,)

@app.route('/time_series/interval', methods=['POST'])
def interval():
    """
    Locations must be a  list of (Province/State, Country/Region) tuple
    province can be none, then it will return for whole countries
    countries can not be none
    """
    req_Json = request.json
    locations = req_Json['locations']
    s_date = req_Json['start']
    e_date = req_Json['end']
    summary = []
    for location in locations.split(";"):
        location = location.split(",")
        key = ','.join(location) + ','
        r = cp_interval(location[0], location[1], s_date, e_date)
        active = int(r.split(",")[3])
        if active < 0:
            return Response("One of the data source is incorrect, active: {}".format(active), 
            status=400,)
        row = key + r
        summary.append([row.strip()])
    rows = []
    for r in summary:
        t = []
        for i in r[0].split(","):
            t.append((i))
        rows.append(t)
    path = req_Json['csv']
    if path != '':
        write_csv(rows, path,False)
    
    return jsonify({"response": str(rows)})

def cp_interval(province, country, s_date, e_date):
    """
    given a interval of time period, the function will compute the statistics (confirmed, death, active, recovered) among that interval
    for a given country, or province. (start_date, end_date) inclusive where active = confirmed - death - recovered
    both start_date and end_date are in format of M/D/YY as in csv
    one day if start_date = end_date
    """
    if province == '':
        confirmed, death, recovered = 0, 0, 0
        try:
            dates = generatedate(s_date, e_date) 
            conn = timeseries_connection()
            cursor = conn.cursor()
            for date in dates:
                selectQuery = 'select "{}" from confirmed where "Country/Region" = "{}"'.format(date, str(country))  
                cursor.execute(selectQuery)
                resultquery = cursor.fetchall()
                for t in resultquery:
                    confirmed += t[0]

                selectQuery = 'select "{}" from death where "Country/Region" = "{}"'.format(date, str(country))  
                cursor.execute(selectQuery)
                resultquery = cursor.fetchall()
                for t in resultquery:
                    death += t[0]

                selectQuery = 'select "{}" from recovered where "Country/Region" = "{}"'.format(date, str(country))  
                cursor.execute(selectQuery)
                resultquery = cursor.fetchall()
                for t in resultquery:
                    recovered += t[0]
                
            active = confirmed - death - recovered
            return '{},{},{},{}'.format(confirmed, death, recovered, active)
        except sqlite3.Error as e:
            return Response(str(e), status=400,)

    else:
        confirmed, death, recovered = 0, 0, 0
        try:
            dates = generatedate(s_date, e_date) 
            conn = timeseries_connection()
            cursor = conn.cursor()
            for date in dates:
                selectQuery = 'select "{}" from confirmed where "Country/Region" = "{}" and "Province/State" = "{}"'.format(date, str(country), str(province))  
                cursor.execute(selectQuery)
                resultquery = cursor.fetchall()
                for t in resultquery:
                    confirmed += t[0]

                selectQuery = 'select "{}" from death where "Country/Region" = "{}" and "Province/State" = "{}"'.format(date, str(country), str(province))  
                cursor.execute(selectQuery)
                resultquery = cursor.fetchall()
                for t in resultquery:
                    death += t[0]

                selectQuery = 'select "{}" from recovered where "Country/Region" = "{}" and "Province/State" = "{}"'.format(date, str(country), str(province))   
                cursor.execute(selectQuery)
                resultquery = cursor.fetchall()
                for t in resultquery:
                    recovered += t[0]
                
            active = confirmed - death - recovered

            return '{},{},{},{}'.format(confirmed, death, recovered, active)
        except sqlite3.Error as e:
            return Response(str(e), status=400,)

def generatedate(start, end):
    dates = []
    try:
        start_check, end_check = start.split('/'), end.split('/')
        if not int(start_check[0]) in list(range(1, 13)) or not int(end_check[0]) in list(range(1, 13)):
            return Response("Invalid header, wrong date format in month",
                status=400,
            )
        elif not int(start_check[1]) in list(range(1, 32)) or not int(end_check[1]) in list(range(1, 32)):
            return Response("Invalid header, wrong date format in day",
                status=400,
            )
        elif not int(start_check[2]) in [20,21] or not int(end_check[2]) in [20,21]:
            return Response("Invalid header, wrong date format in year",
                status=400,
            )
    except ValueError:
        return Response("Invalid input",
                status=400,
            )
    #all the date are correct, start to generate header from start date to end date
    start_check[2], end_check[2] = "20" + str(start_check[2]), "20" + str(end_check[2])
    #convert into panda datetime
    s, e = '-'.join(start_check), '-'.join(end_check)
    for d in pd.date_range(s, e).tolist():
        df = dateformat(str(d.date()))
        dates.append(df)
    return dates



#################################################################################################################
#                                                                                                               #
#                                           Daily Report                                                        #
#                                                                                                               #
#################################################################################################################
def daily_csv(rows, csv_name,header):
    path = os.path.join('../dailycsv/', csv_name)
    fp = open(path, 'w')
    myFile = csv.writer(fp)
    if header:
        myFile.writerow(rows)
    else:
        myFile.writerows(rows)
    fp.close()

def dailyreport_connection():
    conn = None
    try:
        conn = sqlite3.connect("databases/dailyreport.db")
    except sqlite3.Error as e:
        return Response(str(e), status=400,)
    return conn

def clear_dailyreport():
    try:
        # get the all the table names in dailyreport.db
        conn = dailyreport_connection()
        cursor = conn.cursor()
        tablesquery = """SELECT * FROM dates"""
        cursor.execute(tablesquery)
        dates = cursor.fetchall()
        for d in dates:
            name = d[0]
            print(name)
            remove_query = "DROP TABLE IF EXISTS '{}'".format(name)
            cursor.execute(remove_query)
        clean_query = """DELETE FROM dates"""
        cursor.execute(clean_query)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
        return Response(str(e), status=400,)

def dailyreport_init():
    try:
        conn = dailyreport_connection()
        cursor = conn.cursor()

        sql_query = """CREATE TABLE IF NOT EXISTS 'dates' (
            stored_date text UNIQUE 
        )"""
        cursor.execute(sql_query)
    except sqlite3.Error as e:
        return Response(str(e), status=400,)

@app.route('/daily_report', methods=['GET'])
def dailyreport():
    return jsonify({"response": "In /daily_report/, you will be entering data format for time series, please enter the header seperated by commas"},
                    {"format":   "FIPS,Admin2,Province_State,Country_Region,Last_Update,Lat,Long,Confirmed,Deaths,Recovered,Active,Combined_Key,Incidence_Rate,Case-Fatality_Ratio"}) 

@app.route('/daily_report/view_data', methods=['POST'])
def view_daily():
    """
    view a table for the given date
    """
    req_Json = request.json
    date = req_Json['date']
    month, day, year = date.split("-")
    try:
        datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        return Response("Invalid date", status=400,)
    try:
        conn = dailyreport_connection()
        cursor = conn.cursor()
        view_query = """SELECT * FROM '{}'""".format(date)
        cursor.execute(view_query)
        result = cursor.fetchall()
        path = req_Json['csv']
        if path != '':
            daily_csv(result, path,False)
        
        return jsonify({date: result})
    except sqlite3.Error as e:
        return Response(e, status=400,)
    

@app.route('/daily_report/update_data', methods=['POST'])
def input_daily():
    """
    POST: user input the data date, data body and wether or whether or not to turn it into a csv output,
    note the the data date has to be format of MM-DD-YYYY, and data body has to have valid row in each line
    if the date already exsists, the new update will overwrite/replace the change if and only if the combined key are the same
    """
    #check for input date
    req_Json = request.json
    date = req_Json['date']
    month, day, year = date.split("-")
    try:
        datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        return Response("Invalid date, status=400,")

    #check the data body is valid for each line
    data = req_Json['data']
    for row in data.splitlines():
        if not valid_format(row):
            return Response("Invalid data body", status=400,)

    #create table
    try:
        conn = dailyreport_connection()
        cursor = conn.cursor()

        table_query = """CREATE TABLE IF NOT EXISTS '{}' (
            FIPS text,
            Admin2 text,
            Province_State text,
            Country_Region text NOT NULL,
            Last_Update text NOT NULL,
            Lat float NOT NULL,
            Long float NOT NULL,
            Confirmed int NOT NULL,
            Deaths int NOT NULL,
            Recovered int NOT NULL,
            Active int NOT NULL,
            Combined_Key text NOT NULL,
            Incident_Rate float NOT NULL,
            Case_Fatality_Ratio float NOT NULL
        )""".format(date)
        cursor.execute(table_query)
        #input rows one each
        for row in data.splitlines():
            if not daily_input(date, row):
                return Response("failed to update", status=400,)

        #update dates
        conn = dailyreport_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT or REPLACE INTO dates VALUES ('{}')".format(date))
        conn.commit()
    except sqlite3.Error as e:
        return Response(str(e), status=400)
    return jsonify({"response": "Update Daily Report Succuessfully"})

def daily_input(date, row):
    try:
        row = split_row(row)
        row[5],row[6],row[7],row[8],row[9],row[10] = float(row[5]), float(row[6]), int(row[7]), int(row[8]), int(row[9]), int(row[10])
        row[12], row[13] = float(row[12]), float(row[13])
        conn = dailyreport_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT or REPLACE INTO "{}" VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'.format(date), row)
        conn.commit()

        #also check if any of the death,recovered,confirmd, active are negative numbers
        if row[7] < 0 or row[8] < 0 or row[9] < 0 or row[10] < 0:
            return False
        return True
    except sqlite3.Error as e:
        print(e)
        return False

def valid_format(row):
    try:
        row = split_row(row)
        if len(row) != 14:
            return False
        float(row[5]), float(row[6]), int(row[7]), int(row[8]), int(row[9]), int(row[10]), float(row[12]), float(row[13])
        if str(row[3]) == '':
            return False
        #check row[4] is date
        datetime.datetime.strptime(row[4],'%Y-%m-%d %H:%M:%S')
        #check row[11] is tuple key
        if not('(' == row[11][0] and ')' == row[11][-1]):
            return False
        key = row[11][1:-1]
        if row[0] == '' and row[1] == '':
            if len(key.split(",")) != 1:
                return False
        elif row[1] == '' or row[0] == '':
            if len(key.split(",")) != 2:
                return False
        elif len(key.split(",")) != 3:
            return False
        if len(key.split(",")) == 1:
            if key.split(",")[0] == row[2]:
                return True
        if len(key.split(",")) == 2:
            if key.split(",")[1] == row[2] and key.split(",")[0] in (row[1], row[0]):
                return True
        if len(key.split(",")) == 3:
            if key.split(",")[0] == row[0] and key.split(",")[1] == row[1] and key.split(",")[2] == row[2]:
                return True

    except (ValueError, TypeError, NameError):
        return False
    
    return True

def split_row(s):
    """
    Split `s` by top-level commas only. Commas within parentheses are ignored.
    """
    return re.split(r',(?!(?:[^(]*\([^)]*\))*[^()]*\))', s)

@app.route('/daily_report/interval', methods=['POST'])
def daily_summary():
    """
    Users provides time interval (start_time, end_time), as well as the province and country users want to do analysis on
    users can also input csv format option providing the path.
    Locations must be a  list of (Admin2, Province/State, Country/Region) seperated by ;
    where Country/Region must be not null
    """
    req_Json = request.json
    locations = req_Json['locations']
    s_date = req_Json['start']
    e_date = req_Json['end']
    summary = []
    for location in locations.split(";"):
        t = [location]
        for i in cp_interval(location, s_date, e_date):
            t.append(i)
        summary.append((t))

    path = req_Json['csv']
    if path != '':
        daily_csv(summary, path,False)
    return jsonify({"response":str(summary)})

def cp_interval(key, s_date, e_date):
    """
    (start_date, end_date) inclusive where active = confirmed - death - recovered
    both start_date and end_date are in format of M/D/YY as in csv
    one day if start_date = end_date
    """
    confirmed, death, recovered,active = 0, 0, 0, 0
    try:
        dates = generatedate(s_date, e_date)
        for date in dates:
            conn = dailyreport_connection()
            cursor = conn.cursor()
            selectQuery = """SELECT Confirmed, Deaths, Recovered, Active from '{}' 
            where Combined_Key = '{}' """.format(date, key)
            cursor.execute(selectQuery)
            result = cursor.fetchall()
            if result != [] and len(result[0]) == 4:
                confirmed += int(result[0][0])
                death += int(result[0][1])
                recovered += int(result[0][2])
                active += int(result[0][3])
        return [confirmed, death, recovered, active]
    except sqlite3.Error as e:
        print(e)
        return Response(str(e), status=400,)


def generatedate(s, e):
    dates = []
    for d in pd.date_range(s, e).tolist():
        df = dateformat(str(d.date()))
        df = "-".join(df.split("/"))
        dates.append(df)
    return dates

if __name__ == '__main__':
    clear_timeseries()
    timeseries_init()
    clear_dailyreport()
    dailyreport_init()
    app.run(debug=True, port=9803)