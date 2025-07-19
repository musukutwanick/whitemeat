"""
Django Admin Setup Script for The White Meat Company

This script helps you set up Django admin access.

INSTRUCTIONS:
1. Open a new terminal/command prompt
2. Navigate to your project directory: cd "c:\Users\josh\Desktop\whitemeat"
3. Activate virtual environment: .venv\Scripts\activate
4. Run the following commands one by one:

STEP 1: Apply migrations
-----------------------
python manage.py migrate

STEP 2: Create a superuser (admin)
----------------------------------
python manage.py createsuperuser

When prompted, enter:
- Username: admin (or your preferred username)
- Email: your-email@example.com
- Password: (choose a secure password)
- Password (again): (repeat the same password)

STEP 3: Start the development server
------------------------------------
python manage.py runserver

STEP 4: Access Django Admin
---------------------------
1. Open your browser
2. Go to: http://localhost:8000/admin/
3. Login with the username and password you created
4. You can now manage users, groups, and other Django admin features

STEP 5: Access Your Custom Admin Dashboard
------------------------------------------
1. Go to: http://localhost:8000/login/
2. Login with the same credentials
3. You'll be redirected to your custom admin dashboard
4. From there you can manage restaurant branches and menu items

TROUBLESHOOTING:
- If you get "Pillow not installed" error, run: pip install Pillow
- If migrations fail, try: python manage.py makemigrations frontend
- If you forget your admin password, you can create a new superuser

WHAT'S NEXT:
After creating the admin user, you can:
1. Add restaurant branches and menu categories by running: python manage.py shell < setup_data.py
2. Start adding menu items through the custom admin dashboard
3. Create notices and announcements
"""

import os
import sys

def main():
    print("🚀 Django Admin Setup for The White Meat Company")
    print("=" * 50)
    
    project_dir = r"c:\Users\josh\Desktop\whitemeat"
    venv_python = r".venv\Scripts\python.exe"
    
    print(f"Project Directory: {project_dir}")
    print(f"Virtual Environment: {venv_python}")
    print()
    
    print("📋 SETUP STEPS:")
    print("1. python manage.py migrate")
    print("2. python manage.py createsuperuser")
    print("3. python manage.py runserver")
    print("4. Visit http://localhost:8000/admin/")
    print()
    
    print("💡 ADMIN URLS:")
    print("- Django Admin: http://localhost:8000/admin/")
    print("- Custom Dashboard: http://localhost:8000/login/")
    print("- Main Website: http://localhost:8000/")
    print()
    
    print("🎯 After setup, you can manage:")
    print("- Users and permissions (Django admin)")
    print("- Restaurant branches")
    print("- Menu items with images")
    print("- Notices and announcements")

if __name__ == "__main__":
    main()
