#!/usr/bin/env python
"""
Create admin user automatically
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from django.contrib.auth.models import User

# Check if admin user already exists
if User.objects.filter(username='admin').exists():
    print("Admin user already exists!")
    admin_user = User.objects.get(username='admin')
    print(f"Username: {admin_user.username}")
    print(f"Email: {admin_user.email}")
    
    # Update password
    admin_user.set_password('admin123')
    admin_user.save()
    print("Password updated to: admin123")
else:
    # Create new admin user
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print("Admin user created successfully!")
    print(f"Username: admin")
    print(f"Email: admin@example.com")
    print(f"Password: admin123")

print("\nYou can now login to Django admin at: http://localhost:8000/admin/")
