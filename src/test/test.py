import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'api')))
from app import *
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

url = "http://127.0.0.1:9803/time_series/header"

class TestHeader(unittest.TestCase):
    def test_header_valid(self):
        # file = open('test_header_valid1.json', 'r')
        # json_input = file.read()
        info = {'header': "Province/State,Country/Region,Lat,Long,01/22/20,01/23/20", 'csv': ""}
        info = json.dumps(info)
        request_json = json.loads(info)
        resp = requests.post(url, request_json)
        assert resp.status_code != 200



if __name__ == "__main__":
    unittest.main()
