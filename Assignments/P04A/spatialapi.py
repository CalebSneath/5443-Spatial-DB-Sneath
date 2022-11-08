#!/usr/bin/env python3
##############################################################################
# Author: Caleb Sneath
# Assignment: P04 - Missile Defence Part 2
# Date: October 31, 2022
# Python 3.9.5
# Project Version: 0.2.0
#
# Description: A simple Python database API created for educational purposes
#              to simulate missile interception between an attacker and one
#              or more defenders. This is a defender API.
#
# Local Instructions:
# Building: Requires Python (Tested for 3.9.5), FastAPI, and psycopg2.
# To install the last two, simply run in the terminal:
# pip install fastapi
# pip install psycopg2
# Afterward, set up your basic with pgAdmin and fill out the .config.json 
# file. Adjust the line below to your install path if necessary for
# the confPath variable.
# Run this file in the terminal with spatialapi.py and it should work.
#
# Server Instructions: 
# Get whatever server provider you choose. Follow the above instructions
# for local install. If pip install fails for psycopg2, try with the
# precompiled binaries instead by using:
#   pip install psycopg2-binary
# For the ip address, ip probably needs to be set to "0.0.0.0" in config.
# Postgres and postgis may need to be installed also if they are not.
#
# Running Instructions:
# - After setting up with the above instructions, run "spatialapi.py".
# - Open up your web browser.
# - For all instructions below, {address} will be a placeholder for 
#   whatever ip and port you entered in the config file or for your server.
#   For example, if you are running on a server with ip "167.999.99.99",
#   and you selected port 8081, {address} would mean "167.999.99.99:8081".
#   Likewise, if it was instead on localhost with port 8080, it would be
#   "localhost:8081". Both of these are of course without the quotes.
# - For your first time running, in your address bar type and enter 
#   "http://{address}/createTables". This will create all tables for the
#   first time in the database. This shouldn't need to be done again.
# - Add whatever attacker's you need by typing into your address bar
#   "http://{address}/addAttackerIP/{target address}" where {target address}
#   follows a similar pattern as address, just for the attacker.
#   Repeat this for any attackers.
# - (Optional) To permanently save an attacker ip so this does not need
#   to be done again, in your address bar run 
#   "http://{address}/persistCurrentIPs"
# - To load up a new round of the simulation, run in your browser:
#   "http://{address}/initializeSimulation". This will not begin the 
#   simulation by itself to allow other people to get ready.
# - When you are ready to begin, run 
#   "http://localhost:8081/simulationControlLoop"
# - The simulation will either produce an error message or run until
#   the arsenal is depleted and then automatically send the messsage
#   to all attackers to end the simulation. 
# - To restart, just go back to the initializeSimulation step.
##############################################################################

# Libraries for FastAPI
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Databse Libraries
import psycopg2

# Network libraries
import requests

# Builtin libraries
from math import radians, degrees, cos, sin, asin, sqrt, pow, atan2
import os
import json
import sys
import time
import datetime

# Local project module
from module import convertTimeToSecondsSimple, convertTimeFromSecondsNoDate
from module import convertTimeToSecondsNoDate, convertTimeToSeconds
from module import convertTimeFromSeconds, convertDateToOtherDate
#from module import missiledbmanager


##############################################################################
#                          Tables Descriptions
# assigned_regions:           Holds geometry and ids of assigned regions
##  Columns:                  INT gid, INT cid, geometry boundary. Also
#                             has a serial key.
# points_of_interest:         Holds any points within assigned region
#                             such as missile batteries or target cities
##  Columns:                  INT point_id, 
##                            Geometry 4326 Point point_geometry,
##                            TEXT point_category. Also
#                             has a serial key.
# missile_spec_key:           Lists the specifications of all active classes
#                             of missiles. Note, speed and radius categories
#                             are worthless without conversion to an outside
#                             scale of some kind.
##  Columns:                  text classification_label, INT speed_category
##                            (Note: scaled 1-9),INT radius_label (also 1-9).
##                            Also has a serial key.
# active_missile_pings:       Lists 1 - 2 (maybe 3 if nonlinear adversary
#                             missile motion) radar pings per hostile missile
#                             to help interpolate missile paths
#                             and decide how to react.
##  Columns:                  INT missile_id, Geometry 4326 Point intersects, 
##                            INT time_code, text missile_type.  Also
##                            has a serial key.
# trajectory_prediction:      Scratch database to make query syntax easier
#                             by holding points along a line interpolated from 
#                             points for missile line from two points.
##  Columns:                  INT missile_id, Geometry 4326 Point intersects, 
##                            INT time_code, text missile_type.  Also
##                            has a serial key.
# active_missile_pings:       Keeps track of missile pings for missiles which
#                             have already had their response decided and 
#                             solved.
##  Columns:                  INT missile_id, Geometry 4326 Point intersects, 
##                            INT time_code, text missile_type.  Also
##                            has a serial key.
# missile_inventory:          Holds all missile types along with their 
#                             remaining quantity.
##  Columns:                  text missile_name, INT missile_count Also
##                            has a serial key.
# missile_inventory:          Holds all missile types along with their 
#                             remaining quantity.
##  Columns:                  text missile_name, INT missile_count Also
##                            has a serial key.
# attacker_addresses:         Holds attacker network information allowsing
#                             for persistent storage across simulations.
##  Columns:                  text attack_address. Also
##                            has a serial key.
##############################################################################

### These all would be better not as globals
# Will hold all tablenames
tableDict = \
    {\
        "" : "", \
        "" : ""
    }

# Load up from JSON or central server
# Stores information necessary to reach the web address of other APIs.
attackerIPs = []
defenderIPs = []

# Load up from JSON, central server, or web URL
# Stores information necessary to reach the web address of the central 
# simulation manager.
athenaIP = None

# Keeps track of what the simulation timestamp will be.
simulationTime = 0
simulationDone = False

# Keeps track of whether this is running as defender, attacker, or athena
# as well as general team information
simulationMode = "defender"
teamID = None
cid = None
gid = None
teamname = None

# Strategy configuration variables
# Determines if missiles that are targetting another region will be
# intercepted by defender.
altruist = False
# Determines whether missiles should be shot later when closest, or 
# as early as possible. Safety margin defines
# how many seconds to leave as a buffer if not shooting earliest.
shootEarliest = False
safetyMargin = 3
# Determines how many seconds to plan in advance
predictionCap = 1000

