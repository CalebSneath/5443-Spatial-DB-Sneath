/*
# Author: Caleb Sneath
# Assignment: P01 - Project Setup
# Date: September 29, 2022
#
# Description:
# A collection of database backups, query commands, and screenshots to show the results of 
# loading spatial data from files, randomly generating spatial data, detecting and predicting 
# collisions, and visualizing that data. This project is designed as the first part of a 
# multi-part project with the goal of creating something similar to the 80's arcade game, 
# "Missile Command". This part of the project specifically focuses on reading and generating 
# the data for missile paths as well as military bases.
#
# Instructions:
# Create a new database in PGAdmin. Load up the PostGIS extension.
# Run the following code in the query tool.
# More assistance available on the GitHub Repository.
#
# Credits:
# Example data obtained from: 
# https://github.com/rugbyprof/5443-Spatial-DB/tree/main/Assignments/P02
# https://github.com/rugbyprof/5443-Spatial-DB/tree/main/Assignments/P03
# Code Inspiration:
# The intersection query was partially inspired by an answer on this question:
# https://gis.stackexchange.com/questions/271824/st-intersection-intersection-of-all-geometries-in-a-table
*/

/* Create a field to serve as identifiers */
CREATE TABLE hostile_projectiles (id SERIAL PRIMARY KEY);

/* Sequentially add up to the desired amount of rows (1000 in this case) */
/* while generating random starting times. */
/* Starting times will be in seconds, from 0 to 30,000. */
ALTER TABLE hostile_projectiles ADD COLUMN start_time FLOAT;

DO $$
DECLARE
count INTEGER := 0;
BEGIN
WHILE (count < 1001) LOOP
	INSERT INTO hostile_projectiles ("start_time") VALUES (random() * 30000);
	count := count + 1;
END LOOP;
END$$;

/* ogr2ogr command used to load geojson file. */
/*
ogr2ogr -f "PostgreSQL" PG:"dbname=P03A user=Example password=Example" "C:\databases\data\P03A\us_bbox.geojson" -nln bound_box -append
*/

/* Generate the starting points */

ALTER TABLE hostile_projectiles ADD COLUMN start_point geometry;

/* Sequentially add random starting points to the desired amount of rows (1000 in this case) */
DO $$
DECLARE
count INTEGER := 1;
DECLARE geo_box geometry := ST_SetSRID(
	ST_GeomFromText(
	'LINESTRING(-129.7844079 19.7433195,-61.9513812 19.7433195 , -61.9513812 54.3457868,-129.7844079 54.3457868, -129.7844079 19.7433195)'
	), 4326);
DECLARE geo_cent geography := ST_Centroid(geo_box::geometry)::geography(Point, 4326);
DECLARE geo_rand_initial geometry;
DECLARE temp_line geography;
DECLARE temp_angle FLOAT;
BEGIN
WHILE (count < 1001) LOOP
	temp_angle := 2 * pi() * random();
	geo_rand_initial := ST_SetSRID(ST_Project(geo_cent, 5000000, temp_angle)::geometry(Point, 4326), 4326);
	temp_line := ST_MakeLine(geo_rand_initial, ST_SetSRID(geo_cent::geometry, 4326))::geography;
	UPDATE hostile_projectiles SET start_point = ST_Intersection( temp_line, geo_box::geography )::geometry(Point, 4326)
		WHERE "id" = count;
	count := count + 1;
END LOOP;
END$$;



/* Add new row for ending points */
ALTER TABLE hostile_projectiles ADD COLUMN end_point geometry(Point, 4326);


/* Sequentially add random ending points to the desired amount of rows (1000 in this case) 
	based on a starting point within a certain range, biased so it will go closer to the middle of the box.
*/
DO $$
DECLARE
count INTEGER := 1;
DECLARE geo_box geometry := ST_SetSRID(
	ST_GeomFromText(
	'LINESTRING(-129.7844079 19.7433195,-61.9513812 19.7433195 , -61.9513812 54.3457868,-129.7844079 54.3457868, -129.7844079 19.7433195)'
	), 4326);
DECLARE geo_cent geography := ST_Centroid(geo_box)::geography;
DECLARE geo_pole_line geometry:= ST_SetSRID(ST_MakeLine(geo_cent::geometry(Point, 4326), ST_MakePoint(ST_X(geo_cent::geometry(Point, 4326)), 90.0)::geometry(Point, 4326)), 4326);
DECLARE geo_rand_initial geometry;
DECLARE temp_start_line geometry;
DECLARE temp_line geography;
DECLARE temp_angle FLOAT;
DECLARE starter geometry;
BEGIN
WHILE (count < 1001) LOOP
	SELECT start_point FROM hostile_projectiles WHERE "id" = count INTO starter;
	temp_start_line := ST_SetSRID(ST_MakeLine(geo_cent::geometry(Point, 4326), starter), 4326);
	temp_angle := ST_ANGLE(geo_pole_line, temp_start_line) + (0.7 * pi()) + (0.6 * random() * pi()); 
	geo_rand_initial := ST_SetSRID(ST_Project(geo_cent, 5000000, temp_angle)::geometry(Point, 4326), 4326);
	temp_line := ST_MakeLine(geo_rand_initial, ST_SetSRID(geo_cent::geometry, 4326))::geography;
	UPDATE hostile_projectiles SET end_point = ST_Intersection( temp_line, geo_box::geography )::geometry(Point, 4326)
		WHERE "id" = count; 
	count := count + 1;
END LOOP;
END$$;

/* Create line from prior points */
ALTER TABLE hostile_projectiles ADD COLUMN trajectory geometry;
UPDATE hostile_projectiles SET trajectory = ST_LineInterpolatePoints(ST_MakeLine(start_point, end_point), 0.03125, true);

/* Make a spatial index for trajectory */
CREATE INDEX geom_index
 ON hostile_projectiles 
 USING gist(trajectory);

/* Calculate a reasonable missile end time.
   Missiles will be assumed to travel randomly from between 0.5 to 1.5 times the speed of sound.
   The speed of sound is about 343 meters per second.
*/
ALTER TABLE hostile_projectiles ADD COLUMN end_time FLOAT;

UPDATE hostile_projectiles SET end_time = start_time + (ST_Distance(start_point::geography, end_point::geography) / ((random() + 0.5) * 343));


/* Drop now redundant beginning and end points */
ALTER TABLE hostile_projectiles DROP COLUMN start_point;
ALTER TABLE hostile_projectiles DROP COLUMN end_point;

SELECT *,trajectory::json FROM hostile_projectiles;

/* Calculate Intersections, grabbing only 10000 here for faster processing of this particular dataset. */
/* Credit: Partially Inspired By: */
/* https://gis.stackexchange.com/questions/271824/st-intersection-intersection-of-all-geometries-in-a-table */
CREATE TABLE collisions (id SERIAL PRIMARY KEY);
ALTER TABLE collisions ADD COLUMN intersects geometry;
INSERT INTO collisions (intersects) 
select ST_SetSRID((ST_Intersection(ST_Buffer(ST_SetSRID(us_mil.geom, 4326)::geography, 1000000.0), hostile_projectiles.trajectory::geography))::geometry, 4326) from us_mil, hostile_projectiles 
where ST_Intersects
    (ST_Buffer(ST_SetSRID(us_mil.geom, 4326)::geography, 1000000.0), hostile_projectiles.trajectory::geography) LIMIT 10000;
SELECT *, intersects::json from collisions;