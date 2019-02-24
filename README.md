# Maptools
This is a set of different files and scripts to create user defined maps for the Garmin's Etrex 10  
The mapping information is provided by **OpenStreetMap**

Given the following file structure

    +Maps/
      +mkgmap/
      +splitter/
      +e10/
      +output/

## Download and install ##
- [mkgmap](http://www.mkgmap.org.uk/download/mkgmap.html "mkgmap") `=> Maps/mkgmap`
- [splitter](http://www.mkgmap.org.uk/download/splitter.html "splitter") `=> Maps/splitter`
## Download maps  ##
- [extract.bbbike.org](https://extract.bbbike.org/?lang=en "bbbike")
- [https://garmin.openstreetmap.nl](garmin.openstreetmap.nl/)
## Other tools ##
- [www.gpsies.com](https://www.gpsies.com) `=> draw tracks and download gpx files`
- [inkatlas.com](https://inkatlas.com) `=> print maps`
- [geojson.io](http://geojson.io) `=> nice drawing on maps and download geojson files (for polygons, lines and points)`
- [POILoaderforWindows](https://www8.garmin.com/support/download_details.jsp?id=927) `=> copy pois to the garmin`
# Etrex 10 #
This is the low end Garmin GPS device with very limited ressources. Some say it is too basic, but given the right tools it can be a marvel and it has very good battery life!   
The idea is to have a map as large as possible with a minimal number of features required for your activity.  
The above mentioned tools will help you split and reduce the size of the map to fit in your device (max 5 to 7 MB).  
Also reserve some memory space for route tracking and extra POI  
The different Python scripts will assist you in creating the proper maps, ready to be processed by **mkgmap**  
You can also use the web site **extract.bbbike.com** to select portions of maps to download
### Files in E10 directory ###
The files in directory ./Maps/E10 (**relations**, **lines**, **points**, etc...) give the rules for element extraction and rendering on the GPS device
  
Examples lines (show rivers at different resolution with different rendering:  
>*(waterway=river | waterway=canal | waterway=drain) & tunnel!=yes {name '${name}'} \[0x1f resolution 18\]  
>waterway=stream & tunnel!=yes \[0x18 resolution 22\]*

Example point (show usefull POI's when wandering):  
>*amenity~'biergarten|cafe|restaurant|bar|pub' {name '${name}'}  \[0x4600 resolution 24 default_name 'Cafe'\]  
>amenity=toilets \[0x4e00 resolution 22 default_name 'Wc'\]  
>amenity=drinking_water|drinking_water=yes|drinkable=yes \[0x5000 resolution 22 default_name 'Drink'\]*  

By giving a default name you can then search on the device for the nearest amenity

There are also rules to abbreviate names on the map, show routes that are part of relations (trails, bike routes, bus routes, etc.)

By tailoring those files, you can add or remove information that gets displayed on the device
## Mkgmap & Overpass ##
Here is a simple example to get a map of island of Elba

    cd Maps  
    wget -O elba.osm "http://overpass-api.de/api/interpreter?data=[out:xml];node(poly:\"42.70363 10.09403 42.70363 10.45383 42.87622 10.45383 42.87622 10.09403 42.70363 10.09403\");( ._; <;);out body;"
    ... or ...
    wget -O elba.osm "http://overpass-api.de/api/interpreter?data=[out:xml];(area[name=\"Isola d'Elba\"][place=island];)->.x;(node(area.x);<;way(area.x);<;relation(area.x);<<;);out body;"
    java -Xmx6000m -jar ".\mkgmap\mkgmap.jar" --style-file=".\e10" --gmapsupp --latin1 --add-pois-to-lines --add-pois-to-areas --check-styles --family-id=1000 --product-id=1 --output-dir=".\output\Elba" ".\Elba.osm" ".\e10\e10.txt"  
    copy /B ".\output\Elba\gmapsupp.img" ".\output\Elba\gmapbmap.img"  
Have a look at OverpassApi.py for other variants
## Batch files ##
### MakeSingle.bat ###
Create a single map (gmapbmap.jar) from an .osm input file and style directory  
`MakeSingle.bat "file_to_process(.osm)" "style_direcory"`
### Make.bat ###
Create a multiple map (splitter.jar and gmapbmap.jar) from an .osm input file and style directory, the input file is split first  
`Make.bat "file_to_process(.osm)" "style_direcory"`
# Scripts #
Those scripts are by no mean fully fledged applications, just quick&dirty code to get the job done. They can be hacked and adapted to automate repetitive processes, like regenerating the data for a map every so often.
## Osm2Gpx.py ##
Create a gpx file given a relation number.
This can be used by the script bbbikeExtract.py to create bounding boxes
## BbbikeExtract.py ##
Given a gpx file, find all bounding boxes of a given surface
The output can be be passed to the site `extract.bbbike.org`
## OverpassApi.py ##
This contains functions to get data from `overpass-api.de/api` with samples of different methods.
## Json2Overpass.py ##
This will extract polygons defined in geojson format from **geojson.io** in a format suitable for Overpass API  
It will also output lines and points coordinates in different formats, to paste into your queries.
  
Example:  
- draw a square aroud Elba island, using `http://geojson.io`, save it as "map.geojson"  
- execute python Json2Overpass.py "map.geojson" => *node(poly:"42.70363 10.09403 42.70363 10.45383 42.87622 10.45383 42.87622 10.09403 42.70363 10.09403");*  
- copy/paste the node info into the next line  
- http://overpass-api.de/api/interpreter?data=[out:xml];*node(poly:"42.70363 10.09403 42.70363 10.45383 42.87622 10.45383 42.87622 10.09403 42.70363 10.09403");*( ._; <;);out body;  
- rename the output file Elba.osm"  
This will give you an **18MB** of data
 
When you use the MakeSingle.Bat file, you will get a **282KB** file (gmapbmap) that can be copyied to your Etrex10 device.

