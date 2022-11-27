#!/usr/bin/env python3
##############################################################################
# Author: Caleb Sneath
# Assignment: P04.X - Battleship API
# Date: November 27, 2022
# Python 3.9.5
# Project Version: 0.2.0
#
# Description: A simple Python database API created for educational purposes
#              to simulate a multiplayer game similar to battleship 
#              between multiple teams.
#
# Local Instructions:
# Building: Requires Python (Tested for 3.9.5), FastAPI, and psycopg2.
# To install the last two, simply run in the terminal:
# pip install fastapi
# pip install psycopg2
# Afterward, set up your basic with pgAdmin and fill out the .config.json 
# file. Adjust the line below to your install path if necessary for
# the confPath variable.
# Include the desired copy of ships.json and bbox.json as input files
# in this project's local directory.
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
#   "http://{address}/initializeSimulation". This will generate
#   the desired output file.
# - The simulation will either produce an error message or run until
#   it is finished
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
from math import radians, degrees, cos, sin, asin, sqrt, pow, atan2, pi
import random
import os
import json
import sys
import time
import datetime

# Local project module
from module import convertTimeToSecondsSimple, convertTimeFromSecondsNoDate
from module import convertTimeToSecondsNoDate, convertTimeToSeconds
from module import convertTimeFromSeconds, convertDateToOtherDate

##############################################################################
#                          Tables Descriptions
# fleet_template:             Acts a normalized storage to hold the fleet
#                             so calculations can be done to it relative
#                             to facing north at coordinate (0, 0).
#                             This is for the south east of the fleet
#                             as a whole, not every ship. Also contains
#                             additional columns to hold info on column,
#                             row, and fleet id for the ships inside.
##  Columns:                  category text, shipclass text, 
##                            displacement numeric, ship_length numeric,
##                            ship_width numeric, torpedolaunchers json,
##                            armament json, armor json, speed numeric,
##                            turn_radius numeric, ship_geom geometry,
##                            ship_col numeric, ship_row numeric,
##                            fleet_num numeric, bearing numeric
##                            such as missile batteries or target cities
# fleet:                      Holds the actual current position of ships
#                             as well as their current equipment and stats.
##  Columns:                  category text, shipclass text, 
##                            displacement numeric, ship_length numeric,
##                            ship_width numeric, torpedolaunchers json,
##                            armament json, armor json, speed numeric,
##                            turn_radius numeric, ship_geom geometry,
##                            bearing numeric
# fleet_overview:             Stores information on the fleet as a whole,
#                             irrespective of the individual ships, such
#                             as a singular point to represent the fleet
#                             (should be the bottom left corner) and
#                             a fleet identification number.
##  Columns:                  fleet_num numeric, 
##                            fleet_reference_point geometry 
# enemy_tracker:              Stores information on enemy fleets as a whole,
#                             not directly tracking individual enemy ships.
#                             Tracked information about enemy fleets includes
#                             a singular point to represent the fleet
#                             (should be the bottom left corner), 
#                             a fleet identification number, and
#                             a number which should include what radius the 
#                             fleet is within for sure should any uncertainty
#                             exist about the exact position.
##  Columns:                  fleet_num numeric, 
##                            fleet_reference_point geometry , and 
##                            certainty_radius
# ship_shapes:                Stores the ships as rotated rectangles.
##  Columns:                  ship_id numeric, ship_polygon geometry
##                            and its spatial index ship_shape_index
# bbox:                       Holds the simulation bounding box as well
#                             as additional bounding boxes to hold areas
#                             which serve as buffers for white listing
#                             and blacklisting spawn areas in the bbox.
#                             Points shouldn't spawn in the min column
#                             and points must be in the max column to spawn.
##  Columns:                  bbox geometry, bbox_min_spawn geometry,
##                            bbox_max_spawn geometry
##                            (Note: scaled 1-9),INT radius_label (also 1-9).
##                            Also has a serial key.
# attacker_addresses:         Holds attacker network information allowsing
#                             for persistent storage across simulations.
##  Columns:                  text attack_address. Also
##                            has a serial key.
##############################################################################

### These all would be better not as globals
# Will hold all tablenames
tableList = \
    [\
        "attacker_addresses", \
        "bbox",               \
        "fleet",              \
        "fleet_template",     \
        "fleet_overview",     \
        "enemy_tracker",      \
        "ship_shapes"
    ]

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
teamname = 'rocketscience'

# Manages simulation program logic such as debugging
# Lower levels print less information to console.
# 0 prints little to console
# 1 prints most failures to console
# 2 prints some successes to console
simulationDebugLevel = 2

randSeed = 1

confPath = ".config.json"


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
#                       API Specific Routes/Functions
##############################################################################

@app.get("/shipDamageCalculation/{targetShipNumber}/{inJoules}/{fireRate}")
def rotateShipGuns(targetShipNumber, inJoules, fireRate):
    """
    shipDamageCalculation
    Calculates how much damage a ship received, if any.
    Ex. 
     http://localhost:8081/shipDamageCalculation/0/20/30
    """
    try:
        with DatabaseCursor(confPath) as cur:
            # Find ship's armor values.
            sql = \
                f"""
                    SELECT armor->'hull', armor->'deck'  
                        FROM fleet WHERE ship_id = {str(targetShipNumber)};
                """
            cur.execute(sql)
            armorList = cur.fetchone()
            armorTotal = float(armorList[0]) + float(armorList[1])
            # No damage if armor is too big
            # Conversion factor determines how much of the input
            # should be offset by a single point of armor
            energyConversionFactor = 1
            if (armorTotal >= (float(inJoules) / float(energyConversionFactor))):
                return "Damage taken: 0"
        damageTaken = float(inJoules) * float(fireRate)
        return ("Damage taken: " + str(damageTaken))

    except:
        if(simulationDebugLevel > 1):
            print ("Host database configuration error or invalid inputs.")
        return "Host database configuration error or invalid inputs."

