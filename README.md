#KML -> GeoJSON
===

Here is a veyr basic attempt to turn a KML into a geojson file

##How to use
	
Run from terminal


	python model.py --l  http://data.cabq.gov/transit/routesandstops/transitstops.kmz --kmz >> test2.geojson
	

or if you already have the file locally


    python model.py --l file:///Users/javier/Downloads/highschools.kml >> hs.geojson