# Test Admin Access Script
Write-Host "Testing Django Admin Access..." -ForegroundColor Green

# Activate virtual environment and start server
Write-Host "Starting Django server..." -ForegroundColor Yellow
& "C:\Users\josh\Desktop\whitemeat\.venv\Scripts\python.exe" manage.py runserver 8001
