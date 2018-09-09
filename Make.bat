@if [%1] == [] goto err
@if [%2] == [] goto err

:: Change this to suite your needs
@set family=1000
@set product=1
@set rootDir=.
@set options=--latin1 --add-pois-to-areas --check-styles  --list-styles
:: increase this to get larger chunks of maps
@set maxnodes=3250000

set typFile=%~2\%~n2.txt
set outDir=.\output\%~n1
@set mkgmap=%rootDir%\mkgmap\mkgmap.jar
@set splitter=%rootDir%\splitter\splitter.jar

del %outDir%\*.pbf

java -Xmx6000m -jar "%splitter%" --max-nodes=%maxnodes% --output-dir=%outDir% "%~1"

del "%outDir%\*.img"
FOR %%I IN ("%outDir%\*.pbf") DO  (
java -Xmx6000m -jar "%mkgmap%" --style-file="%2" --gmapsupp %options% --family-id=%family% --product-id=%product% --output-dir="%outDir%" "%%I" %typFile%
if exist "%outDir%\gmapbmap.img" del "%outDir%\gmapbmap.%%~nI.img"
copy /B "%outDir%\gmapsupp.img" "%outDir%\gmapbmap_%%~nI.img"
)
goto done
:err
@ echo usage Make.bat "file_to_process(.osm)" "style_direcory"
:done
