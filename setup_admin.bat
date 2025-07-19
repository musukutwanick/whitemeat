@echo off
echo ========================================
echo Django Setup - The White Meat Company
echo ========================================

cd /d "c:\Users\josh\Desktop\whitemeat"

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Applying database migrations...
python manage.py migrate

echo.
echo ========================================
echo STEP 1: CREATE ADMIN USER
echo ========================================
echo Please create your admin user:
echo.
python manage.py createsuperuser

echo.
echo ========================================
echo STEP 2: CHANGE ADMIN PASSWORD
echo ========================================
echo Changing password for admin user:
echo.
.venv\Scripts\python.exe manage.py changepassword admin

echo.
echo ========================================
echo STEP 3: START SERVER
echo ========================================
echo Starting Django development server...
echo.
echo IMPORTANT URLS:
echo - Main Website: http://localhost:8000/
echo - Django Admin: http://localhost:8000/admin/
echo - Custom Dashboard: http://localhost:8000/login/
echo.
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver

pause