# Simulation internal logic configuration variables
# Simulation conversion in meters
simCatSpeedConversion = 500
simCatRadiusConversion = 100
# Simulation conversion in lat/long approximations
simCatSpeedConversionGeom = 500
simCatRadiusConversionGeom = 100

# Manages simulation program logic such as debugging
# Lower levels print less information to console.
# 0 prints little to console
# 1 prints most failures to console
# 2 prints some successes to console
simulationDebugLevel = 2

confPath = "/home/P04A/P04A/.config.json"


class DatabaseCursor(object):

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
            + self.conn_config["dbhost"]
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
### This API is designed to simulate the defender side
### of a missile defense system.
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



##############################################################################
#                          API Specific Routes
##############################################################################


@app.get("/attackerClockRequest")
def attackerClockRequest():
    """
    attackerClockRequest
    Sends a request to attacker for the current simulation time.
    Ex. 
     http://localhost:8081/attackerClockRequest
    """
    # Return current time if attacker
    if(simulationMode == "attacker"):
        return {"time": convertTimeFromSecondsNoDate(simulationTime)}
    # Defender instead requests time from first attacker
    url = "http://" + attackerIPs[0] + "/GET_CLOCK"
    tempTime = json.loads(requests.get(url).content)
    return convertTimeToSecondsSimple(tempTime['time'])


def metersToDegreesNA(inMeters):
    """
    metersToDegreesNA
    Converts meters into the approximate 
    degree for North America.
    Uses 1 Degree of Separation =  111,139 meters.
    Warning: Not at all suitable near the poles.
    """
    return float(inMeters)/111139.0


def degreesToMetersNA(inDegrees):
    """
    degreesToMetersNA
    Converts meters into the approximate 
    degree for North America.
    Uses 1 Degree of Separation =  111,139 meters.
    Warning: Not at all suitable near the poles.
    """
    return float(inDegrees)*111139.0


def convertSpeedMetersToDegree(inString):
    """
    convertSpeedMetersToDegree
    Converts the speed category (from one to nine)
    up into the equivalent speed in meters. Then,
    it uses an approximation to convert that
    roughly into the degrees. Finally, returns
    it as a string.
    Uses 1 Degree of Separation =  111,139 meters.
    Warning: Not at all suitable near the poles.
    """
    # TODO this is inefficient and ugly
    if str(int(inString)) == "1":
        return str(metersToDegreesNA(24975))
    elif str(int(inString)) == "2":
        return str(metersToDegreesNA(27750))
    elif str(int(inString)) == "3":
        return str(metersToDegreesNA(33300))
    elif str(int(inString)) == "4":
        return str(metersToDegreesNA(36075))
    elif str(int(inString)) == "5":
        return str(metersToDegreesNA(38850))
    elif str(int(inString)) == "6":
        return str(metersToDegreesNA(41625))
    elif str(int(inString)) == "7":
        return str(metersToDegreesNA(44400))
    elif str(int(inString)) == "8":
        return str(metersToDegreesNA(47175))
    else:
        return str(metersToDegreesNA(49950))