@app.get("/fleetHitDetection/{initX}/{initY}/{finalX}/{finalY}")
def fleetHitDetection(initX, initY, finalX, finalY):
    """
    fleetHitDetection
    Returns the shortest distance or first intersection of a projectile.
    """

    # What extra radius around the ship counts as a hit.
    extraHitBuffer = 10

    try:
        with DatabaseCursor(confPath) as cur:
            # Calculate if there are any intersections first
            sql = \
                f"""
                    SELECT  ST_Centroid(ST_Intersection(ST_MakeLine(ST_SetSRID(ST_MakePoint({str(initX)}, {str(initX)}), 4326), 
                                                    ST_SetSRID(ST_MakePoint({str(finalX)}, {str(finalY)}), 4326)), 
					                        ST_Buffer(ship_polygon::geography, {str(extraHitBuffer)})::geometry(Polygon, 4326)))::jsonb,
                            ship_id
                    FROM ship_shapes
                    WHERE ST_Intersects(ST_MakeLine(ST_SetSRID(ST_MakePoint({str(initX)}, {str(initX)}), 4326), 
                                                    ST_SetSRID(ST_MakePoint({str(finalX)}, {str(finalY)}), 4326)), 
					                        ST_Buffer(ship_polygon::geography, {str(extraHitBuffer)})::geometry(Polygon, 4326))
                    ORDER BY ST_Distance(ST_SetSRID(ST_MakePoint({str(initX)}, {str(initY)}), 4326), ship_polygon) LIMIT 1;
                """

            cur.execute(sql)
            intersectsFirst = cur.fetchone()

            print(intersectsFirst)

            # Returns any ship if a hit.
            if(intersectsFirst != None):
                return ("Hits ship: " + str(intersectsFirst[1]))

            # Calculates closest hit otherwise
            sql = \
                f"""
                    SELECT ST_Distance(ship_polygon::geography, ST_SetSRID(ST_MakePoint(0, 0), 4326)::geography)
                    FROM ship_shapes 
                    ORDER BY ST_Distance(ship_polygon::geography, ST_SetSRID(ST_MakePoint(0, 0), 4326)::geography) ASC
                    LIMIT 1;
                """

            cur.execute(sql)
            closestDistance = cur.fetchone()[0]

            return ("Closest distance: " + str(closestDistance))

    except:
        if(simulationDebugLevel > 1):
            print ("Host database configuration error.")
        return "Host database configuration error."

def updateShipShapes():
    """
    updateShipShapes
    Updates ship polygons so that they reflect the ship's current 
    position and dimensions. Places ships with their position
    at the bottom left of the polygon.
    """
    try:
        with DatabaseCursor(confPath) as cur:
            # Calculate new rectangles for ship geometry.
            # Ship reference points are on the bottom left corner
            sql = \
                f"""
                    UPDATE ship_shapes 
                        SET ship_polygon = 
                            ST_SetSRID(ST_MakePolygon(
                                ST_AddPoint(
                                ST_AddPoint( 
                                ST_AddPoint( 
                                ST_MakeLine(
                                /* Bottom left point */
                                (SELECT ship_geom FROM fleet WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1),
                                /* Top left point */
                                ST_Project
                                    (
                                        (SELECT ship_geom FROM fleet WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)::geography,
                                        (SELECT ship_length FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1),
                                        (SELECT bearing FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)
                                    )::geometry (Point,4326)),
                                /* Top Right point */
                                ST_Project
                                    (
                                        (
                                            ST_Project
                                            (
                                                (SELECT ship_geom FROM fleet WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)::geography,
                                                (SELECT ship_width FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1),
                                                (SELECT bearing + (Pi() * 0.5) FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)
                                            )::geometry (Point,4326)
                                        )::geography,
                                        (SELECT ship_length FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1),
                                        (SELECT bearing FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)
                                    )::geometry (Point,4326)),
                                /* Bottom right point */
                                ST_Project
                                    (
                                        (SELECT ship_geom FROM fleet WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)::geography,
                                        (SELECT ship_width FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1),
                                        (SELECT bearing + (Pi() * 0.5) FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)
                                    )::geometry (Point,4326)
                                ), 
                                /* Bottom left point */
                                (SELECT ship_geom FROM fleet WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1))
                            ), 4326);
                """

            cur.execute(sql)

            return "Shapes updated successfully."

    except:
        if(simulationDebugLevel > 1):
            print ("Host database configuration error.")
        return "Host database configuration error."

def updateShipShapesAlternate():
    """
    updateShipShapesAlternate
    Updates ship polygons so that they reflect the ship's current 
    position and dimensions. An alternate version
    that places ships at their polygon's center for position.
    """
    try:
        with DatabaseCursor(confPath) as cur:
            # Calculate new rectangles for ship geometry.
            # Ship reference points are on the bottom left corner
            sql = \
                f"""
                    UPDATE ship_shapes 
                        SET ship_polygon = 
                            ST_SetSRID(ST_MakePolygon(
                                ST_AddPoint(
                                ST_AddPoint( 
                                ST_AddPoint( 
                                ST_MakeLine(
                                /* Bottom left point */
                                (SELECT ship_geom FROM fleet WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1),
                                /* Top left point */
                                ST_Project
                                    (
                                        (SELECT ship_geom FROM fleet WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)::geography,
                                        (SELECT ship_length FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1),
                                        (SELECT bearing FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)
                                    )::geometry (Point,4326)),
                                /* Top Right point */
                                ST_Project
                                    (
                                        (
                                            ST_Project
                                            (
                                                (SELECT ship_geom FROM fleet WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)::geography,
                                                (SELECT ship_width FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1),
                                                (SELECT bearing + (Pi() * 0.5) FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)
                                            )::geometry (Point,4326)
                                        )::geography,
                                        (SELECT ship_length FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1),
                                        (SELECT bearing FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)
                                    )::geometry (Point,4326)),
                                /* Bottom right point */
                                ST_Project
                                    (
                                        (SELECT ship_geom FROM fleet WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)::geography,
                                        (SELECT ship_width FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1),
                                        (SELECT bearing + (Pi() * 0.5) FROM FLEET WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1)
                                    )::geometry (Point,4326)
                                ), 
                                /* Bottom left point */
                                (SELECT ship_geom FROM fleet WHERE fleet.ship_id = ship_shapes.ship_id LIMIT 1))
                            ), 4326);
                """

            cur.execute(sql)

            return "Shapes updated successfully."

    except:
        if(simulationDebugLevel > 1):
            print ("Host database configuration error.")
        return "Host database configuration error."

