@echo off
echo ========================================
echo Testing Custom Admin Login Flow
echo ========================================
echo.

cd /d "c:\Users\josh\Desktop\whitemeat"

echo 1. Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo 2. Creating admin user (if not exists)...
.venv\Scripts\python.exe setup_user.py

echo.
echo 3. Starting Django development server...
echo.
echo ========================================
echo TEST THE LOGIN FLOW:
echo ========================================
echo 1. Go to: http://localhost:8000/
echo 2. Scroll to footer and click "LOGIN" button
echo 3. Enter credentials: admin / admin123
echo 4. Should redirect to custom admin dashboard
echo.
echo URLs for testing:
echo - Main Site: http://localhost:8000/
echo - Direct Login: http://localhost:8000/login/
echo - Admin Dashboard: http://localhost:8000/dashboard/
echo ========================================
echo.

.venv\Scripts\python.exe manage.py runserver

pause
