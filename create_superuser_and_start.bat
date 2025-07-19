@echo off
echo ========================================
echo Django Superuser Setup
echo ========================================
echo.

cd /d "c:\Users\josh\Desktop\whitemeat"

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Checking for existing superusers...
.venv\Scripts\python.exe setup_user.py

echo.
echo ========================================
echo CREATE SUPERUSER (if needed)
echo ========================================
echo If no superuser was found above, create one now:
echo.
.venv\Scripts\python.exe manage.py createsuperuser

echo.
echo ========================================
echo LOGIN INSTRUCTIONS
echo ========================================
echo 1. Go to: http://localhost:8000/
echo 2. Click LOGIN in the footer
echo 3. Use the superuser credentials you just created
echo 4. Access your custom admin dashboard!
echo.
echo Starting Django server...
echo.

.venv\Scripts\python.exe manage.py runserver

pause
