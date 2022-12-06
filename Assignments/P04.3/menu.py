#!/usr/bin/env python3
##############################################################################
# Author: Caleb Sneath
# Assignment: P04.X - Battleship API
# Date: November 30, 2022
# Python 3.9.5
# Project Version: 0.3.0
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
# pip install pika
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
# Broswer Instructions:
# - To load up a new round of the simulation, run in your browser:
#   "http://{address}/initializeSimulation". This will generate
#   the desired output file.
# - The simulation will either produce an error message or run until
#   it is finished
# - To restart, just go back to the initializeSimulation step.
# Multiplayer Terminal Menu Instructions:
# - Open up a terminal in the "menu.py" directory.
# - Run "python3 menu.py"
##############################################################################

import json
import requests
from comms import CommsSender
from comms import CommsListener

class BattleshipMenu:
    def __init__(self):
        # Member variables
        self.ownDatabaseDetails = {}
        self.hostileConnectionDetails = {}
        self.menuList = []

        # Default load file names
        menuFileName = "menu.json"
        ownDBFileName = ".config.json"
        hostileConnectionFileName = "login.json"

        # Load data into member variables
        with open(menuFileName) as loadFile:
            self.menuList = json.load(loadFile)
        with open(ownDBFileName) as loadFile:
            self.ownDatabaseDetails = json.load(loadFile)
        with open(hostileConnectionFileName) as loadFile:
            self.hostileConnectionDetails = json.load(loadFile)

    def generateAuthString(self): 
        """
        generateAuthString
        Placeholder function in case anything in this class has 
        functionality added that needs quick construction of
        an authentication string. 
        """
        return "placeholder"

    def genericRoute(self, inRoute, inParams = ""):
        """
        genericRoute
        Generates a generic "get" request from the 
        config file's host and port that can follow the
        format of:
        "http://host:port/" and then a variable number
        of fields such as:
        "x/20/y/30"etc.
        """
        path = "http://" + self.ownDatabaseDetails['host'] + ":" + str(self.ownDatabaseDetails['publicport'])
        commandField = "/" + str(inRoute)
        if inParams != "" and inParams != None:
            commandField += ("/" + str(inParams))
        try:
            # Grab the response
            url = path + commandField
            returnCode = requests.get(url).content

            # Format and/or display the response
            if (str(type(returnCode)) == "<class 'bytes'>"):
                intermediateFormatted = str(returnCode).replace("\"'", '"').replace('"', "'").replace("b'", "", 1).replace("}'", "}")
                returnFormatted = (json.loads(intermediateFormatted.replace("'", '"')))
                returnJSONified = json.dumps(returnFormatted, indent=3)
                print(returnJSONified)
            else:
                print(str(returnCode))
            return "request processed"
        except:
            return "request error"

    def processMenuItem(self, inItem):
        """
        processMenuItem
        Reads the config file item for the inputted inItem
        parameter. Then, takes the user's input and calls
        the relevant route.
        """
        printItem = json.dumps(self.menuList[inItem], indent=3)
        print(printItem)

        menuChoice = 1
        while(menuChoice != len(self.menuList)):
            print("Enter any parameters, separated by a slash '/'.")
            print("To instead exit and return to the previous menu, enter 'back'.")

            paramEntry = input()

            if paramEntry == 'back':
                return
                
            processedString = self.genericRoute(self.menuList[inItem]['route'], paramEntry)
            print(processedString)
            if (processedString == "request processed"):
                return
            else:
                print("Please try again.")

    def turnMenu(self):
        """
        turnMenu
        Contains options to launch games and all available options
        available during a turn. All options are loaded from a menu file
        called "menu.json" which contains all descriptions and actual
        route lists.
        """
        print("Beginning game session.")

        menuChoice = 1
        while(int(menuChoice) != len(self.menuList)):
            print("Enter the number of your desired inputs.")
            print("If your desired route needs anything else, enter every field as asked.")
            print("To simply preview an entry, select it and enter 'back'.")

            for index in range(0, len(self.menuList)):
                printEntry = str(index) + " " + self.menuList[index]['item']
                print(printEntry)
            exitEntry = str(len(self.menuList)) + " " + "Exit game"
            print(exitEntry)

            try:
                menuChoice = int(input())
            except:
                menuChoice = 1
                print("Invalid input. Try again.")

            # Run commands if valid
            if(menuChoice >= 0 and menuChoice < len(self.menuList)):
                self.processMenuItem(menuChoice)
            
            # Move to new menu if needed
            print("Command processed.")

    def startMenu(self):
        """
        startMenu
        The top level menu for the simulation.
        Contains several options suited more for management of
        the client-side software as a whole, such as routes
        to manage local databases and tables. Aside from that
        this menu function also contains the options to start
        the normal simulation options or to exit.
        """
        print("Battleship Multiplayer Client")
        print("Enter the number of your desired inputs.")
        print("If your desired route needs anything else, enter every field as asked.")

        routeList = []
        routeList.append("initializeSimulation")
        routeList.append("destroyTables")
        routeList.append("createTables")
        routeList.append("tableMaintenance")

        menuChoice = 1
        while(menuChoice != 0 and menuChoice != 4):
            print("0. Start game.")
            print("1. Destroy tables.")
            print("2. Create tables.")
            print("3. Vacuum/Analyze tables.")
            print("4. Exit.")
            try:
                menuChoice = int(input())
            except:
                menuChoice = 1
                print("Invalid input. Try again.")

            # Run commands if valid
            # Currently doesn't boot game here. Can be changed
            # by tweaking menuChoice > 0 to >=
            if(menuChoice > 0 and menuChoice < len(routeList)):
                print(self.genericRoute(routeList[menuChoice]))
            
            # Move to new menu if needed
            if menuChoice == 0:
                self.turnMenu()

        print("Exiting session.")
            
if __name__ == "__main__":

    gameSession = BattleshipMenu()
    gameSession.startMenu()
