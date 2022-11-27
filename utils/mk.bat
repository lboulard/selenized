@SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
@ECHO OFF
CD /D "%~dp0"
SET OUTDIR=output\
FOR %%f IN (palettes\*.py) DO CALL :gen "%%f"
FOR %%f IN (palettes\personalized\*.py) DO CALL :gen "%%f"
FOR %%f IN (%OUTDIR%*.color-listing) DO CALL :rename "%%f"
SET FILES=
FOR %%f IN (%OUTDIR%*.json) DO SET "FILES=!FILES! "%%f""
ECHO ON
jq -s "{schemes: [.[].schemes[]]}" %FILES% >selenized.msterminal-schemes.json
@ECHO OFF
GOTO :EOF

:gen
IF "%~n1"=="selenized_base" GOTO :EOF
ECHO ON
.\tenv\Scripts\python.exe evaluate_template.py "%~1"^
 templates\color-listing.template^
 templates\mintty.minttyrc.template^
 templates\msterminal.json.template
@ECHO OFF
IF ERRORLEVEL 1 EXIT /B %ERRORLEVEVEL%
GOTO :EOF

:rename
ECHO ON
MOVE /Y "%~1" "%~dpn1.txt"
@ECHO OFF
IF ERRORLEVEL 1 EXIT /B %ERRORLEVEVEL%
GOTO :EOF
