@echo off
echo Creating admin user...

cd /d "c:\Users\josh\Desktop\whitemeat"
call .venv\Scripts\activate.bat

echo.
echo Running admin creation script...
.venv\Scripts\python.exe create_admin.py

echo.
echo Starting server...
echo Go to: http://localhost:8000/admin/
echo Username: admin
echo Password: admin123
echo.
.venv\Scripts\python.exe manage.py runserver

pause
