@echo off
echo Testing Django Admin Access...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if admin user exists
echo Checking for admin user...
.venv\Scripts\python.exe manage.py shell -c "from django.contrib.auth.models import User; print('Admin user exists:', User.objects.filter(is_superuser=True).exists())"

echo.
echo Starting Django server...
echo Access Django admin at: http://localhost:8000/admin/
echo.
.venv\Scripts\python.exe manage.py runserver

pause
