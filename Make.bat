@if %1. == . goto err
@if %2. == . goto err

@set family=1000
@set product=1
@set rootDir=.
@set options=--latin1 --make-poi-index --add-pois-to-lines --add-pois-to-areas --check-styles --bounds="%rootDir%\bounds.zip" --precomp-sea="%rootDir%\sea.zip"
:: increase this to get larger chunks of maps
@set maxnodes=3250000

set typFile=%~2\%~n2.txt
set outDir=.\output\%~n1
@set mkgmap=%rootDir%\mkgmap\mkgmap.jar
@set splitter=%rootDir%\splitter\splitter.jar

@if %3. == ns. goto skip

del %outDir%\*.pbf

java -Xmx6000m -jar "%splitter%" --max-nodes=%maxnodes% --output-dir=%outDir% "%~1"

:skip
del "%outDir%\*.img"
FOR %%I IN ("%outDir%\*.pbf") DO  (
java -Xmx6000m -jar "%mkgmap%" --style-file="%2" --gmapsupp %options% --family-id=%family% --product-id=%product% --output-dir="%outDir%" "%%I" %typFile%
if exist "%outDir%\gmapbmap.img" del "%outDir%\gmapbmap.%%~nI.img"
copy /B "%outDir%\gmapsupp.img" "%outDir%\gmapbmap_%%~nI.img"
)
goto done

pause edit file template.args
java -Xmx6000m -jar "%mkgmap%" --style-file="%2" --gmapsupp %options% --family-id=%family% --product-id=%product% --output-dir="%outDir%" -c "%outDir%\template.args" %typFile%

:err
@ echo usage MakeSplit.bat "file_to_split" "style_direcory" [ns]
:done
