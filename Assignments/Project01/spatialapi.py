#!/usr/bin/env python3
##############################################################################
# Author: Caleb Sneath
# Assignment: P01 - Project Setup
# Date: September 8, 2022
# Python 3.9.5
# Project Version: 0.1.0
#
# Description: A simple Python database API created for educational purposes.
# Contains three initial functions: 
# findOne: Takes the passed in attribute and value, then returns the
# first matching row in the table.
# Example syntax: 
# http://localhost:8081/findOne/abbreviation=TX
# findAll: Returns the contents of every row in the table.
# Example syntax: 
# http://localhost:8081/findAll/
# findClosest: 
# Example syntax: 
# http://localhost:8081/findClosest/longitude=-150.0&latitude=65.0
#
# Building: Requires Python (Tested for 3.9.5), FastAPI, and psycopg2.
# To install the last two, simply run in the terminal:
# pip install fastapi
# pip install psycopg2
# Afterward, set up your basic with pgAdmin and fill out the .config.json 
# file. Run this file in the terminal with spatialapi.py and it should work.
#
# Credit:
# Example data obtained from: 
# https://cs.msutexas.edu/~griffin/data/
#
# Largely based on code obtained from: 
# https://github.com/rugbyprof/5443-Spatial-DB/blob/main/Resources/04_ApiHelp/
# module/features.py
#
# Partial code snippet inspirations from:
# https://stackoverflow.com/questions/32812463/setting-schema-for-
# all-queries-of-a-connection-in-psycopg2-getting-race-conditi
#
# https://stackoverflow.com/questions/1984325/explaining-pythons-
# enter-and-exit
#
# https://gis.stackexchange.com/questions/145007/creating-geometry-
# from-lat-lon-in-table-using-postgis
##############################################################################

# Libraries for FastAPI
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Databse Libraries
import psycopg2

# Builtin libraries
from math import radians, degrees, cos, sin, asin, sqrt, pow, atan2
import os
import json
import sys

class DatabaseCursor(object):
    """
    Credit:
    https://raw.githubusercontent.com/rugbyprof/5443-Spatial-DB/main/
    Lectures/02_Chap2/main.py

    https://stackoverflow.com/questions/32812463/setting-schema-for-
    all-queries-of-a-connection-in-psycopg2-getting-race-conditi

    https://stackoverflow.com/questions/1984325/explaining-pythons-
    enter-and-exit
    """

    def __init__(self, conn_config_file):
        with open(conn_config_file) as config_file:
            self.conn_config = json.load(config_file)

    # Load object from information from the config file
    def __enter__(self):
        self.conn = psycopg2.connect(
            "dbname='"
            + self.conn_config["dbname"]
            + "' "
            + "user='"
            + self.conn_config["user"]
            + "' "
            + "host='"
            + self.conn_config["host"]
            + "' "
            + "password='"
            + self.conn_config["password"]
            + "' "
            + "port="
            + self.conn_config["port"]
            + " "
        )
        self.cur = self.conn.cursor()
        self.cur.execute("SET search_path TO " + self.conn_config["schema"])

        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        # some logic to commit/rollback

        self.conn.commit()
        self.conn.close()


description = \
"""
## Description
### This API is designed to be a quick and simple 
### Python backend for educational purposes.
"""

app = FastAPI(
    title="Spatial Databases API",
    description=description,
    version="0.1.0",
    contact={
        "name": "Caleb Sneath",
        "email": "ansengor@yahoo.com",
    },
)

@app.get("/")
async def docs_redirect():
    """Api's base route that displays the information created \
        above in the ApiInfo section."""
    return RedirectResponse(url="/docs")

"""
findOne
Returns a single tuple based on a column name (attribute) 
and value (e.g id=1299 , or name=texas).
Example syntax: 
 http://localhost:8081/findOne/abbreviation=TX
"""
@app.get("/findOne/{target}")
async def findOne(target):
    # Declare variables with proper scope
    attribute = ""
    value = ""
    tableName = ""

    try:
        # Extract our two fields from the URL 
        # string by delimiting the equals sign
        targetSplit = target.split("=")
        attribute = targetSplit[0]
        value = targetSplit[1]
    except:
        return ("Invalid URL field.")

    try:
        with DatabaseCursor(".config.json") as cur:
            with open(".config.json") as config_file:
                # Try to grab table name from the config file.
                configAttributes = json.load(config_file)
                tableName = configAttributes["table"]

            # Construct proper SQL query
            sql = f"""SELECT * from {tableName} 
                    WHERE {attribute} = '{value}' LIMIT 5"""
            cur.execute(sql)
            queryTuple = cur.fetchone()
            return queryTuple
    except:
        return ("Host database configuration error or invalid column field.")

"""
findAll
Returns all the tuples from your table
Example syntax: 
 http://localhost:8081/findAll/
"""
@app.get("/findAll/")
async def findAll():
    tableName = ""

    try:
        with DatabaseCursor(".config.json") as cur:
            with open(".config.json") as config_file:
                # Try to grab table name from the config file.
                configAttributes = json.load(config_file)
                tableName = configAttributes["table"]

            # Construct proper SQL query statement
            sql = f"""SELECT * FROM {tableName}"""
            cur.execute(sql)
            queryTuple = cur.fetchall()
            return queryTuple
    except:
        return ("Host database configuration error or invalid column field.")

"""
findClosest
Returns a single tuple which contains the closest geometry 
to the one passed in (e.g. lon=-123.63454&lat=34.74645).
Note: Longitude parameter must be first and latitude second
for correct usage, and geometry must be named, "geom".
Example syntax: 
 http://localhost:8081/findClosest/longitude=-150.0&latitude=65.0
"""
@app.get("/findClosest/{target}")
async def findClosest(target):
    # Declare variables with proper scope
    value1 = ""
    value2 = ""
    tableName = ""
    
    try:
        # Extract our four fields from the URL 
        # string by delimiting the equals sign
        # after converting our other delimiter to an equals
        targetSplit = (target.replace('&', '=')).split("=")
        #attribute1 = targetSplit[0]
        #attribute2 = targetSplit[2]
        value1 = str(targetSplit[1])
        value2 = str(targetSplit[3])
    except:
        return ("Invalid URL field.")

    try:
        with DatabaseCursor(".config.json") as cur:
            with open(".config.json") as config_file:
                # Try to grab table name from the config file.
                configAttributes = json.load(config_file)
                tableName = configAttributes["table"]

            # Construct proper SQL query statement
            sql = \
                f"""
                SELECT * FROM {tableName}
                  WHERE ((ST_Distance(geom, ST_SetSRID(ST_MakePoint({value1}, {value2}), 4326))) =
	                (SELECT MIN(ST_Distance(geom, ST_SetSRID(ST_MakePoint({value1}, {value2}), 4326)))
	  	                FROM {tableName}));
                """
            print(sql)
            cur.execute(sql)
            queryTuple = cur.fetchone()
            return queryTuple
    except:
        return ("Host database configuration error or invalid column field.")

if __name__ == "__main__":
    uvicorn.run("spatialapi:app", host="0.0.0.0", port=8081, log_level="debug", reload=True)