@echo off
echo ========================================
echo Django Database Setup
echo ========================================
echo.

:: Navigate to the directory containing this script
cd /d "%~dp0"

:: Check if a local virtual environment exists
if exist .venv\Scripts\python.exe (
    echo Local virtual environment found. Activating...
    call .venv\Scripts\activate.bat
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    echo No local virtual environment (.venv) found. Using global python.
    set PYTHON_CMD=python
)

echo.
echo Step 1: Creating migrations...
%PYTHON_CMD% manage.py makemigrations frontend

echo.
echo Step 2: Applying migrations...
%PYTHON_CMD% manage.py migrate

echo.
echo Step 3: Setting up initial data...
%PYTHON_CMD% setup_data.py

echo.
echo Step 4: Checking superuser...
%PYTHON_CMD% setup_user.py

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo Your custom admin dashboard is now ready!
echo.
echo Starting Django server...
echo Go to: http://localhost:8000/login/
echo.

%PYTHON_CMD% manage.py runserver

pause