def addEnemyPosition(inX, inY, inRadius, inFleet = 0):
    """
    addEnemyPosition
    Attempts to move the fleet the specified distance in meters.
    """
    try:
        with DatabaseCursor(confPath) as cur:
            # Find max distance of fleet's slowest ship.
            sql = \
                f"""
                    INSERT INTO enemy_tracker 
                        (fleet_num, fleet_reference_point, certainty_radius)
                        VALUES
                        ({str(inFleet)}, 
                        ST_SetSRID(ST_MakePoint({str(inX)}, {str(inY)}), 4326), 
                        {str(inRadius)});
                """

            cur.execute(sql)

            return "Enemy position recorded successfully."

    except:
        if(simulationDebugLevel > 1):
            print ("Host database configuration error or invalid inputs.")
        return "Host database configuration error or invalid inputs."

@app.get("/moveFleet/{targetFleetNumber}/{targetDistance}")
def moveFleet(targetFleetNumber, targetDistance):
    """
    moveFleet
    Attempts to move the fleet the specified distance in meters.
    Ex. 
     http://localhost:8081/moveFleet/0/20
    """
    try:
        with DatabaseCursor(confPath) as cur:
            # Find max distance of fleet's slowest ship.
            sql = \
                f"""
                    SELECT min(speed) FROM fleet 
                        WHERE fleet_num = {str(targetFleetNumber)} LIMIT 1;
                """

            cur.execute(sql)
            minSpeed = cur.fetchone()[0]

            # Abort movement attempt if any ship in fleet is too slow
            # for movement to target destination.
            if int(minSpeed) < int(targetDistance):
                return "Error: Distance must be within minimum fleet max travel range."

            sql = \
                f"""
                    UPDATE fleet 
                        SET ship_geom = ST_Project(ship_geom::geography, 
                            {str(targetDistance)}, 
                            (SELECT bearing FROM fleet WHERE fleet_num = 
                                {str(targetFleetNumber)} LIMIT 1) * 180 / Pi()
                        )::geometry(Point, 4326)
                        WHERE fleet_num = {str(targetFleetNumber)};

                    UPDATE fleet_overview 
                        SET fleet_reference_point = ST_Project(
                            fleet_reference_point::geography, {str(targetDistance)}, 
                            (SELECT bearing FROM fleet_overview WHERE fleet_num = 
                            {str(targetFleetNumber)} LIMIT 1) * 180 / Pi()
                        )::geometry(Point, 4326)
                        WHERE fleet_num = {str(targetFleetNumber)};
                """

            cur.execute(sql)

        updateShipShapes()

        return "Fleet moved successfully."

    except:
        if(simulationDebugLevel > 1):
            print ("Host database configuration error or invalid inputs.")
        return "Host database configuration error or invalid inputs."

@app.get("/moveShip/{targetShipNumber}/{targetDistance}")
def moveFleet(targetShipNumber, targetDistance):
    """
    moveShip
    Attempts to move the ship the specified distance in meters.
    Also breaks off the ship from any existing fleet to create
    a new one. Note, after being broken off, it can and likely
    should be handled as its own fleet of one ship.
    Ex. 
     http://localhost:8081/moveShip/1/20
    """
    try:
        with DatabaseCursor(confPath) as cur:
            # Ensure this is a valid move
            sql = \
                f"""
                    SELECT min(speed) FROM fleet 
                        WHERE ship_num = {str(targetShipNumber)} LIMIT 1;
                """

            cur.execute(sql)
            minSpeed = cur.fetchone()[0]

            # Abort movement attempt if any ship in fleet is too slow
            # for movement to target destination.
            if int(minSpeed) < int(targetDistance):
                return "Error: Distance must be within ship max travel range."

            # Find max fleet id to create new unique id for ship's fleet
            sql = \
                f"""
                    SELECT MAX(fleet_num) FROM fleet_template LIMIT 1;
                """

            cur.execute(sql)
            newId = int(cur.fetchone()[0]) + 1

            # Place ship in new fleet and then handle the movement like one.
            sql = \
                f"""
                    UPDATE fleet 
                        SET fleet_num = {str(newId)}
                        WHERE ship_id = {str(targetShipNumber)};

                    UPDATE fleet_template 
                        SET fleet_num = {str(newId)}
                        WHERE ship_id = {str(targetShipNumber)};

                    INSERT INTO fleet_overview
                        (fleet_num, fleet_reference_point, bearing)
                        VALUES
                        (
                            {str(newId)}, 
                            (SELECT ship_geom FROM fleet WHERE fleet_num = {str(newId)} LIMIT 1), 
                            (SELECT bearing FROM fleet WHERE fleet_num = {str(newId)} LIMIT 1)
                        );
                """

            cur.execute(sql)

            moveFleet(newId, targetDistance)

            return "Ship moved successfully."

    except:
        if(simulationDebugLevel > 1):
            print ("Host database configuration error or invalid inputs.")
        return "Host database configuration error or invalid inputs."

