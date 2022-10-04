SELECT gid,ansicode,areaid,fullname,mtfcc,aland,awater,intptlat,intptlon,geom::json
 FROM us_mil
	LIMIT 5; 
	
SELECT id, trajectory::json, start_time, end_time
 FROM hostile_projectiles
	LIMIT 5; 