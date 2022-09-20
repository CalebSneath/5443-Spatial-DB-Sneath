# P02 - World Data - Practice Spatial Data Importation, Indices, and Querying.
## Caleb Sneath
#### September 19, 2022
### Description:

# Description: 
A collection of database backups, query commands, and screenshots to show the results of loading spatial data from files, creating spatial indices, and querying these files. Except for one file where the data was obtained from a shape file and shape types and indices were constructed using spatial functions, all tables were created using the shp2pgsql GUI with postgres.

### Files

|   #   | File            | Description                                        |
| :---: | --------------- | -------------------------------------------------- |
|   1   | [Query List.SQL](https://github.com/CalebSneath/5443-Spatial-DB-Sneath/blob/main/Assignments/P02A/Query%20List.sql)         | Contains the queries to view several of the rows and every column, with geometry set to display as a more human readable format.   |
|   2   | [airports SQL.txt](https://github.com/CalebSneath/5443-Spatial-DB-Sneath/tree/main/Assignments/P02A/airports%20SQL.txt)         | Additional queries used instead of the shp2pgsql command for the airports .csv file. |
|   3   | [Various .SQL files]  | Recreates the final resulting table.  |
|   4   | [Various .PNG files]  | Screenshots showing the ran queries.  |
|   5   | [Various .7Z files]  | Various compressed .SQL files.  |

### Instructions

- Load up PGAdmin or your preferred database management software.
- Create or load a database. This database was named "P02A"
- Run the SQL commands on any of the .SQL files to copy the resulting database.

### Overview
There are many different ways to create a spatial geometry. Geometries can be loaded from special shape files, or they can be manually constructed from their constituent parts using various spatial functions. Much like indices for normal data types, spatial data types can also create indices. Although this isn't always a good idea, for data that is infrequently modified and used for queries with a lot of sparse data, this can save an immense amount of time. For this reason, some commands automatically make use of spatial indices, however this isn't always the case.

# Credits
### Example data obtained from: 
### https://github.com/rugbyprof/5443-Spatial-DB/tree/main/Assignments/P02