@app.get("/rotateFleet/{targetFleetNumber}/{targetAngleDelta}")
def rotateFleet(targetFleetNumber, targetAngleDelta):
    """
    rotateFleet
    Attempts to rotate the fleet's ships by the specified angle in degrees.
    Positive numbers turn clockwise, negative numbers counter-clockwise.
    Ex. 
     http://localhost:8081/rotateFleet/0/20
    """
    try:
        with DatabaseCursor(confPath) as cur:
            # Find max angle of fleet's slowest turning ship.
            sql = \
                f"""
                    SELECT min(turn_radius) FROM fleet 
                        WHERE fleet_num = {str(targetFleetNumber)} LIMIT 1;
                """

            cur.execute(sql)
            minAngleDifference = cur.fetchone()[0]

            # Abort movement attempt if any ship in fleet can't turn enough.
            if int(minAngleDifference) < abs(targetAngleDelta):
                return "Error: Distance must be within minimum fleet max travel range."


            sql = \
                f"""
                    UPDATE fleet 
                        SET bearing = ((((bearing * 180 / Pi()) + 
                            {targetAngleDelta} + 360)::INTEGER % 360) * Pi() / 180)
                        WHERE fleet_num = {str(targetFleetNumber)};

                    UPDATE fleet_template 
                        SET bearing = ((((bearing * 180 / Pi()) + 
                        {targetAngleDelta} + 360)::INTEGER % 360) * Pi() / 180)
                        WHERE fleet_num = {str(targetFleetNumber)};

                    UPDATE fleet_overview 
                        SET bearing = ((((bearing * 180 / Pi()) + 
                        {targetAngleDelta} + 360)::INTEGER % 360) * Pi() / 180)
                        WHERE fleet_num = {str(targetFleetNumber)};
                """

            cur.execute(sql)

        updateShipShapes()

        return "Fleet rotated successfully."

    except:
        if(simulationDebugLevel > 1):
            print ("Host database configuration error or invalid inputs.")
        return "Host database configuration error or invalid inputs."

@app.get("/rotateShip/{targetShipNumber}/{targetAngleDelta}")
def rotateFleet(targetShipNumber, targetAngleDelta):
    """
    rotateShip
    Attempts to rotate the specified ship by the specified angle in degrees.
    Positive numbers turn clockwise, negative numbers counter-clockwise.
    Also breaks off the ship from any existing fleet to create
    a new one. Note, after being broken off, it can and likely
    should be handled as its own fleet of one ship.
    Ex. 
     http://localhost:8081/rotateFleet/0/20
    """
    try:
        with DatabaseCursor(confPath) as cur:
            # Ensure this is a valid rotation
            sql = \
                f"""
                    SELECT min(turn_radius) FROM fleet 
                        WHERE ship_num = {str(targetShipNumber)} LIMIT 1;
                """

            cur.execute(sql)
            minAngleDifference = cur.fetchone()[0]

            # Abort movement attempt if the ship can't turn enough.
            if int(minAngleDifference) < abs(targetAngleDelta):
                return "Error: Distance must be within minimum fleet max travel range."

            # Find max fleet id to create new unique id for ship's fleet
            sql = \
                f"""
                    SELECT MAX(fleet_num) FROM fleet_template LIMIT 1;
                """

            cur.execute(sql)
            newId = int(cur.fetchone()[0]) + 1

            # Place ship in new fleet and then handle the rotation like one.
            sql = \
                f"""
                    UPDATE fleet 
                        SET fleet_num = {str(newId)}
                        WHERE ship_id = {str(targetShipNumber)};

                    UPDATE fleet_template 
                        SET fleet_num = {str(newId)}
                        WHERE ship_id = {str(targetShipNumber)};

                    INSERT INTO fleet_overview
                        (fleet_num, fleet_reference_point, bearing)
                        VALUES
                        (
                            {str(newId)}, 
                            (SELECT ship_geom FROM fleet WHERE fleet_num = {str(newId)} LIMIT 1), 
                            (SELECT bearing FROM fleet WHERE fleet_num = {str(newId)} LIMIT 1)
                        );
                """

            cur.execute(sql)

            rotateFleet(newId, targetAngleDelta)

            return "Ship rotated successfully."

    except:
        if(simulationDebugLevel > 1):
            print ("Host database configuration error or invalid inputs.")
        return "Host database configuration error or invalid inputs."

@app.get("/rotateShipGuns/{targetShipNumber}/{targetAngleDelta}")
def rotateShipGuns(targetShipNumber, targetAngleDelta):
    """
    rotateShipGuns
    Attempts to rotate the ship's guns by the specified angle in degrees.
    Positive numbers turn clockwise, negative numbers counter-clockwise.
    Ex. 
     http://localhost:8081/rotateShipGuns/0/20
    """
    armamentList = []

    try:
        with DatabaseCursor(confPath) as cur:
            # Find list of matching guns to turn
            sql = \
                f"""
                    SELECT armament FROM fleet 
                        WHERE ship_id = {str(targetShipNumber)};
                """

            cur.execute(sql)
            armamentList = cur.fetchone()[0]

        # Abort rotation attempt if no matching guns.
        if (armamentList == None or len(armamentList) == 0):
            return "Error: Invalid ship or no guns on ship."

        # Iterate through each gun
        for index in range(0, len(armamentList)):
            armamentList[index]['gunAngle'] =             \
                (float(armamentList[index]['gunAngle']) + \
                (float(targetAngleDelta) * pi / 180)) %   \
                (pi * 2.0)
        with DatabaseCursor(confPath) as cur:

            # Clean up JSON formatting string for postgres
            armamentString = ""
            if(armamentList == None):
                armamentString = "null"
            else:
                armamentString = str(armamentList)
                armamentString = armamentString.replace('\'', '"')
                armamentString = armamentString.replace('None', 'null')

            sql = \
                f"""
                    UPDATE fleet 
                        SET armament = '{armamentString}'
                        WHERE ship_id = {str(targetShipNumber)};

                    UPDATE fleet_template 
                        SET armament = '{armamentString}'
                        WHERE ship_id = {str(targetShipNumber)};
                """

            cur.execute(sql)

        return "Ship guns rotated successfully."

    except:
        if(simulationDebugLevel > 1):
            print ("Host database configuration error or invalid inputs.")
        return "Host database configuration error or invalid inputs."

