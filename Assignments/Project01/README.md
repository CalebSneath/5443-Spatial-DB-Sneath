# P01 - Project Setup - Implementation of a basic Python Postgres API for educational purposes.
## Caleb Sneath
#### September 8, 2022
#### Version: 0.1.0
### Description:

# Description: 
A simple Python database API created for educational purposes.

### Files

|   #   | File            | Description                                        |
| :---: | --------------- | -------------------------------------------------- |
|   1   | [spatialapi.py](https://github.com/CalebSneath/5443-Spatial-DB-Sneath/tree/main/Assignments/Project01/spatialapi.py)         | The main program that runs the api.   |
|   2   | [SQL Statements.txt](https://github.com/CalebSneath/5443-Spatial-DB-Sneath/blob/main/Assignments/Project01/SQL%20Statements.txt)         | A series of example SQL statements to create a database compatible with the API. |
|   3   | [filtered_cities.csv](https://github.com/CalebSneath/5443-Spatial-DB-Sneath/tree/main/Assignments/Project01/filtered_cities.csv)         | A compatible CSV file to be used as an example.  |
|   4   | [.config.json](https://github.com/CalebSneath/5443-Spatial-DB-Sneath/blob/main/Assignments/Project01/.config.json)         | A plain text configuration file for server and database settings.  |

### Commands and Special Operators

|   #   | Command         | Description                                        |
| :---: | --------------- | -------------------------------------------------- |
|   1   | findOne  | Matches an attribute and value. |
|   2   | findAll | Dumps entire table. |
|   3   | findClosest | Finds closest point in geometry. |

### Instructions

- Building: Requires Python (Tested for 3.9.5), FastAPI, and psycopg2.
- To install the last two, simply run in the terminal:
- pip install fastapi
- pip install psycopg2
- Afterward, set up your basic with pgAdmin and fill out the .config.json file. Run this file in the terminal with spatialapi.py and it should work.

# Credits
## Code Credit 
### Example data obtained from: 
https://cs.msutexas.edu/~griffin/data/

### Largely based on code obtained from: 
https://github.com/rugbyprof/5443-Spatial-DB/blob/main/Resources/04_ApiHelp/module/features.py
<br>

### Partial code snippet inspirations from:
https://stackoverflow.com/questions/32812463/setting-schema-for-all-queries-of-a-connection-in-psycopg2-getting-race-conditi
<br>
https://stackoverflow.com/questions/1984325/explaining-pythons-enter-and-exit
<br>
https://gis.stackexchange.com/questions/145007/creating-geometry-from-lat-lon-in-table-using-postgis
