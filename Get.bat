@IF [%1] == [] (
    @Echo get.bat "RuleFile" [options] StyleName
    @Echo         -r enable routing
    @Echo         -nt no type 
    @Echo         -mx set mapname to 436x ^(must be numeric^)
    @Echo         -dx set description to "x"
    @Echo         -sx use server x ^(0-6^)
    @Echo           1=de, 2=fr, 3=lz4, 4=dh, 5=kumi, 6=z, 0=none
    @Echo usage: get.bat marly.dat -r -m0001 -s4 -dMarly e20
    @goto done
)

@set sname=%~n1
@set dname=%~n1
@SHIFT
@set osmname=%sname%.osm
@set output=.\output
@set opts=--gmapsupp --latin1 --add-pois-to-areas --ignore-fixme-values
@set opts1=--family-id=1000 --product-id=1
@set style=--style-file="..\Styles\e10"
@set type="..\Styles\e10.typ"
@set style=--style-file="..\Styles\e20x"
@set type="..\Styles\e20x.typ"
@set skipget=0
@set skiptype=0
@set server="http://overpass-api.de/api/interpreter"

:Loop
    @IF [%1]==[] GOTO Continue
    @set var=%1
    @SHIFT

    @if /I %var:~0,2% == -m (
        @set opts2=--mapname=436%var:~2%
        @goto Loop
    )
    @if /I %var:~0,2% == -d (
        @set opts3=--description=%var:~2%
        @set dname=%var:~2%
        @goto Loop
    )
    @if /I [%var%] == [-r] (
        @set opts=%opts% --route
        @goto Loop
    )
    @if /I [%var%] == [-nt] (
        @set skiptype=1
        @goto Loop
    )
    @if /I %var:~0,2% == -s (
        @set skipget=0
        @if %var:~2% == 0 set skipget=1
        @if %var:~2% == 1 set server="http://overpass-api.de/api/interpreter"
        @if %var:~2% == 2 set server="http://overpass.openstreetmap.fr/api/interpreter"
        @if %var:~2% == 3 set server="https://lz4.overpass-api.de/api/interpreter"
        @if %var:~2% == 4 set server="http://overpass.osm.ch/api/interpreter"
        @if %var:~2% == 5 set server="https://overpass.kumi.systems/api/interpreter"
        @if %var:~2% == 6 set server="https://z.overpass-api.de/api/interpreter"
        @goto Loop
    )
    @set style=--style-file="..\Styles\%var%"
    @set type="..\Styles\%var%.typ"
    @GOTO Loop

:Continue

@if %skipget% == 1 goto SkipGet1
@If Not Exist "%sname%.dat" goto error1
c:\usr\bin\wget -O "%osmname%" --post-file="%sname%.dat" %server%
@IF %ERRORLEVEL% NEQ 0 GOTO error2

:SkipGet1
@if skiptype == 1 set type=""
@set opts1=%opts1% %opts2% %opts3%
java -Xmx6000m -jar "..\mkgmap\mkgmap.jar" %opts% %style% %opts1% --output-dir="%output%\%sname%" ".\%osmname%" %type%

@if not errorlevel 0 goto error3
@copy /B "%output%\%sname%\gmapsupp.img" "%output%\%sname%\gmapbmap.img" >NUL 2>&1
@copy /B "%output%\%sname%\gmapsupp.img" "%output%\%dname%.img" >NUL 2>&1
@copy /B "%output%\%sname%\*.img" "%output%" >NUL 2>&1

@del "%output%\%sname%\gmapsupp.img" >NUL 2>&1
@del "%output%\%sname%\osmmap.tdb" >NUL 2>&1
@del "%output%\%sname%\osmmap.img" >NUL 2>&1
@del "%output%\gmapbmap.img" >NUL 2>&1
@del "%output%\gmapsupp.img" >NUL 2>&1
@del "%output%\osmmap.img" >NUL 2>&1

@echo created "%output%\%sname%\gmapbmap.img"
@echo created "%output%\%dname%.img"

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