@app.get("/fireGun/{targetShipNumber}/{gunNumber}/{targetX}/{targetY}")
def fireGun(targetShipNumber, gunNumber, targetX, targetY):
    """
    fireGun
    Attempts to fire guns by collecting all necessary info and
    adjusting any relevant values.
    Ex. 
     http://localhost:8081/fireGun/0/0/30/60
    """
    try:
        with DatabaseCursor(confPath) as cur:
            # Collect and calculate many things relevant to firing weapons
            sql = \
                f"""
                    SELECT bearing, armament,  
                        /* Distance between gun and target. */
                        ST_Distance(
                            ST_Project(ship_geom::geography, bearing, (armament->{str(gunNumber)}->>'pos')::numeric), 
                            ST_SetSRID(ST_MakePoint({str(targetX)}, {str(targetX)}), 4326)::geography
                        ),
                        /* Angle between gun and target. */
                        ST_Angle(
                            ST_Project(ship_geom::geography, bearing, (armament->{str(gunNumber)}->>'pos')::numeric)::Geometry (Point, 4326), 
                            ST_SetSRID(ST_MakePoint(ST_X(ST_Project(ship_geom::geography, 
                                bearing, (armament->{str(gunNumber)}->>'pos')::numeric)::Geometry (Point, 4326)), 90), 4326), 
                            ST_Project(ship_geom::geography, bearing, (armament->{str(gunNumber)}->>'pos')::numeric)::Geometry (Point, 4326), 
                            ST_SetSRID(ST_MakePoint({str(targetX)}, {str(targetY)}), 4326)
                        )
                    FROM fleet where ship_id = 0;
                """
            cur.execute(sql)
            firingQuery = cur.fetchone()

            # Calculate firing result variables
            armamentList = list(firingQuery[1])
            shipBearing = firingQuery[0]
            print(gunNumber)
            print(armamentList)
            print(type(armamentList))
            print(armamentList[gunNumber])
            gunBearing = armamentList[gunNumber]['gunAngle']
            targetDistance = firingQuery[2]
            targetBearing = firingQuery[3]
            gunAngleAdjustment = float(targetBearing) - ((float(shipBearing) + float(gunBearing)) % (2 * pi))

            # Exit if no ammo or weapon
            if (float(armamentList[gunNumber]['gun']['ammo'][0]['count'] <= 0)):
                return "Invalid weapon or insufficient ammo."

            # Exit if out of range
            # Don't know how to calculate max range yet.
            maxRange = 100000
            if (float(targetDistance) >= maxRange):
                return "Selected target is out of range of gun."
                
            # Calculate shots fired in case limited ammo
            shotsFired = armamentList[gunNumber]['gun']['rof']
            if (float(armamentList[gunNumber]['gun']['ammo'][0]['count'] <= shotsFired)):
                shotsFired = armamentList[gunNumber]['gun']['ammo'][0]['count']

            armamentList[gunNumber]['gun']['ammo'][0]['count'] -= shotsFired
            armamentList[gunNumber]['gunAngle'] = (armamentList[gunNumber]['gunAngle'] + gunAngleAdjustment) % (2 * pi)

            # Update armaments
            # Clean up JSON formatting string for postgres
            armamentString = ""
            if(armamentList == None):
                armamentString = "null"
            else:
                armamentString = str(armamentList)
                armamentString = armamentString.replace('\'', '"')
                armamentString = armamentString.replace('None', 'null')

            sql = \
                f"""
                    UPDATE fleet 
                        SET armament = '{armamentString}'
                        WHERE ship_id = {str(targetShipNumber)};

                    UPDATE fleet_template 
                        SET armament = '{armamentString}'
                        WHERE ship_id = {str(targetShipNumber)};
                """

            cur.execute(sql)

        return ("Shot firing accounted for.")

    except:
        if(simulationDebugLevel > 1):
            print ("Host database configuration error or invalid inputs.")
        return "Host database configuration error or invalid inputs."

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