@app.get("/RADAR_SWEEP")
def radar_sweep():
    """
    radar_sweep
    Sends a request to attackers for this region and timestamp's missile locations
    Ex. 
     http://localhost:8081/RADAR_SWEEP
    """
    if(simulationDebugLevel > 1):
        print("Team ID: ")
        print(teamID)

    shootBuffer = "0"
    if(not shootEarliest):
        shootBuffer = safetyMargin
        shootOrder = "DESC"
    else:
        shootBuffer = "0"
        shootOrder = "ASC"

    # Carry out SQL queries in database.
    try:
        # Iterate through attackers
        for index in range(0, len(attackerIPs)):
            radarTuple = ('N/A')
            try:
                # Select attackers to query
                url = "http://" + attackerIPs[index] + "/RADAR_SWEEP"
                radarTuple =  json.loads(requests.get(url).content)
            except:
                if(simulationDebugLevel > 0):
                    print("Error contacting attacker server for radar sweep.")
                return "Error contacting attacker server for radar sweep."

            # Make sure the radar sweep isn't empty
            if('N/A' in radarTuple):
                break


            # Iterate through all elements of the returned tuple and process them.
            for inIndex in range(0, len(radarTuple['features'])):

                with DatabaseCursor(confPath) as cur:
                    # Check if this missile was solved
                    missilesInSolved = 0
                    sql = \
                        f"""
                            SELECT COUNT(missile_id) FROM solved_missile_pings WHERE missile_id = {str(radarTuple['features'][inIndex]['id'])};
                        """
                    cur.execute(sql)
                    missilesInSolved = int(cur.fetchone()[0])

                    # Just ignore and update solved if this missile is already solved. Either it can't be stopped,
                    # it's not a threat, or an interception is already launched.
                    if (missilesInSolved > 0):
                        sql = \
                            f"""
                                INSERT INTO solved_missile_pings (intersects, time_code, missile_type, missile_id) VALUES 
                                    (ST_SetSRID(ST_MakePoint({str(radarTuple['features'][inIndex]['geometry']['coordinates'][0])}, {str(radarTuple['features'][inIndex]['geometry']['coordinates'][1])}, {str(metersToDegreesNA(radarTuple['features'][inIndex]['properties']['altitude']))}), 4326), 
                                    {str(convertTimeToSecondsSimple(radarTuple['features'][inIndex]['properties']['current_time']))}, '{str(radarTuple['features'][inIndex]['properties']['missile_type'])}', {str(radarTuple['features'][inIndex]['id'])});
                            """
                        cur.execute(sql)
                    else:
                        # Check if this missile can now be solved
                        missilesInActive = 0
                        sql = \
                            f"""
                                SELECT COUNT(missile_id) FROM active_missile_pings WHERE missile_id = {str(radarTuple['features'][inIndex]['id'])};
                            """
                        cur.execute(sql)
                        missilesInActive = int(cur.fetchone()[0])

                        # Check if this missile can now be solved
                        if(missilesInActive > 0):
                            if(simulationDebugLevel > 1):
                                print("Beginning an interception planning")
                            # Grab info on current location
                            sql = \
                                f"""
                                    SELECT ST_X(intersects), ST_Y(intersects), ST_Z(intersects), time_code, missile_type, missile_id from active_missile_pings;
                                """
                            cur.execute(sql)
                            previousMissileSpot = cur.fetchone()
                                
                            # Grab info on current missile type
                            sql = \
                                f"""
                                    SELECT (radius_category * {str(metersToDegreesNA(simCatRadiusConversion))}) FROM missile_spec_key WHERE classification_label = '{str(previousMissileSpot[4])}';
                                """
                            cur.execute(sql)
                            previousMissileType = cur.fetchone()[0]
                            # Calculate missile velocity vectors
                            timeDifference = (float(convertTimeToSecondsSimple(radarTuple['features'][inIndex]['properties']['current_time'])) - float(previousMissileSpot[3]))
                            xSpeed = (float(radarTuple['features'][inIndex]['geometry']['coordinates'][0]) - float(previousMissileSpot[0])) / timeDifference
                            ySpeed = (float(radarTuple['features'][inIndex]['geometry']['coordinates'][1]) - float(previousMissileSpot[1])) / timeDifference
                            zSpeed = (metersToDegreesNA(radarTuple['features'][inIndex]['properties']['altitude']) - float(previousMissileSpot[2])) / timeDifference

                            # Collect interception inventory
                            sql = \
                                f"""
                                    SELECT missile_name FROM missile_inventory WHERE missile_count > 0 ORDER BY missile_count DESC;
                                """
                            cur.execute(sql)
                            interceptionMissileTypes = cur.fetchall()

                            # Interpolate points in advance one second at a time.
                            sql = \
                                f"""
                                    DROP TABLE trajectory_prediction;
                                    CREATE TABLE trajectory_prediction (id SERIAL PRIMARY KEY, intersects geometry, time_code INT, missile_type TEXT, missile_id INT); 
                                    DO $$
                                        DECLARE count INTEGER := 1;
                                        DECLARE prediction_cap FLOAT := {str(predictionCap)};
                                        DECLARE geo_x FLOAT := {str(radarTuple['features'][inIndex]['geometry']['coordinates'][0])};
                                        DECLARE geo_y FLOAT := {str(radarTuple['features'][inIndex]['geometry']['coordinates'][1])};
                                        DECLARE geo_z FLOAT := {str(metersToDegreesNA(radarTuple['features'][inIndex]['properties']['altitude']))};
                                        DECLARE delta_x FLOAT := {str(xSpeed)};
                                        DECLARE delta_y FLOAT := {str(ySpeed)};
                                        DECLARE delta_z FLOAT := {str(zSpeed)};
                                    BEGIN
                                    WHILE (count < prediction_cap) LOOP
                                            INSERT INTO trajectory_prediction (intersects, time_code, missile_type, missile_id) VALUES 
                                                (ST_SetSRID(ST_MakePoint(geo_x + (delta_x * count), geo_y + (delta_y * count), geo_z + (delta_z * count)), 4326), 
                                                {str(simulationTime)} + count, '{str(radarTuple['features'][inIndex]['properties']['missile_type'])}', {str(radarTuple['features'][inIndex]['id'])});
                                            count := count + 1;
                                    END LOOP;
                                    END$$;

                                    /* Insert indices last to not slow point creation by rebuilding. */
                                    CREATE INDEX trajectory_index
                                    ON trajectory_prediction 
                                    USING gist(intersects);
                                """
                            cur.execute(sql)

                            # Ignore missile if it won't intersect a city.
                            # Only if not altruist
                            intersectsCharge = 1
                            sql = \
                                f"""
                                    SELECT count(ST_Intersects(ST_Buffer(points_of_interest.point_geometry, {str(metersToDegreesNA(simCatRadiusConversion))} * (SELECT radius_category FROM missile_spec_key WHERE missile_spec_key.classification_label = '{str(radarTuple['features'][inIndex]['properties']['missile_type'])}')), trajectory_prediction.intersects))
                                        FROM 
                                            points_of_interest, trajectory_prediction
                                        WHERE
                                            point_category != 'Battery';
                                """
                            cur.execute(sql)

                            intersectsCharge = cur.fetchone()[0]
                            if(altruist == False and intersectsCharge == 0):
                                if(simulationDebugLevel > 1):
                                    print("Ignoring a low threat hostile missile.")
                                sql = \
                                    f"""
                                        INSERT INTO solved_missile_pings (intersects, time_code, missile_type, missile_id) VALUES 
                                            (ST_SetSRID(ST_MakePoint({str(radarTuple['features'][inIndex]['geometry']['coordinates'][0])}, {str(radarTuple['features'][inIndex]['geometry']['coordinates'][1])}, {str(metersToDegreesNA(radarTuple['features'][inIndex]['properties']['altitude']))}), 4326), 
                                            {str(simulationTime)}, '{str(radarTuple['features'][inIndex]['properties']['missile_type'])}', {str(radarTuple['features'][inIndex]['id'])});
                                        DELETE FROM active_missile_pings WHERE missile_id = {str(radarTuple['features'][inIndex]['id'])}
                                    """
                                cur.execute(sql)
                                break

                            for interIndex in range(0, len(interceptionMissileTypes)):
                                interceptSpeed = 0
                                interceptRadius = 0
                                # Collect interception inventory
                                sql = \
                                    f"""
                                        SELECT speed_category, radius_category * {str(metersToDegreesNA(simCatRadiusConversion))} FROM missile_spec_key WHERE classification_label = '{str(interceptionMissileTypes[interIndex][0])}';
                                    """
                                cur.execute(sql)
                                interceptionMissileSpec = cur.fetchone()
                                interceptSpeed = convertSpeedMetersToDegree(interceptionMissileSpec[0])
                                interceptRadius = interceptionMissileSpec[1]

                                if(simulationDebugLevel > 1):
                                    print("Queried possible missile specs.")

                                ##############
                                # Calculate intersects
                                # Returns row in this order (Final Long, Final Lat, Final Alt, Launch Time, Explosion Time, targeted missile id)
                                sql = \
                                    f"""
                                        SELECT ST_X(trajectory_prediction.intersects), ST_Y(trajectory_prediction.intersects),ST_Z(trajectory_prediction.intersects), 
                                            trajectory_prediction.time_code - (ST_3DDistance(
                                                (SELECT point_geometry FROM points_of_interest WHERE point_category = 'Battery' ORDER BY ST_3DDistance(point_geometry, trajectory_prediction.intersects) ASC LIMIT 1), trajectory_prediction.intersects) /  {str(interceptSpeed)}),
											trajectory_prediction.time_code, trajectory_prediction.missile_id
                                        FROM trajectory_prediction 
										WHERE 
                                            /* Ensure missile is above ground */
                                            ST_Z(trajectory_prediction.intersects) >= 0
                                            AND
                                            /* Ensure missile wouldn't have passed by this time. */
                                            (trajectory_prediction.time_code - {str(simulationTime)} - {str(shootBuffer)}) >= 
                                            (ST_3DDistance(
                                                (SELECT point_geometry FROM points_of_interest WHERE point_category = 'Battery' ORDER BY ST_3DDistance(point_geometry, trajectory_prediction.intersects) ASC LIMIT 1), 
                                                    trajectory_prediction.intersects) 
                                                / {str(interceptSpeed)})
                                        ORDER BY time_code {shootOrder} LIMIT 1;
                                    """
                                cur.execute(sql)
                                missileCoordinate = cur.fetchone()

                                # Send this missile if it will work, missiles are checked in preference to send, preferring high quantity first
                                if(missileCoordinate != None):
                                    # Returns row in this order (Initial intercept Long, Initial intercept Lat)
                                    sql = \
                                        f"""
                                            SELECT ST_X(points_of_interest.point_geometry), ST_Y(points_of_interest.point_geometry)
                                            FROM points_of_interest 
                                            WHERE 
                                                /* Ensure missile is above ground */
                                                points_of_interest.point_category = 'Battery'
                                                ORDER BY ST_3DDistance(points_of_interest.point_geometry, ST_SetSRID(ST_MakePoint({str(missileCoordinate[0])}, {str(missileCoordinate[1])}, {str(missileCoordinate[2])}), 4326)) ASC LIMIT 1;
                                        """
                                    cur.execute(sql)
                                    interceptBaseCoordinate = cur.fetchone()

                                    if(simulationDebugLevel > 1):
                                        print("Attempting to fire a missile.")

                                    startDate = convertDateToOtherDate(convertTimeFromSeconds(missileCoordinate[3]))
                                    endDate = convertDateToOtherDate(convertTimeFromSeconds(missileCoordinate[4]))

                                    ##############
                                    # Send missile launch to attacker
                                    # USE THE fire solution route
                                    # Create URL, header, and json payload
                                    url = "http://" + attackerIPs[index] + "/FIRE_SOLUTION"
                                    payload = json.dumps({
                                    "team_id": int(teamID), 
                                    "target_missile_id": int(missileCoordinate[5]),
                                    "missile_type": str(interceptionMissileTypes[interIndex][0]),
                                    "firedfrom_lon": float(interceptBaseCoordinate[0]),
                                    "firedfrom_lat": float(interceptBaseCoordinate[1]),
                                    "fired_time": str(startDate),
                                    "aim_lat": float(missileCoordinate[1]),
                                    "aim_lon": float(missileCoordinate[0]),
                                    "expected_hit_time": str(endDate),
                                    "target_alt": float(degreesToMetersNA(missileCoordinate[2]))
                                    })

                                    headers = {
                                    'Content-Type': 'application/json'
                                    }
                                    print(payload)

                                    # Send request
                                    response = requests.request("POST", url, headers=headers, data=payload).content


                                    if(simulationDebugLevel > 1):
                                        print("Missile notification sent to attacker.")
                                        print(response)

                                    # Move missile into logs
                                    sql = \
                                        f"""
                                            INSERT INTO logged_intercepts (intersects, time_code, missile_type, missile_id) VALUES 
                                                (ST_SetSRID(ST_MakePoint({str(missileCoordinate[0])}, {str(missileCoordinate[1])}, {str(missileCoordinate[2])}), 4326), 
                                                {str(missileCoordinate[4])}, '{str(interceptionMissileTypes[interIndex][0])}', {str(missileCoordinate[5])});
                                        """
                                    cur.execute(sql)
                                    if(simulationDebugLevel > 1):
                                       print("Logged intersection")


                                    ##############
                                    # Decrement relevant missile inventory and break loop.
                                    sql = \
                                        f"""
                                            UPDATE missile_inventory SET missile_count = missile_count - 1 WHERE missile_name = '{str(interceptionMissileTypes[interIndex][0])}';
                                        """
                                    cur.execute(sql)
                                    interIndex = len(interceptionMissileTypes) + 1
                                    break

                            # Move missile into solved and delete old records from active missile database.
                            sql = \
                                f"""
                                    INSERT INTO solved_missile_pings (intersects, time_code, missile_type, missile_id) VALUES 
                                        (ST_SetSRID(ST_MakePoint({str(radarTuple['features'][inIndex]['geometry']['coordinates'][0])}, {str(radarTuple['features'][inIndex]['geometry']['coordinates'][1])}, {str(metersToDegreesNA(radarTuple['features'][inIndex]['properties']['altitude']))}), 4326), 
                                        {str(convertTimeToSecondsSimple(radarTuple['features'][inIndex]['properties']['current_time']))}, '{str(radarTuple['features'][inIndex]['properties']['missile_type'])}', {str(radarTuple['features'][inIndex]['id'])});
                                    DELETE FROM active_missile_pings WHERE missile_id = {str(radarTuple['features'][inIndex]['id'])}
                                """
                            cur.execute(sql)
                            
                        else:
                            # Nothing more can be done yet but record this missile as active.
                            sql = \
                                f"""
                                    INSERT INTO active_missile_pings (intersects, time_code, missile_type, missile_id) VALUES 
                                        (ST_SetSRID(ST_MakePoint({str(radarTuple['features'][inIndex]['geometry']['coordinates'][0])}, {str(radarTuple['features'][inIndex]['geometry']['coordinates'][1])}, {str(metersToDegreesNA(radarTuple['features'][inIndex]['properties']['altitude']))}), 4326), 
                                        {str(convertTimeToSecondsSimple(radarTuple['features'][inIndex]['properties']['current_time']))}, '{str(radarTuple['features'][inIndex]['properties']['missile_type'])}', {str(radarTuple['features'][inIndex]['id'])});
                                """
                            cur.execute(sql)

            # Execute final constructed statement to add to database.
            #cur.execute(sql)
            if(simulationDebugLevel > 1):
                print("Radar sweep processed")
            return "Radar sweep processed."
    except:
        if(simulationDebugLevel > 0):
            print("Error in generating reponse to radar sweep.")
        return ("Host database configuration error, connection error, or invalid column field.")



