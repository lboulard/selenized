@SETLOCAL
@ECHO OFF
IF NOT EXIST "%~dp0\tenv\." CALL :mkenv "%~dp0\tenv"
"%~dp0\tenv\Scripts\python.exe" "%~dpn0.py"
EXIT /B %ERRORLEVEVEL%

:mkenv
ECHO ON
py -3.8 -m venv "%~1"
"%~dp0\tenv\Scripts\pip.exe" install colormath
@ECHO OFF
IF ERRORLEVEL 1 EXIT /B %ERRORLEVEVEL%