@app.get("/loadRegion")
def loadRegion():
    """
    loadFleetJSON
    Loads a JSON file for the bounding box.
    Generates several regions based on that
    and loads it as well as the bounding box
    into tables.
     http://localhost:8081/loadRegion
    """
    # Create variables with proper scope to store infile info
    inFileName = 'bbox.json'
    #fleetFileName = 'jsontest.json'
    # Select persistent first attacker address to query
    # Currently it only loads a local file instead.
    # Only local files currently.
    #url = "http://" + attackerIPs[0] + "/REGISTER"
    #fleetDict = json.loads(requests.get(url).content)

    try:
        inFile = open(inFileName)
        bboxDict = json.load(inFile)
        inFile.close()
    except:
        if(simulationDebugLevel > 1):
            print("Error reading fleet file.")
        return "Error reading fleet file."

    north = str(bboxDict['UpperLeft']['lat'])
    south = str(bboxDict['LowerRight']['lat'])
    east = str(bboxDict['LowerRight']['lon'])
    west = str(bboxDict['UpperLeft']['lon'])

    # Pick a random region.
    # Also ensure that a 1 degree buffer on both sides
    # of the border is built into future placement.
    cardinalList = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
        "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    degrees = random.random() * 360
    degrees = int(float(degrees))
    index = int((degrees + 11.25) / 22.5)
    direction = cardinalList[index % 16]
    regionLowAngle = (index * 22.5 - 10.25) * pi / 180
    regionHighAngle = (index * 22.5 + 10.25) * pi / 180

    if(direction == 0):
        regionLowAngle = 10.25 * pi / 180
        regionHighAngle = (360 - 10.25) * pi / 180

    try:
        with DatabaseCursor(confPath) as cur:

            # Spawn configs
            # Determines how much buffer room to leave at center and far edges.
            # Note: These are highly effected by projection issues,
            # so lower values are usually better, especially for min.
            desiredMinBuffer = 0.2
            desiredMaxBuffer = 0.45

            # Construct insertion query for this ship
            sql = \
                f"""
                    INSERT INTO bbox 
                        (bbox_geom)
                        VALUES
                        (
                            /* Generate original bounding box */
                            (SELECT
                            ST_MakePolygon(
                            ST_AddPoint(ST_AddPoint(ST_AddPoint(
                                ST_AsText(
                                ST_MakeLine(
                                ST_SetSRID(ST_MakePoint({str(west)}, {str(north)}), 4326), 
                                ST_SetSRID(ST_MakePoint({str(east)}, {str(north)}), 4326))), 
                                ST_SetSRID(ST_MakePoint({str(east)}, {str(south)}), 4326)),
                                ST_SetSRID(ST_MakePoint({str(west)}, {str(south)}), 4326)),
                                ST_SetSRID(ST_MakePoint({str(west)}, {str(north)}), 4326))))
                        );

                    /* Generate the box showing what part towards the center it should stay away from */
                    UPDATE bbox 
                        SET bbox_min_spawn = ST_SetSRID(ST_Buffer(ST_Centroid((SELECT bbox_geom FROM bbox LIMIT 1)), 
                            {str(desiredMinBuffer)} * LEAST({str(east)} - {str(west)}, {str(north)} - {str(south)})), 4326);

                    UPDATE bbox 
                        SET bbox_max_spawn = ST_SetSRID(ST_Buffer(ST_Centroid((SELECT bbox_geom FROM bbox LIMIT 1)), 
                            {str(desiredMaxBuffer)} * LEAST({str(east)} - {str(west)}, {str(north)} - {str(south)})), 4326);


                    DO $$
                    DECLARE rand_num float := random();
                    DECLARE count INTEGER := 1;
                    DECLARE new_x FLOAT := 0;
                    DECLARE new_y FLOAT := 0;
                    DECLARE rand_point geometry;
                    BEGIN
                    WHILE (count < 10001) LOOP
                        rand_point := (ST_SetSRID(ST_GeometryN(ST_GeneratePoints((SELECT bbox_geom FROM bbox LIMIT 1), 1), 1), 4326));

                        IF 	ST_Intersects(rand_point, (SELECT bbox_max_spawn FROM bbox LIMIT 1))
                        THEN
                            IF NOT ST_Intersects(rand_point, (SELECT bbox_min_spawn FROM bbox LIMIT 1))
                            THEN
                                IF (ST_Azimuth(ST_SetSRID(ST_Centroid((SELECT bbox_geom FROM bbox LIMIT 1)), 4326), rand_point) > {str(regionLowAngle)}) 
                                AND (ST_Azimuth(ST_SetSRID(ST_Centroid((SELECT bbox_geom FROM bbox LIMIT 1)), 4326), rand_point) < {str(regionHighAngle)})
                                THEN
                                    new_x := ST_X(rand_point);
                                    new_y := ST_Y(rand_point);
                                    count := 10002;
                                END IF;
                            END IF;
                        END IF;
                        count := count + 1;
                    END LOOP;
                    INSERT INTO fleet SELECT 
                                    ship_id, category, shipclass, displacement, ship_length, ship_width, torpedolaunchers,
                                    armament, armor, speed, turn_radius,
                                    ST_Translate(ST_Rotate(ship_geom, 2 * Pi() * rand_num, ST_SetSRID(ST_MakePoint(0,0), 4326)
                                    ), new_x, new_y)::geometry(Point, 4326),
                                    bearing, fleet_num 
                                    FROM fleet_template;
                    INSERT INTO fleet_overview (fleet_num, fleet_reference_point, bearing) 
	                    VALUES (0, ST_SetSRID(ST_MakePoint(new_x, new_y), 4326), 2 * Pi() * rand_num);
                    UPDATE fleet SET bearing = rand_num;
                    INSERT INTO ship_shapes (ship_id) SELECT 
                        ship_id
                        FROM fleet_template;
                    END$$;
                """
            cur.execute(sql)

        updateShipShapes()
    except:
        if(simulationDebugLevel > 0):
            print("Host database configuration error or invalid column field.")
        return ("Host database configuration error or invalid column field.")

@app.get("/loadFleetJSON")
def loadFleetJSON():
    """
    loadFleetJSON
    Loads the fleet from a connection or JSON file.
    Currently only checks a local JSON file named
    "ships.json"
     http://localhost:8081/loadFleetJSON
    """
    # Create variables with proper scope to store infile info
    fleetList = []
    fleetFileName = 'ships.json'
    #fleetFileName = 'jsontest.json'
    # Select persistent first attacker address to query
    # Currently it only loads a local file instead.
    # Only local files currently.
    #url = "http://" + attackerIPs[0] + "/REGISTER"
    #fleetDict = json.loads(requests.get(url).content)

    # Configure desired number of columns for fleet
    numCols = 10

    try:
        inFile = open(fleetFileName)
        fleetList = json.load(inFile)
        inFile.close()
    except:
        if(simulationDebugLevel > 1):
            print("Error reading fleet file.")
        return "Error reading fleet file."

    try:
        for index in range(0, len(fleetList)):
            with DatabaseCursor(confPath) as cur:
                # Add default gun angles to JSON
                if(fleetList[index]['armament'] != None):
                    for inIndex in range(0, len(fleetList[index]['armament'])):
                        fleetList[index]['armament'][inIndex]['gunAngle'] = 0

                # Clean up JSON formatting string for postgres
                armamentString = ""
                if(fleetList[index]['armament'] == None):
                    armamentString = "null"
                else:
                    armamentString = str(fleetList[index]['armament'])
                    armamentString = armamentString.replace('\'', '"')
                    armamentString = armamentString.replace('None', 'null')
                if(fleetList[index]['torpedoLaunchers'] == None):
                    torpedoString = "null"
                else:
                    torpedoString = str(fleetList[index]['torpedoLaunchers'])
                    torpedoString = torpedoString.replace('\'', '"')
                    torpedoString = torpedoString.replace('None', 'null')
                armorString = str(fleetList[index]['armor']).replace('\'', '"')
                armorString = armorString.replace('None', 'null')

                # Construct insertion query for this ship
                sql = \
                    f"""
                        INSERT INTO public.fleet_template 
                        (
                            ship_id, category, shipclass, displacement, ship_length, 
                            ship_width, torpedolaunchers, armament, armor, speed, 
                            turn_radius, ship_geom, ship_col, ship_row, fleet_num, bearing
                        ) 
                        VALUES 
                        (
                            {str(fleetList[index]['id'])}, '{str(fleetList[index]['category'])}', 
                            '{str(fleetList[index]['shipClass'])}', 0, {str(fleetList[index]['length'])}, 
                            {str(fleetList[index]['width'])}, '{torpedoString}', '{armamentString}', '{armorString}', 
                            {str(fleetList[index]['speed'])}, {str(fleetList[index]['turn_radius'])}, 
                            ST_SetSRID(ST_MakePoint(0, 0),4326), {str(int(index % numCols))}, {str(int(index / numCols))}, 
                            0, 0
                        );
                    """
                cur.execute(sql)

        # Calculate and update fleet template positions
        with DatabaseCursor(confPath) as cur:
            sql = \
                f"""
                    /* Handle staggered rows */
                        UPDATE fleet_template 
                            SET ship_geom = ST_Project(matching_row.ship_geom::geography, 222 * matching_row.ship_row, Pi()
                            )::geometry(Point, 4326)
                                FROM (SELECT ship_geom, ship_col, ship_row, ship_id FROM fleet_template) AS matching_row
                                WHERE (matching_row.ship_col % 3) = 0 AND fleet_template.ship_id = matching_row.ship_id;

                        UPDATE fleet_template 
                            SET ship_geom = ST_Project(matching_row.ship_geom::geography, 111 * matching_row.ship_col, (0.5 * Pi())
                            )::geometry(Point, 4326)
                                FROM (SELECT ship_geom, ship_col, ship_row, ship_id FROM fleet_template) AS matching_row
                                WHERE fleet_template.ship_id = matching_row.ship_id;
                                
                        UPDATE fleet_template 
                            SET ship_geom = ST_Project(matching_row.ship_geom::geography, (222 * matching_row.ship_row) + 111, Pi()
                            )::geometry(Point, 4326)
                                FROM (SELECT ship_geom, ship_col, ship_row, ship_id FROM fleet_template) AS matching_row
                                WHERE (matching_row.ship_col % 3) != 0 AND fleet_template.ship_id = matching_row.ship_id;
                """
            cur.execute(sql)

    except:
        if(simulationDebugLevel > 0):
            print("Host database configuration error or invalid column field.")
        return ("Host database configuration error or invalid column field.")
        
