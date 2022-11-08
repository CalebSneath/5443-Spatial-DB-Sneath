# P03 - Missile Command (Part 2) - A Defender Missile Defense Simulation.
## Caleb Sneath
#### November 08, 2022

# Description: 
A fastAPI and psycopg2 based api for the simulation of a missile defense system. This simulation is designed to be used by the defender, and supports one or more attackers. The API makes use of several techniques to try and improve speed, including the use of spatial indices, routes to facilitate the maintenance of the table by vacuuming and analyzing it, cleaning up data between simulations, discretizing the problem, exiting early when solutions are found, as well as breaking the problem up into multiple parts when helpful. On top of speed, this solution also has a few settings to customize the 
A collection of database backups, query commands, and screenshots to show the results of loading spatial data from files, randomly generating spatial data, detecting and predicting collisions, and visualizing that data. This project is designed as the first part of a multi-part project with the goal of creating something similar to the 80's arcade game, "Missile Command". This part of the project specifically focuses on reading and generating the data for missile paths as well as military bases.

### Files

|   #   | File            | Description                                        |
| :---: | --------------- | -------------------------------------------------- |
|   1   | [spatialapi.py](https://github.com/CalebSneath/5443-Spatial-DB-Sneath/tree/main/Assignments/P04A/spatialapi.py)         | Contains the main program file.  |
|   2   | [module/__init__.py](https://github.com/CalebSneath/5443-Spatial-DB-Sneath/tree/main/Assignments/P04A/module/__init__.py)         | Contains the commands to generate the random missile paths and timestamps. |
|   2   | [module/timeconversion.py](https://github.com/CalebSneath/5443-Spatial-DB-Sneath/tree/main/Assignments/P04A/module/timeconversion.py)         | Contains the commands to generate the random missile paths and timestamps. |
|   3   | [Various .jpeg files]  | Screenshots to show end data visualization.  |

### Local Instructions:
 Building: Requires Python (Tested for 3.9.5), FastAPI, and psycopg2. To install the last two, simply run in the terminal:
- pip install fastapi
- pip install psycopg2
 Afterward, set up your basic with pgAdmin and fill out the .config.json file. Adjust the line below to your install path if necessary for the confPath variable.Run this file in the terminal with spatialapi.py and it should work.

### Server Instructions: 
 Get whatever server provider you choose. Follow the above instructions for local install. If pip install fails for psycopg2, try with the precompiled binaries instead by using:
   pip install psycopg2-binary
 For the ip address, ip probably needs to be set to "0.0.0.0" in config. Postgres and postgis may need to be installed also if they are not.

## Running Instructions:
 - After setting up with the above instructions, run "spatialapi.py".
 - Open up your web browser.
 - For all instructions below, {address} will be a placeholder for whatever ip and port you entered in the config file or for your server. For example, if you are running on a server with ip "167.999.99.99", and you selected port 8081, {address} would mean "167.999.99.99:8081". Likewise, if it was instead on localhost with port 8080, it would be "localhost:8081". Both of these are of course without the quotes.
 - For your first time running, in your address bar type and enter "http://{address}/createTables". This will create all tables for the first time in the database. This shouldn't need to be done again, unless you want to remove logged solutions.
 - Add whatever attacker's you need by typing into your address bar "http://{address}/addAttackerIP/{target address}" where {target address} follows a similar pattern as address, just for the attacker. Repeat this for any attackers.
 - (Optional) To permanently save an attacker ip so this does not need to be done again, in your address bar run "http://{address}/persistCurrentIPs"
 - To load up a new round of the simulation, run in your browser: "http://{address}/initializeSimulation". This will not begin the simulation by itself to allow other people to get ready.
 - When you are ready to begin, run 
   "http://localhost:8081/simulationControlLoop"
 - The simulation will either produce an error message or run until the arsenal is depleted and then automatically send the messsage to all attackers to end the simulation. 
 - To restart, just go back to the initializeSimulation step.

### Overview
In order for a reasonable simulation to be run, bases need to be modeled, and flight paths for the missiles need to be generated. The region is loaded from a json object sent by the attacker which also contains the assigned arsenal.
<br>
<img src="Trajectories.jpeg" width="720">
<br>
With two missile points and timestamps, a linear trajectory can be extrapolated. Aside from their relative position to each other, the starting times are rather meaningless. Up to a certain timestamp later which can be configured in the source code, the linear flight path of incoming missiles from radar sweeps can be predicted and placed into a temporary table by looking at the difference in X, Y, and Z components of the two points and then dividing by the difference in time. Note that this only works if the missiles do indeed follow linear motion.
<br>
<img src="Intersections.jpeg" width="720">
<br>
A query is run to select the closest point to a missile battery, which is above the ground, and which has a distance no greater than the currently considered missile can reach for that timestamp of the extrapolated path. If it is, we know that the missile can in fact reach it then, so that will be the final destination of the missile. This can further be used to solve for the launch time.
<br>
<img src="Final_Visualization.jpeg" width="720">
<br>

### Known Issues
Since this relies upon assumptions of linear motion, any curve in trajectories will produce an incorrect solution. Also, it uses an approximation to create the speed that only somewhat works in North America, but is vastly incorrect elsewhere due to the curvature of the Earth affecting the conversion from degrees to meters.

# Credits
### Example data obtained from: 
### https://github.com/rugbyprof/5443-Spatial-DB/tree/main/Assignments/P02
### https://github.com/rugbyprof/5443-Spatial-DB/tree/main/Assignments/P03
<br>

### Code Inspiration:
An early intersection query was partially inspired by an answer on this question:
### https://gis.stackexchange.com/questions/271824/st-intersection-intersection-of-all-geometries-in-a-table
