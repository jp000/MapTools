

if exist "%~1.geojson" "C:\Program Files (x86)\GPSBabel\gpsbabel.exe" -w -i geojson -f "%~1" -o garmin_gpi,category="%2",alerts=1,proximity=100m,hide -F "%~pn1.gpi"

if exist "%~1.geojson" "C:\Program Files (x86)\GPSBabel\gpsbabel.exe" -w -i geojson -f "%~1" -o garmin_gpi,category="%2b",alerts=1,proximity=100m,bitmap="PinBlue.bmp" -F "%~pn1_b.gpi"

if exist "%~1.geojson" "C:\Program Files (x86)\GPSBabel\gpsbabel.exe" -w -i geojson -f "%~1" -o garmin_gpi,category="%2r",alerts=1,proximity=100m,bitmap="PinRed.bmp" -F "%~pn1_r.gpi"

if exist "%~1.gpx" "C:\Program Files (x86)\GPSBabel\gpsbabel.exe" -w -i gpx -f "%~1" -o garmin_gpi,category="%2" -F "%~pn1_g.gpi"

if exist "%~1.geojson" "C:\Program Files (x86)\GPSBabel\gpsbabel.exe" -w -i geojson -f "%~1" -o tomtom -F "%~pn1.ov2"

