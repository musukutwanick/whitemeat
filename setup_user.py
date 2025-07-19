import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from django.contrib.auth.models import User

try:
    # Check if any superuser exists
    superusers = User.objects.filter(is_superuser=True)
    
    if superusers.exists():
        print("Superuser(s) found:")
        for user in superusers:
            print(f"- Username: {user.username}")
            print(f"- Email: {user.email}")
        
        print(f"\nYou can login to the custom admin with any of these superuser credentials.")
        print("Go to: http://localhost:8000/login/")
        
    else:
        print("No superuser found. Creating default admin user...")
        # Create new admin user
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Admin user created successfully!")
        print("\nLogin credentials:")
        print("Username: admin")
        print("Password: admin123")
    
    print("\nCustom Login URL: http://localhost:8000/login/")
    print("Django Admin URL: http://localhost:8000/admin/")
    
except Exception as e:
    print(f"Error: {e}")