@app.get("/defenderSimulationDoneCheck")
def defenderSimulationDoneCheck():
    """
    defenderSimulationDoneCheck
    Checks if there are remaining missiles to defend the region.
    Returns False if so, otherwise returns True to recommend ending
    the simulation.
     http://localhost:8081/defenderSimulationDoneCheck
    """ 
    try:
        with DatabaseCursor(confPath) as cur:
            # Check if at least one missile remains.
            sql = \
            f"""
                SELECT SUM(missile_count) from missile_inventory;
            """

            cur.execute(sql)
            if (int(cur.fetchone()[0]) > 0):
                # Missiles remain, no other issues
                return False
            else:
                # Missiles are empty, surrender
                return True

    except:
        return True
        print ("Host database configuration error or invalid column field. Ending simulation.")


@app.get("/simulationControlLoop")
async def simulationControlLoop():
    """
    simulationControlLoop
    Repeats simulation control loop until athena says end simulation
    Example syntax: 
     http://localhost:8081/simulationControlLoop
    """
    # Send attackers the simulation begin signal.
    if(simulationDebugLevel > 1):
        print("Beginning simulation session.")
    for index in range(0, len(attackerIPs)):
        url = "http://" + attackerIPs[index] + "/START/" + str(teamID)
        requests.get(url)

    while (defenderSimulationDoneCheck() == False):
        # Grab updated time
        global simulationTime
        #simulationTime = attackerClockRequest()
        simulationTime = convertTimeToSeconds(str(datetime.datetime.now()))
        if(simulationDebugLevel > 1):
            print(simulationTime)

        # Iterate through attackers to process radar sweeps
        for index in range(0, len(attackerIPs)):
            radar_sweep()
            pass

        # Sleep one second
        time.sleep(1)

    # Send attackers the simulation end signal.
    for index in range(0, len(attackerIPs)):
        url = "http://" + attackerIPs[index] + "/QUIT/" + str(teamID)
        requests.get(url)

    if(simulationDebugLevel > 1):
        print("Finished simulation session.")
    return "Finished simulation."