@app.get("/exportFleetJSON")
def exportFleetJSON():
    """
    exportFleetJSON
    Loads a fleet and returns it as a JSON file.
     http://localhost:8081/loadFleetJSON
    """
    # Create variables with proper scope to store return json info
    returnList = []
    shipTuple = None

    try:
        with DatabaseCursor(confPath) as cur:
            sql = \
                f"""
                    SELECT 
                        ship_id, category, shipclass, ship_length, 
                        ship_width, torpedolaunchers, armament, armor, speed, 
                        turn_radius, ship_geom::jsonb, displacement, bearing
                    FROM public.fleet_template;
                """
            cur.execute(sql)
            shipTuple = cur.fetchall()
        for index in range(0, len(shipTuple)):
            returnDict = {}
            returnDict['id'] = shipTuple[index][0]
            returnDict['category'] = shipTuple[index][1]
            returnDict['shipClass'] = shipTuple[index][2]
            returnDict['length'] = shipTuple[index][3]
            returnDict['width'] = shipTuple[index][4]
            returnDict['torpedoLaunchers'] = shipTuple[index][5]
            returnDict['armament'] = shipTuple[index][6]
            returnDict['armor'] = shipTuple[index][7]
            returnDict['speed'] = shipTuple[index][8]
            returnDict['turn_radius'] = shipTuple[index][9]
            returnDict['location'] = shipTuple[index][10]
            returnDict['displacement'] = shipTuple[index][11]
            returnDict['bearing'] = shipTuple[index][12]
            returnList.append(returnDict)
        return returnList
    except:
        if(simulationDebugLevel > 0):
            print("Host database configuration error or invalid column field.")
        return ("Host database configuration error or invalid column field.")

@app.get("/exportFleetPositionJSON")
def exportFleetPositionJSON():
    """
    exportFleetPositionJSON
    Loads a fleet and returns it as a JSON file 
    containing mostly simplified positional info.
     http://localhost:8081/loadFleetPositionJSON
    """
    # Create variables with proper scope to store return json info
    returnDict = {}
    returnDict['fleet_id'] = teamname
    returnList = []
    shipTuple = None

    try:
        with DatabaseCursor(confPath) as cur:
            sql = \
                f"""
					SELECT 
                        ship_id, bearing, ST_X(ST_Centroid(ship_geom)), ST_Y(ST_Centroid(ship_geom))
                    FROM public.fleet_template;
                """
            cur.execute(sql)
            shipTuple = cur.fetchall()
        for index in range(0, len(shipTuple)):
            returnShipDict = {}
            returnShipDict['ship_id'] = shipTuple[index][0]
            returnShipDict['bearing'] = shipTuple[index][1]
            returnShipDict['location'] = {'lon': shipTuple[index][2], 'lat': shipTuple[index][3]}
            returnList.append(returnShipDict)
        returnDict['ship_status'] = returnList
        return returnDict
    except:
        if(simulationDebugLevel > 0):
            print("Host database configuration error or invalid column field.")
        return ("Host database configuration error or invalid column field.")


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

