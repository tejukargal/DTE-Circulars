@echo off
echo Setting up Virtual Environment...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing/updating dependencies...
venv\Scripts\pip.exe install -r requirements.txt

echo.
echo Starting DTE Circulars Web App...
echo Open your browser and go to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

venv\Scripts\python.exe app.py
pause