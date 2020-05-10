: https://www.alltrails.com/fr/
: http://www.traildino.com

@IF [%1]==[] @ECHO Usage Gpx2gpi.bat {input file.gpx} [max routes] & Exit /b1
@IF NOT EXIST "%~dpn1.gpx" (
    @ECHO %~dpn1.gpx not found
    @EXIT /b1
)
@SET INP=%~dpn1
@SET NAME=%~n1
@IF NOT EXIST %~dp1Out @mkdir %~dp1Out
@SET OUT=%~dp1Out\%NAME%
@SHIFT
@IF [%1] == [] @SET SIMPLIFY=
@IF NOT [%1] == [] @SET SIMPLIFY=-x simplify,count=%1 & @SHIFT

@SET BABEL=C:\Program Files (x86)\GPSBabel\gpsbabel.exe
@SET BITMAP=c:\Usr\Maps\MapTools\Scripts\PinBlue.6X11.bmp

"%BABEL%" -w -i gpx,suppresswhite=1,gpxver=1.1 -f "%INP%.gpx" %SIMPLIFY% -x transform,wpt=trk,del -o garmin_gpi,bitmap="%BITMAP%",category="%NAME%",unique=1 -F "%OUT%.gpi"
"%BABEL%" -w -i gpx,suppresswhite=1,gpxver=1.1 -f "%INP%.gpx" %SIMPLIFY% -o gpx,gpxver=1.1 -F "%OUT%.trk.gpx"
"%BABEL%" -w -i gpx,suppresswhite=1,gpxver=1.1 -f "%INP%.gpx" %SIMPLIFY% -x transform,rte=trk,del -o gpx,gpxver=1.1 -F "%OUT%.rte.gpx"

"%BABEL%" -w -i gpx,suppresswhite=1,gpxver=1.1 -f "%INP%.gpx" %SIMPLIFY% -x transform,wpt=trk,del -o unicsv -F "%OUT%.csv"
@ECHO Edit file "%OUT%.csv", then press enter
@PAUSE
"%BABEL%" -w -i unicsv -f "%OUT%.csv" -o garmin_gpi,bitmap="%BITMAP%",category="%NAME%",unique=1 -F "%OUT%.edit.gpi"
