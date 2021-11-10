import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'api')))
import app
import unittest
from unittest.mock import MagicMock,Mock,patch
import sqlite3
import requests
from flask import Response
import json

#################################################################################################################
#                                                                                                               #
#                                             Time Series                                                       #
#                                                                                                               #
#################################################################################################################

# Test database connection
class TestConnection(unittest.TestCase):
    def test_sqlite3_connect_success(self):
        sqlite3.connect = MagicMock(return_value='connection succeeded')

        dbc = app.timeseries_connection()
        sqlite3.connect.assert_called_with("databases/timeseries.db")
        self.assertEqual(dbc, 'connection succeeded')

    def test_sqlite3_connect_fail(self):
        sqlite3.connect = MagicMock(return_value = 'connection failed')

        dbc = app.timeseries_connection()
        sqlite3.connect.assert_called_with("databases/timeseries.db")
        self.assertEqual(dbc, 'connection failed')

# Test time_series/header POST
url_header = "http://127.0.0.1:9803/time_series/header"
class TestHeader(unittest.TestCase):
    def test_header_valid(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,01/22/20,01/23/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        response_json = json.loads(resp.text)
        exp = {"Success": "header is generated, can process to /time_series/input to input csv body['Province/State', 'Country/Region', 'Lat', 'Long', '01/22/2020', '01/23/2020']"}
        exp = json.dumps(exp)
        exp_json = json.loads(exp)
        assert response_json == exp_json 
        assert resp.status_code == 200

    def test_header_valid_day_input(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,1/4/20,1/5/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        response_json = json.loads(resp.text)
        exp = {"Success": "header is generated, can process to /time_series/input to input csv body['Province/State', 'Country/Region', 'Lat', 'Long', '01/22/2020', '01/23/2020', '01/04/2020', '01/05/2020']"}
        exp = json.dumps(exp)
        exp_json = json.loads(exp)
        assert response_json == exp_json 
        assert resp.status_code == 200

    def test_header_valid_month_input(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,1/22/20,1/23/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        response_json = json.loads(resp.text)
        exp = {"Success": "header is generated, can process to /time_series/input to input csv body['Province/State', 'Country/Region', 'Lat', 'Long', '01/22/2020', '01/23/2020', '01/04/2020', '01/05/2020']"}
        exp = json.dumps(exp)
        exp_json = json.loads(exp)
        assert response_json == exp_json
        assert resp.status_code == 200

    def test_header_missing_province(self):
        info = {'header': "Country/Region,Lat,Long,01/22/20,01/23/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        response_json = json.loads(resp.text)
        exp = {"valid": "Not valid header"}
        exp = json.dumps(exp)
        exp_json = json.loads(exp)
        assert response_json == exp_json 

    def test_header_invalid_date_format(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,01-22-20,01-23-20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        assert resp.text == "Invalid input"
        assert resp.status_code == 400

    def test_header_invalid_year_input1(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,01/22/19,01/23/19", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        assert resp.text == "Invalid header, wrong date format in year"
        assert resp.status_code == 400

    def test_header_invalid_year_input2(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,01/22/2020,01/23/2021", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        assert resp.text == "Invalid header, wrong date format in year"
        assert resp.status_code == 400

    def test_header_invalid_month_input(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,13/22/20,13/23/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        assert resp.text == "Invalid header, wrong date format in month"
        assert resp.status_code == 400

    def test_header_invalid_day_input(self):
        info = {'header': "Province/State,Country/Region,Lat,Long,01/44/20,01/45/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url_header, json = request_json)
        assert resp.text == "Invalid header, wrong date format in day"
        assert resp.status_code == 400




if __name__ == "__main__":
    unittest.main()
