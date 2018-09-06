@if [%1] == [] goto err
@if [%2] == [] goto err

@set subdir=
@if not [%3] == [] @set subdir=\%~3

:: Change this to suite your needs
@set family=1000
@set product=1
@set rootDir=.
@set options=--latin1 --add-pois-to-areas --check-styles  --list-styles

set typFile=%~2\%~n2.txt
set outDir=.\output\%~n1
@set mkgmap=%rootDir%\mkgmap\mkgmap.jar
@set splitter=%rootDir%\splitter\splitter.jar

@del "%outDir%\*.img"
java -Xmx6000m -jar "%mkgmap%" --style-file="%2" --gmapsupp %options% --family-id=%family% --product-id=%product% --output-dir="%outDir%" "%1" "%typFile%"
@if not exist "%outDir%%subdir%" mkdir "%outDir%%subdir%
copy /B "%outDir%\gmapsupp.img" "%outDir%%subdir%\gmapbmap.img"
goto done

:err
@ echo usage MakeSingle.bat "file_to_process(.osm)" "style_direcory" ["subdir"]
:done