@app.get("/loadPersistentIPs")
def loadPersistentIPs():
    """
    loadPersistentIPs
    Queries database for persistent IPs and loads as simulation variables.
    Example syntax: 
     http://localhost:8081/loadPersistentIPs
    """
    # Carry out SQL queries in database.
    try:
        with DatabaseCursor(confPath) as cur:
            # Select persistent athena address
            sql = \
                f"""
                    SELECT current_athena_address FROM athena_address;
                """
            cur.execute(sql)
            athenaTuple = cur.fetchone()

            # Update athena address if it exists
            if(athenaTuple != None):
                athenaIP = athenaTuple[1]

            # Select persistent attacker addresses
            sql = \
                f"""
                    SELECT attack_address FROM attacker_addresses;
                """
            cur.execute(sql)
            attackerTuple = cur.fetchall()
            # Update attacker addresses if they exist
            if(len(attackerTuple) > 0):
                for index in range(0, len(attackerTuple)):
                    attackerIPs.append(attackerTuple[index][0])
                    
            # Select persistent defender addresses
            sql = \
                f"""
                    SELECT defense_address FROM defender_addresses;
                """
            cur.execute(sql)
            defenderTuple = cur.fetchall()
            # Update defender addresses if they exist
            if(len(defenderTuple) > 0):
                for index in range(0, len(defenderTuple)):
                    defenderIPs.append(defenderTuple[index][0])

            if(simulationDebugLevel > 1):
                print("Persistent simulation connection settings loaded.")
            return "Persistent simulation connection settings loaded."
    except:
        print("Error persisting connection data.")
        return ("Host database configuration error or invalid column field.")



