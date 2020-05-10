@IF [%1] == [] (
@echo file.gpx convert to file.geojson
goto done
)
SET DIST = %2
IF [%2] == [] SET DIST=200

"C:\Program Files (x86)\GPSBabel\gpsbabel.exe" -w -r -t -i gpx -f "%~1" -x duplicate,location -x position,distance=%DIST%M -o geojson -F "%~dpn1.geojson"
"C:\Program Files (x86)\GPSBabel\gpsbabel.exe" -w -r -t -i gpx -f "%~1" -o geojson -F "%~dpn1_1.geojson"
"C:\Program Files (x86)\GPSBabel\gpsbabel.exe" -w -r -t -i gpx -f "%~1" -x duplicate,location -x position,distance=%DIST%M -o gpx -F "%~dpn1_1.gpx"
:done
