@echo off
echo ========================================
echo Django Database Setup
echo ========================================
echo.

cd /d "c:\Users\josh\Desktop\whitemeat"

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Step 1: Creating migrations...
.venv\Scripts\python.exe manage.py makemigrations frontend

echo.
echo Step 2: Applying migrations...
.venv\Scripts\python.exe manage.py migrate

echo.
echo Step 3: Setting up initial data...
.venv\Scripts\python.exe setup_data.py

echo.
echo Step 4: Checking superuser...
.venv\Scripts\python.exe setup_user.py

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo Your custom admin dashboard is now ready!
echo.
echo Starting Django server...
echo Go to: http://localhost:8000/login/
echo.

.venv\Scripts\python.exe manage.py runserver

pause
