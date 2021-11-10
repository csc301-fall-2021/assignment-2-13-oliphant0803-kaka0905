import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'api')))
import app
import unittest
from unittest.mock import MagicMock,Mock,patch
import sqlite3
import requests
import responses
import json

#################################################################################################################
#                                                                                                               #
#                                             Time Series                                                       #
#                                                                                                               #
#################################################################################################################

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



if __name__ == "__main__":
    unittest.main()
