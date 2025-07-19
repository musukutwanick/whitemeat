# PowerShell script to start Django server
Set-Location "c:\Users\josh\Desktop\whitemeat"

# Activate virtual environment
& ".\\.venv\\Scripts\\Activate.ps1"

# Apply migrations
Write-Host "Applying database migrations..." -ForegroundColor Green
python manage.py migrate

# Create superuser if needed
Write-Host "You can now create a superuser..." -ForegroundColor Yellow
Write-Host "Run: python manage.py createsuperuser" -ForegroundColor Yellow

# Start server
Write-Host "Starting Django development server..." -ForegroundColor Green
Write-Host "Visit: http://localhost:8000/" -ForegroundColor Cyan
Write-Host "Admin: http://localhost:8000/admin/" -ForegroundColor Cyan
Write-Host "Custom Dashboard: http://localhost:8000/login/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red

python manage.py runserver