@app.get("/initializeSimulation")
async def initializeSimulation():
    """
    initializeSimulation
    Performs work to load simulation initial values.
    Example syntax: 
     http://localhost:8081/initializeSimulation
    """

    # Configure pseudorandom seed
    #random.seed(randSeed)

    # Load persistent connection settings from database
    if(loadPersistentIPs() == "Host database configuration error, connection error, or invalid column field."):
        if(simulationDebugLevel > 0):
            print("Error loading persistent connection settings.")
        return "Error loading persistent connection settings."

    # Send athena request to load time
    global simulationTime
    simulationTime = 0

    # Reset all necessary databases
    try:
        with DatabaseCursor(confPath) as cur:
            # Construct proper SQL query statement
            # Drop and recreate existing tables
            sql = \
                f"""
                DROP TABLE IF EXISTS public.fleet_template;
                DROP TABLE IF EXISTS public.fleet;
                DROP TABLE IF EXISTS public.bbox;
                DROP TABLE IF EXISTS public.regions;
                DROP TABLE IF EXISTS public.fleet_overview;
                DROP TABLE IF EXISTS public.enemy_tracker;
                DROP TABLE IF EXISTS public.ship_shapes;

                CREATE TABLE public.fleet_template (
                    ship_id numeric NOT NULL,
                    category text,
                    shipclass text,
                    displacement numeric,
                    ship_length numeric,
                    ship_width numeric,
                    torpedolaunchers json,
                    armament json,
                    armor json,
                    speed numeric,
                    turn_radius numeric,
                    ship_geom geometry,
                    ship_col numeric,
                    ship_row numeric,
                    fleet_num numeric,
                    bearing numeric
                );
                
                CREATE TABLE public.fleet (
                    ship_id numeric NOT NULL,
                    category text,
                    shipclass text,
                    displacement numeric,
                    ship_length numeric,
                    ship_width numeric,
                    torpedolaunchers json,
                    armament json,
                    armor json,
                    speed numeric,
                    turn_radius numeric,
                    ship_geom geometry,
                    bearing numeric,
                    fleet_num numeric
                );

                CREATE TABLE public.bbox (
                    bbox_geom geometry, 
                    bbox_min_spawn geometry,
                    bbox_max_spawn geometry
                );
                
                CREATE TABLE public.regions (
                    region_id numeric NOT NULL,
                    region_geometry geometry
                );

                CREATE TABLE IF NOT EXISTS public.fleet_overview 
                (
                    fleet_num numeric,
                    fleet_reference_point geometry,
                    bearing numeric
                );

                CREATE TABLE IF NOT EXISTS public.enemy_tracker 
                (
                    fleet_num numeric,
                    fleet_reference_point geometry,
                    certainty_radius numeric
                );

                CREATE TABLE IF NOT EXISTS public.ship_shapes 
                (
                    ship_id numeric,
                    ship_polygon geometry
                );

                CREATE INDEX IF NOT EXISTS ship_shape_index
                    ON public.ship_shapes
                    USING GIST (ship_polygon);
                """

            cur.execute(sql)
        loadFleetJSON()
        loadRegion()
        # Return a copy of the fleet for debug or early builds
        if (simulationDebugLevel > 1):
            return exportFleetPositionJSON()
        else:
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
                    DROP TABLE IF EXISTS attacker_addresses;
                    DROP TABLE IF EXISTS defender_addresses;
                    DROP TABLE IF EXISTS athena_address;
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
                    CREATE TABLE IF NOT EXISTS attacker_addresses
                        (attacker_index SERIAL PRIMARY KEY, attack_address TEXT);
                    INSERT INTO attacker_addresses 
                        (attack_address) VALUES ('missilecommand.live:8080'); 
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create defender addresses table
            sql = \
                f"""
                    CREATE TABLE IF NOT EXISTS defender_addresses
                        (defender_index SERIAL PRIMARY KEY, defense_address TEXT);
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create athena address table
            sql = \
                f"""
                    CREATE TABLE IF NOT EXISTS athena_address
                        (athena_index SERIAL PRIMARY KEY, current_athena_address TEXT);
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create fleet table
            sql = \
                f"""
                    CREATE TABLE IF NOT EXISTS public.fleet (
                        ship_id numeric NOT NULL,
                        category text,
                        shipclass text,
                        displacement numeric,
                        ship_length numeric,
                        ship_width numeric,
                        torpedolaunchers json,
                        armament json,
                        armor json,
                        speed numeric,
                        turn_radius numeric,
                        ship_geom geometry, 
                        bearing numeric,
                        fleet_num numeric
                    );
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create fleet_template table
            sql = \
                f"""
                    CREATE TABLE IF NOT EXISTS public.fleet_template (
                        ship_id numeric NOT NULL,
                        category text,
                        shipclass text,
                        displacement numeric,
                        ship_length numeric,
                        ship_width numeric,
                        torpedolaunchers json,
                        armament json,
                        armor json,
                        speed numeric,
                        turn_radius numeric,
                        ship_geom geometry,
                        ship_col numeric,
                        ship_row numeric,
                        fleet_num numeric,
                        bearing numeric
                    );
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create bbox table
            sql = \
                f"""
                    CREATE TABLE IF NOT EXISTS public.bbox 
                    (
                        bbox_geom geometry, 
                        bbox_min_spawn geometry,
                        bbox_max_spawn geometry
                    );
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create fleet overview table
            sql = \
                f"""
                    CREATE TABLE IF NOT EXISTS public.fleet_overview 
                    (
                        fleet_num numeric,
                        fleet_reference_point geometry,
                        bearing numeric
                    );
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create regions table
            sql = \
                f"""
                    CREATE TABLE IF NOT EXISTS public.enemy_tracker 
                    (
                        fleet_num numeric,
                        fleet_reference_point geometry,
                        certainty_radius numeric
                    );
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Create regions table
            sql = \
                f"""
                    CREATE TABLE IF NOT EXISTS public.ship_shapes 
                    (
                        ship_id numeric,
                        ship_polygon geometry
                    );

                    CREATE INDEX IF NOT EXISTS ship_shape_index
                        ON public.ship_shapes
                        USING GIST (ship_polygon);
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
    # Note: Since no special operations are needed, in
    # the future this can probably be replaced with
    # just iterating through the table list.
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
            # Destroy fleet table
            sql = \
                f"""
                    DROP TABLE public.fleet;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy fleet_templates table
            sql = \
                f"""
                    DROP TABLE public.fleet_template;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy  bounding box table
            sql = \
                f"""
                    DROP TABLE public.bbox;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy fleet overview table
            sql = \
                f"""
                    DROP TABLE public.fleet_overview;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy enemy tracker table
            sql = \
                f"""
                    DROP TABLE public.enemy_tracker;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Destroy ship shapes table
            sql = \
                f"""
                    DROP TABLE public.ship_shapes;
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
    # Note: Since no special operations are needed, in
    # the future this can probably be replaced with
    # just iterating through the table list.
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
            # Vacuum and analyze fleet table
            sql = \
                f"""
                    VACUUM ANALYZE public.fleet;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze fleet template table
            sql = \
                f"""
                    VACUUM ANALYZE public.fleet_template;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze bounding box table
            sql = \
                f"""
                    VACUUM ANALYZE public.bbox;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze fleet overview table
            sql = \
                f"""
                    VACUUM ANALYZE public.fleet_overview;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze enemy tracker table
            sql = \
                f"""
                    VACUUM ANALYZE public.enemy_tracker;
                """
            cur.execute(sql)
        with DatabaseCursor(confPath) as cur:
            # Vacuum and analyze ship polygons table
            sql = \
                f"""
                    VACUUM ANALYZE public.ship_shapes;
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