@app.get("/getRegion?{target}")
def getRegion(target=teamname):
    """
    getRegion
    Queries attacker for region and loads geometries into database.
    This also grabs the region's arsenal.
    Example syntax: 
     http://localhost:8081/getRegion
    """
    target = str(target)

    # Carry out SQL queries in database.
    try:
        with DatabaseCursor(confPath) as cur:
            # Route if running as athena
            # Athena shouldn't get this call outside of error.
            if (simulationMode == "athena"):
                return "Invalid request. Query attackers for arsenal instead."

            # Only the defender would do everything below

            # Select persistent first attacker address to query
            url = "http://" + attackerIPs[0] + "/REGISTER"
            regionList = json.loads(requests.get(url).content)


            global cid
            global gid
            global teamID
            cid = int(regionList['region']['features'][0]['properties']['cid'])
            gid = int(regionList['region']['features'][0]['properties']['gid'])
            teamID = int(regionList['id'])

            if(simulationDebugLevel > 1):
                print("Real team id:")
                print(teamID)

            # Drop and recreate military_region and points_of_interest tables.
            sql = \
                f"""
                    DROP TABLE assigned_regions;
                    DROP TABLE points_of_interest;
                    CREATE TABLE assigned_regions (index_assigned_id SERIAL PRIMARY KEY, gid INT, cid INT, boundary GEOMETRY);
                    CREATE TABLE points_of_interest (points_index_id SERIAL PRIMARY KEY, point_id INT, point_category TEXT, point_geometry GEOMETRY (PointZ, 4326));

                    CREATE INDEX assigned_regions_index
                    ON assigned_regions 
                    USING gist(boundary);
                    
                    CREATE INDEX points_index
                    ON points_of_interest 
                    USING gist(point_geometry);

                """
            cur.execute(sql)

            # Add new assigned military region
            # Also add a single missile battery to the center, and three others at random points
            # The geojson needs to have its ' changed into " to be compatible with postgis geojson format
            rawRegionString = str(regionList['region']['features'][0]['geometry']).replace('\'', '"')
            sql = \
                f"""
                    INSERT INTO assigned_regions (gid, cid, boundary) VALUES ({str(gid)}, {str(cid)}, (SELECT ST_GeomFromGeoJSON('
                        {rawRegionString}
                        '))); 

                    INSERT INTO points_of_interest (point_id, point_category, point_geometry) VALUES (-1, 'Battery',
                            ST_SetSRID(ST_MakePoint(ST_X(ST_Centroid((SELECT boundary from assigned_regions LIMIT 1))), ST_Y(ST_Centroid((SELECT boundary from assigned_regions LIMIT 1))), 0), 4326));

                    WITH "temp_point" AS (SELECT ST_GeometryN(ST_GeneratePoints((SELECT boundary FROM assigned_regions LIMIT 1), 1), 1))
                    INSERT INTO points_of_interest (point_id, point_category, point_geometry) VALUES (-2, 'Battery',
                            ST_SetSRID(ST_MakePoint(ST_X((SELECT * FROM temp_point)), ST_Y((SELECT * FROM temp_point)), 0), 4326));

                    WITH "temp_point" AS (SELECT ST_GeometryN(ST_GeneratePoints((SELECT boundary FROM assigned_regions LIMIT 1), 1), 1))
                    INSERT INTO points_of_interest (point_id, point_category, point_geometry) VALUES (-3, 'Battery',
                            ST_SetSRID(ST_MakePoint(ST_X((SELECT * FROM temp_point)), ST_Y((SELECT * FROM temp_point)), 0), 4326));

                    WITH "temp_point" AS (SELECT ST_GeometryN(ST_GeneratePoints((SELECT boundary FROM assigned_regions LIMIT 1), 1), 1))
                    INSERT INTO points_of_interest (point_id, point_category, point_geometry) VALUES (-4, 'Battery',
                            ST_SetSRID(ST_MakePoint(ST_X((SELECT * FROM temp_point)), ST_Y((SELECT * FROM temp_point)), 0), 4326));
                """


            for index in range(0, len(regionList['cities']['features'])):
                # Fix if attacker only gave a 2D point
                if (len(regionList['cities']['features'][index]['geometry']['coordinates']) < 3):
                    regionList['cities']['features'][index]['geometry']['coordinates'].append(0)
                rawPointString = str(regionList['cities']['features'][index]['geometry']).replace('\'', '"')

                # Add new point of interest
                pointType = 'Target'
                sql += \
                    f"""
                        INSERT INTO points_of_interest (point_id, point_category, point_geometry) VALUES ({str(regionList['cities']['features'][index]['properties']['id'])}, 'Target', 
                        (SELECT ST_SetSRID(
                            ST_GeomFromGeoJSON('
                                {rawPointString}
                            '),
                            4326)));
                    """
            with open('debugdump.txt', 'w') as f:
                f.write(sql)

            cur.execute(sql)

            # Drop and recreate missile inventory table
            sql = \
                f"""
                DROP TABLE missile_inventory;
                CREATE TABLE missile_inventory(missile_inventory_index SERIAL PRIMARY KEY, missile_name TEXT, missile_count INT); 
                """
            # Insert each missile type and count.
            for key in regionList['arsenal']:
                if (key != "total"):
                    sql += \
                        f"""
                        INSERT INTO missile_inventory (missile_name, missile_count) VALUES ('{str(key)}', {str(regionList['arsenal'][key])}); 
                        """

            # Execute final constructed statement to add to database.
            cur.execute(sql)

            return "Assigned region loaded."
    except:
        if(simulationDebugLevel > 0):
            print("Get region function failure.")
        return ("Host database configuration error, connection error, or invalid column field.")


@app.get("/initializeSimulation")
async def initializeSimulation():
    """
    initializeSimulation
    Performs work to load simulation initial values.
    Example syntax: 
     http://localhost:8081/initializeSimulation
    """
    # Load persistent connection settings from database
    if(loadPersistentIPs() == "Host database configuration error, connection error, or invalid column field."):
        if(simulationDebugLevel > 0):
            print("Error loading persistent connection settings.")
        return "Error loading persistent connection settings."

    # Send athena request to load time
    global simulationTime
    simulationTime = 0

    # Send attacker bases request
    if(getRegion(teamname) == "Host database configuration error, connection error, or invalid column field."):
        if(simulationDebugLevel > 0):
            print("Error obtaining base setup information.")
        return "Error obtaining base setup information."

    # Reset all necessary databases
    try:
        with DatabaseCursor(confPath) as cur:
            # Construct proper SQL query statement
            # Drop and recreate existing tables
            sql = \
                f"""
                    DROP TABLE active_missile_pings;
                    CREATE TABLE active_missile_pings (id SERIAL PRIMARY KEY, intersects geometry, time_code INT, missile_type TEXT, missile_id INT); 

                    CREATE INDEX active_index
                    ON active_missile_pings 
                    USING gist(intersects);

                    DROP TABLE solved_missile_pings;
                    CREATE TABLE solved_missile_pings (id SERIAL PRIMARY KEY, intersects geometry, time_code INT, missile_type TEXT, missile_id INT); 
                    
                    CREATE INDEX solved_index
                    ON solved_missile_pings 
                    USING gist(intersects);
                """

            cur.execute(sql)
            return "Simulation databases reset. Simulation ready."
    except:
        if(simulationDebugLevel > 0):
            print("Host database configuration error or invalid column field.")
        return ("Host database configuration error or invalid column field.")

    # Begin simulation control loop manually with simulationControlLoop route



@app.get("/addAttackerIP/{target}")
async def addAttackerIP(target):
    """
    addAttackerIP
    Adds IP to attacker list for simulation.
    Example syntax: 
     http://localhost:8081/addAttackerIP/0.0.0.0:8012
    """
    # Ensure proper format
    target = str(target)
    # Add to list
    attackerIPs.append(target)


@app.get("/clearAttackerIPs")
async def clearAttackerIPs():
    """
    clearAttackerIPs
    Removes IPs from attacker list for simulation.
    Example syntax: 
     http://localhost:8081/clearAttackerIPs
    """
    attackerIPs = []


@app.get("/addDefenderIP/{target}")
async def addDefenderIP(target):
    """
    addDefenderIP
    Adds IP to defender list for simulation.
    Example syntax: 
     http://localhost:8081/addDefenderIP/0.0.0.0:8012
    """
    # Ensure proper format
    target = str(target)
    # Add to list
    defenderIPs.append(target)


@app.get("/clearDefenderIPs")
async def clearDefenderIPs():
    """
    clearDefenderIPs
    Removes IPs from defender list for simulation.
    Example syntax: 
    http://localhost:8081/clearDefenderIPs
    """
    defenderIPS = []


@app.get("/addAthenaIP/{target}")
async def registerWithathena(target):
    """
    addAthenaIP
    Adds IP to athena variable for simulation.
    Example syntax: 
     http://localhost:8081/addAthenaIP/0.0.0.0:8012
    """
    # Ensure proper format
    target = str(target)
    # Add to list
    athenaIP = target


