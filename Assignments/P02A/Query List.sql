/* US Roads Query */
SELECT gid,linearid,fullname,rttyp,mtfcc,geom::json
 FROM primary_roads
	LIMIT 5;

/* US Rails Query */
SELECT gid,linearid,fullname,mtfcc,geom::json
 FROM us_rails
	LIMIT 5;

/* US States Query */
SELECT gid,region,division,statefp,statens,geoid,stusps,name,lsad,mtfcc,funcstat,aland,awater,intptlat,intptlon,geom::json
 FROM us_states
	LIMIT 5; 

/* US Military Query */
SELECT gid,ansicode,areaid,fullname,mtfcc,aland,awater,intptlat,intptlon,geom::json
 FROM us_mil
	LIMIT 5; 

/* Airports Query */
SELECT id,name,city,country,code3,code4,elevation,gmt,tz_short,timezone,location_type,airport_type,geom::json
 FROM airports
	LIMIT 5;

/* Time Zones Query */
SELECT gid,objectid,scalerank,featurecla,name,map_color6,map_color8,note,zone,utc_format,time_zone,iso_8601,places,dst_places,tz_name1st,tz_namesum,geom::json
 FROM time_zones
	LIMIT 5; 
