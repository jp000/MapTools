@set sname=%~n1
@If Not Exist "%sname%.dat" goto error1

@set name=%sname%.osm
@if Exist %name% goto skipGet

@c:\usr\bin\wget -O "%name%" --post-file=%sname%.dat http://overpass-api.de/api/interpreter
@IF %ERRORLEVEL% NEQ 0 GOTO error2

:skipGet
@java -Xmx6000m -jar "..\mkgmap\mkgmap.jar" --style-file="..\e10" --gmapsupp --latin1 --add-pois-to-lines --add-pois-to-areas --check-styles --family-id=1000 --product-id=1 --output-dir=".\output\%sname%" ".\%name%" "..\e10\e10.txt"
@if not errorlevel 0 goto error3
@copy /B ".\output\%sname%\gmapsupp.img" ".\output\%sname%\gmapbmap.img" 

@del ".\output\%sname%\gmapsupp.img"
@del ".\output\%sname%\osmmap.tdb"
@del ".\output\%sname%\osmmap.img"
@del ".\output\%sname%\e10.typ"
@del ".\output\%sname%\63240001.img"

goto done

:error3
@echo Error executing mkgmap "%name%.osm" (%ERRORLEVEL%)
goto done
:error2
@echo Error executing Wget "%sname%.dat" (%ERRORLEVEL%)
goto done
:error1
@echo "%sname%.dat" not found
:done