@app.get("/persistCurrentIPs")
async def persistCurrentIPs():
    """
    persistCurrentIPs
    Saves currently loaded IPs into the persistent session IP database.
    Example syntax: 
     http://localhost:8081/persistCurrentIPs
    """

    # Carry out SQL queries in database.
    try:
        with DatabaseCursor(confPath) as cur:
            # Construct proper SQL query statement
            # Drop and recreate existing tables
            sql = \
                f"""
                    DROP TABLE attacker_addresses;
                    DROP TABLE defender_addresses;
                    DROP TABLE athena_address;
                    CREATE TABLE attacker_addresses(attacker_index SERIAL PRIMARY KEY, attack_address TEXT);
                    CREATE TABLE defender_addresses(defender_index SERIAL PRIMARY KEY, defense_address TEXT);
                    CREATE TABLE athena_address(athena_index SERIAL PRIMARY KEY, current_athena_address TEXT);
                """

            # Work out insertion string for athena
            athenaClause = \
                f"""
                    INSERT INTO athena_address (current_athena_address) VALUES ('{athenaIP}'); 
                """

            # Work out insertion string for attackers
            attackerClause = f""""""
            for index in range(0, len(attackerIPs)):
                attackerClause += \
                    f"""
                        INSERT INTO attacker_addresses (attack_address) VALUES ('{attackerIPs[index]}'); 
                    """

            # Work out insertion string for defenders
            defenderClause = f""""""
            for index in range(0, len(defenderIPs)):
                defenderClause += \
                    f"""
                        INSERT INTO defender_addresses (defense_address) VALUES ('{defenderIPs[index]}'); 
                    """

            # Combine query into one string
            sql = sql + athenaClause + attackerClause + defenderClause
            cur.execute(sql)

            return "Current simulation IP and Port configurations saved."
    except:
        if(simulationDebugLevel > 0):
            print("Host database configuration error or invalid column field")
        return ("Host database configuration error or invalid column field.")


@app.get("/createTables")
async def createTables():
    """
    createTables
    Creates tables for the first time. If tables already existing keeps this from
    running, simply run the destroyTables route, ignore the error, and retry this.
    Example syntax: 
     http://localhost:8081/createTables
    """
    try:
        with DatabaseCursor(confPath) as cur:
            sql = \
            f"""
                    CREATE SCHEMA IF NOT EXISTS public;
            """
            cur.execute(sql)
            if(simulationDebugLevel > 1):
                print("Succeeded in contacting database.")
    except:
        if(simulationDebugLevel > 0):
            print("Failed to contact database.")
    # Carry out SQL queries in database.
    try:
        # Load schemas and extensions
        with DatabaseCursor(confPath) as cur:
            sql = \
                f"""
                CREATE EXTENSION IF NOT EXISTS postgis_sfcgal WITH SCHEMA public CASCADE;
                CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public CASCADE;
                CREATE EXTENSION IF NOT EXISTS postgis_sfcgal WITH SCHEMA public CASCADE;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Construct proper SQL query statement
            # Create without dropping necessary tables
            # Create attacker addresses table
            # missileCommand.live:8080 is included as a default argument here. It can always
            # be dropped by the route to destroy attacker addresses if this isn't desired.
            sql = \
                f"""
                    CREATE TABLE attacker_addresses(attacker_index SERIAL PRIMARY KEY, attack_address TEXT);
                    INSERT INTO attacker_addresses (attack_address) VALUES ('missilecommand.live:8080'); 
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create defender addresses table
            sql = \
                f"""
                    CREATE TABLE defender_addresses(defender_index SERIAL PRIMARY KEY, defense_address TEXT);
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create athena address table
            sql = \
                f"""
                    CREATE TABLE athena_address(athena_index SERIAL PRIMARY KEY, current_athena_address TEXT);
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create trajectory prediction scratch table
            sql =\
                f"""
                    CREATE TABLE trajectory_prediction (id SERIAL PRIMARY KEY, intersects geometry, time_code INT, missile_type TEXT, missile_id INT); 

                    CREATE INDEX trajectory_index
                    ON trajectory_prediction 
                    USING gist(intersects);
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create assigned regions table
            sql =\
                f"""
                    CREATE TABLE assigned_regions (index_assigned_id SERIAL PRIMARY KEY, gid INT, cid INT, boundary GEOMETRY);

                    CREATE INDEX assigned_regions_index
                    ON assigned_regions 
                    USING gist(boundary);
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create points of interest table
            sql =\
                f"""
                    CREATE TABLE points_of_interest (points_index_id SERIAL PRIMARY KEY, point_id INT, point_category TEXT, point_geometry GEOMETRY (PointZ, 4326));

                    CREATE INDEX points_index
                    ON points_of_interest 
                    USING gist(point_geometry);
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create missile specifications table
            # Note, this is probably too hardcoded, but there's not a system to share specs between attackers and defenders.
            sql =\
                f"""
                    CREATE TABLE missile_spec_key (
                        classification_id SERIAL PRIMARY KEY, 
                        classification_label text,
                        speed_category integer,
                        radius_category integer
                        );

                    INSERT INTO missile_spec_key (classification_id, classification_label, speed_category, radius_category) VALUES (1, 'Atlas', 1, 7);
                    INSERT INTO missile_spec_key (classification_id, classification_label, speed_category, radius_category) VALUES (2, 'Harpoon', 2, 8);
                    INSERT INTO missile_spec_key (classification_id, classification_label, speed_category, radius_category) VALUES (3, 'Hellfire', 3, 7);
                    INSERT INTO missile_spec_key (classification_id, classification_label, speed_category, radius_category) VALUES (4, 'Javelin', 4, 7);
                    INSERT INTO missile_spec_key (classification_id, classification_label, speed_category, radius_category) VALUES (5, 'Minuteman', 5, 9);
                    INSERT INTO missile_spec_key (classification_id, classification_label, speed_category, radius_category) VALUES (6, 'Patriot', 6, 6);
                    INSERT INTO missile_spec_key (classification_id, classification_label, speed_category, radius_category) VALUES (7, 'Peacekeeper', 7, 6);
                    INSERT INTO missile_spec_key (classification_id, classification_label, speed_category, radius_category) VALUES (8, 'SeaSparrow', 8, 5);
                    INSERT INTO missile_spec_key (classification_id, classification_label, speed_category, radius_category) VALUES (9, 'Titan', 8, 5);
                    INSERT INTO missile_spec_key (classification_id, classification_label, speed_category, radius_category) VALUES (10, 'Tomahawk', 9, 6);
                    INSERT INTO missile_spec_key (classification_id, classification_label, speed_category, radius_category) VALUES (11, 'Trident', 9, 9);
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create missile inventory table
            sql =\
                f"""
                    CREATE TABLE missile_inventory(missile_inventory_index SERIAL PRIMARY KEY, missile_name TEXT, missile_count INT); 
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create active missile pings table
            sql =\
                f"""
                    CREATE TABLE active_missile_pings (id SERIAL PRIMARY KEY, intersects geometry, time_code INT, missile_type TEXT, missile_id INT); 

                    CREATE INDEX active_index
                    ON active_missile_pings 
                    USING gist(intersects);
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create solved missile pings table
            sql =\
                f"""
                    CREATE TABLE solved_missile_pings (id SERIAL PRIMARY KEY, intersects geometry, time_code INT, missile_type TEXT, missile_id INT); 

                    CREATE INDEX solved_index
                    ON solved_missile_pings 
                    USING gist(intersects);
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create solved missile pings table
            sql =\
                f"""
                    CREATE TABLE logged_intercepts (id SERIAL PRIMARY KEY, intersects geometry, time_code INT, missile_type TEXT, missile_id INT); 

                    CREATE INDEX logged_index
                    ON logged_intercepts 
                    USING gist(intersects);
                """
            cur.execute(sql)

        return "Necessary missing tables created."
    except:
        if(simulationDebugLevel > 0):
            print("Host database configuration error or at least one table already exists.")
        return ("Host database configuration error or at least one table already exists.")


@app.get("/destroyTables")
async def destroyTables():
    """
    destroyTables
    Destroys all necessary tables for the simulation.
    Warning: This does exactly what it says. Usually this
    shouldn't be necessary, and the only effect is erasing
    all attacker and defender persistent address tables.
    Doing this during an active simulation will obviously
    break it.
    Example syntax: 
     http://localhost:8081/destroyTables
    """

    # Carry out SQL queries in database.
    try:
        with DatabaseCursor(confPath) as cur:
            # Construct proper SQL query statement
            # Destroy without recreating necessary tables
            # Destroy attacker addresses table
            sql = \
                f"""
                    DROP TABLE attacker_addresses;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy defender addresses table
            sql = \
                f"""
                    DROP TABLE defender_addresses;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy athena address table
            sql = \
                f"""
                    DROP TABLE athena_address;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy trajectory prediction scratch table
            sql =\
                f"""
                    DROP TABLE trajectory_prediction;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy assigned regions table
            sql =\
                f"""
                    DROP TABLE assigned_regions;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy points of interest table
            sql =\
                f"""
                    DROP TABLE points_of_interest;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy missile specifications table
            sql =\
                f"""
                    DROP TABLE public.missile_spec_key;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy missile inventory table
            sql =\
                f"""
                    DROP TABLE missile_inventory; 
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy active missile pings table
            sql =\
                f"""
                    DROP TABLE active_missile_pings;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy solved missile pings table
            sql =\
                f"""
                    DROP TABLE solved_missile_pings;
                """
            cur.execute(sql)        
        with DatabaseCursor(confPath) as cur:
            sql = \
                f"""
                    DROP TABLE logged_intercepts;
                """
            cur.execute(sql)

        return "Necessary missing tables destroyed."
    except:
        if(simulationDebugLevel > 0):
            print("Host database configuration error or missing table.")
        return ("Host database configuration error or missing table.")


