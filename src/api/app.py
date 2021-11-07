from sqlite3.dbapi2 import IntegrityError
from flask import Flask, request, jsonify, json, Response
import datetime
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import sqlite3

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
                print(start_check[0], end_check[0])
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
    inputone(req_Json['confirmed'], 'confirmed')
    inputone(req_Json['death'], 'death')
    inputone(req_Json['recovered'], 'recovered')
    return jsonify({"response": "update successfully"})

def inputone(data, tablename):
    """
    Given a row of data for a table, input the data into that table
    """
    if data == 'noupdate':
        return 
    if not checkvalid(data):
        return Response("Invalid data body", status=400,)
    try:
        conn = timeseries_connection()
        cursor = conn.cursor()
        data = data.split(",")
        data[0] = '"{}"'.format(data[0])
        data[1] = '"{}"'.format(data[1])
        data = ",".join(data)
        cursor.execute('INSERT or REPLACE INTO {} VALUES ({})'.format(tablename, data))
        conn.commit()
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
    such as a non-numeric value of deaths.
    """
    #check comma separated:
    if not "," in data:
        return False
    #check if one line:
    if "/n" not in data:
        return checktype(data)

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


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == "GET":
        return jsonify({"response": "You can enter your name in POST request"})
    elif request.method == "POST":
        req_Json = request.json
        name = req_Json['name']
        return jsonify({"response": "Hi " + name})

if __name__ == '__main__':
    clear_timeseries()
    timeseries_init()
    app.run(debug=True, port=9803)