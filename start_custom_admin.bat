@echo off
echo ========================================
echo The White Meat Company - Custom Admin
echo ========================================
echo.

cd /d "c:\Users\josh\Desktop\whitemeat"

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Setting up admin user...
.venv\Scripts\python.exe setup_user.py

echo.
echo Starting Django development server...
echo.
echo ========================================
echo ADMIN ACCESS INFORMATION:
echo ========================================
echo Custom Login Page: http://localhost:8000/login/
echo Django Admin (Built-in): http://localhost:8000/admin/
echo.
echo Login Credentials:
echo Username: admin
echo Password: admin123
echo.
echo After logging in at /login/, you'll access your custom admin dashboard!
echo ========================================
echo.

.venv\Scripts\python.exe manage.py runserver

pause
