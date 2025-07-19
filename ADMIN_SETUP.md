# Django Admin Setup Guide for The White Meat Company

## 🚀 Quick Setup Instructions

### Step 1: Open Terminal/Command Prompt
1. Press `Windows + R`, type `cmd`, press Enter
2. Navigate to your project: `cd "c:\Users\josh\Desktop\whitemeat"`

### Step 2: Activate Virtual Environment
```bash
.venv\Scripts\activate
```
You should see `(whitemeat)` or similar at the beginning of your command prompt.

### Step 3: Install Required Packages (if needed)
```bash
pip install Pillow
```

### Step 4: Apply Database Migrations
```bash
python manage.py migrate
```

### Step 5: Create Admin User
```bash
python manage.py createsuperuser
```
When prompted, enter:
- **Username**: `admin` (or your choice)
- **Email**: `admin@whitemeatcompany.zw` (or your email)
- **Password**: Choose a secure password
- **Password (again)**: Repeat the same password

### Step 6: Set Up Initial Data (Optional)
```bash
python manage.py shell < setup_data.py
```
This creates the restaurant branches (Rabbit Hole Main, PaGomo) and menu categories.

### Step 7: Start the Server
```bash
python manage.py runserver
```

## 🌐 Accessing Admin Interfaces

### Django Admin (User Management)
- **URL**: http://localhost:8000/admin/
- **Purpose**: Manage users, groups, and all models
- **Login**: Use the superuser credentials you created

### Custom Admin Dashboard (Menu Management)
- **URL**: http://localhost:8000/login/
- **Purpose**: Manage restaurant menus and notices
- **Login**: Use the same superuser credentials

### Main Website
- **URL**: http://localhost:8000/
- **Purpose**: View the public website

## 🎯 What You Can Do in Django Admin

1. **Users**: Create/edit user accounts
2. **Restaurant Branches**: Add new restaurant locations
3. **Menu Categories**: Organize menu items
4. **Menu Items**: Add dishes with images and details
5. **Notices**: Create announcements and promotions

## 🎯 What You Can Do in Custom Dashboard

1. **Select Branch**: Choose which restaurant to manage
2. **Add Menu Items**: Upload images, set prices, add descriptions
3. **Manage Notices**: Create promotions, events, announcements
4. **View Statistics**: See overview of your restaurant data

## ❗ Troubleshooting

### If you get "Pillow not installed" error:
```bash
pip install Pillow
```

### If migrations fail:
```bash
python manage.py makemigrations frontend
python manage.py migrate
```

### If you forget your admin password:
```bash
python manage.py createsuperuser
```
Create a new admin user with a different username.

### If the server won't start:
- Check if another server is running on port 8000
- Try: `python manage.py runserver 8001`

## 🎉 Success!

Once setup is complete, you'll be able to:
- ✅ Login to Django admin at `/admin/`
- ✅ Login to custom dashboard at `/login/`
- ✅ Add menu items for different branches
- ✅ Upload images for menu items
- ✅ Create notices and announcements
- ✅ Manage your restaurant data efficiently

## 📞 Next Steps

1. Create your admin user following the steps above
2. Login to both admin interfaces
3. Add some test menu items with images
4. Create a sample notice or promotion
5. Visit the main website to see your changes!
