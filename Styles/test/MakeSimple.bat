@set family=1000
@set product=1
@set rootDir=c:\Usr\Maps

@set mkgmap=%rootDir%\mkgmap\mkgmap.jar
@set splitter=%rootDir%\splitter\splitter.jar

::java -Xmx6000m -jar "%mkgmap%" --style-file=".\test" --gmapsupp --family-id=%family% --product-id=%product% --output-dir=".\tmp" "points.osm"

java -Xmx6000m -jar "%mkgmap%" --style-file=".\test" --index --gmapsupp test-map:all-elements