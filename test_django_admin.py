#!/usr/bin/env python
"""
Test script to verify Django admin access
"""
import os
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    
    print("Testing Django Admin Setup...")
    print(f"Admin users count: {User.objects.filter(is_superuser=True).count()}")
    
    if User.objects.filter(is_superuser=True).exists():
        admin_user = User.objects.filter(is_superuser=True).first()
        print(f"Admin user exists: {admin_user.username}")
        print("You can access Django admin at: http://localhost:8000/admin/")
    else:
        print("No admin user found. Please run setup_admin.bat first.")
    
    print("\nStarting Django server...")
    execute_from_command_line(['manage.py', 'runserver'])
