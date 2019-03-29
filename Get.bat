@set sname=%~n1
@set osmname=%sname%.osm
@set opts=--gmapsupp --latin1 --make-poi-index --add-pois-to-lines --add-pois-to-areas --check-styles
@set style=--style-file="..\e10"
@if not %3. == . set style=--style=%3
@if %2. == -f. goto wget
@if %2. == -F. goto wget
@if Exist %osmname% goto skipGet

:wget
@If Not Exist "%sname%.dat" goto error1
@c:\usr\bin\wget -O "%osmname%" --post-file=%sname%.dat http://overpass-api.de/api/interpreter
@IF %ERRORLEVEL% NEQ 0 GOTO error2

:skipGet
java -Xmx6000m -jar "..\mkgmap\mkgmap.jar" %opts% %style% --family-id=1000 --product-id=1 --output-dir=".\output\%sname%" ".\%osmname%" "..\e10\e10.txt"
@if not errorlevel 0 goto error3
@copy /B ".\output\%sname%\gmapsupp.img" ".\output\%sname%\gmapbmap.img" 

@del ".\output\%sname%\gmapsupp.img"
@del ".\output\%sname%\osmmap.tdb"
@del ".\output\%sname%\osmmap.img"
@del ".\output\%sname%\e10.typ"
@del ".\output\%sname%\63240001.img"

goto done

:error3
@echo Error executing mkgmap "%osmname%" (%ERRORLEVEL%)
goto done
:error2
@echo Error executing Wget "%sname%.dat" (%ERRORLEVEL%)
goto done
:error1
@echo "%sname%.dat" not found
:done
@exit /b