@app.get("/tableMaintenance")
async def tableMaintenance():
    """
    tableMaintenance
    Manually schedules a VACUUM ANALYZE on all tables.
    Probably not too useful considering that most data
    used by the simulation is created in real time, but
    it may at least fix any rare issues or help attacker
    and defender persistent address tables.
    Example syntax: 
     http://localhost:8081/tableMaintenance
    """

    # Carry out SQL queries in database.
    try:
        with DatabaseCursor(confPath) as cur:
            # Construct proper SQL query statement
            # Vacuum and analyze all necessary tables
            # Vacuum and analyze attacker addresses table
            sql = \
                f"""
                    VACUUM ANALYZE attacker_addresses;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze defender addresses table
            sql = \
                f"""
                    VACUUM ANALYZE defender_addresses;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze athena address table
            sql = \
                f"""
                    VACUUM ANALYZE athena_address;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze trajectory prediction scratch table
            sql =\
                f"""
                    VACUUM ANALYZE trajectory_prediction;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze assigned regions table
            sql =\
                f"""
                    VACUUM ANALYZE assigned_regions;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze points of interest table
            sql =\
                f"""
                    VACUUM ANALYZE points_of_interest;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze missile specifications table
            sql =\
                f"""
                    VACUUM ANALYZE missile_spec_key;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze missile inventory table
            sql =\
                f"""
                    VACUUM ANALYZE missile_inventory; 
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze active missile pings table
            sql =\
                f"""
                    VACUUM ANALYZE active_missile_pings;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze solved missile pings table
            sql =\
                f"""
                    VACUUM ANALYZE solved_missile_pings;
                """
            cur.execute(sql)
            # Vacuum and analyze logged intercepts
        with DatabaseCursor(confPath) as cur:
            sql = \
                f"""
                    VACUUM ANALYZE logged_intercepts;
                """
            cur.execute(sql)

            return "Maintenance on tables complete."
    except:
        if (simulationDebugLevel > 0):
            print("Host database configuration error or missing table.")
        return ("Host database configuration error or missing table.")

if __name__ == "__main__":
    # Grab config info
    initializerConfigFile = confPath
    initialConfig = {}

    try:
        with open(initializerConfigFile) as config_file:
            # Load up server starting info from config file
            initialConfig = json.load(config_file)
    # Use default arguments if fail
    except:
        if(simulationDebugLevel > 0):
            print("Error reading config file. Using default values.")
        initialConfig["sitename"] = "spatialapi:app"
        initialConfig["host"] = "0.0.0.0"
        initialConfig["publicport"] = "8081"
    

    uvicorn.run(initialConfig["sitename"], host=initialConfig["host"], port=initialConfig["publicport"], log_level="debug", reload=True)

