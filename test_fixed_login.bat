@echo off
echo ========================================
echo Testing Fixed Login Form
echo ========================================
echo.

cd /d "c:\Users\josh\Desktop\whitemeat"

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Checking superuser...
.venv\Scripts\python.exe setup_user.py

echo.
echo Starting server with fixed login form...
echo.
echo Go to: http://localhost:8000/login/
echo The form should now show only ONE clean login form!
echo.

.venv\Scripts\python.exe manage.py runserver

pause
