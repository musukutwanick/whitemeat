"""
Setup script for The White Meat Company Admin Dashboard

This script creates initial data for restaurant branches and menu categories.
Run this after applying migrations:

1. python manage.py makemigrations frontend
2. python manage.py migrate
3. python manage.py shell < setup_data.py

"""

from frontend.models import RestaurantBranch, MenuCategory

# Create Restaurant Branches
branches_data = [
    {
        'name': 'Rabbit Hole - Main Branch',
        'slug': 'rabbit-hole-main',
        'address': 'Belvedere, Harare, Zimbabwe',
        'phone': '+263 772 333 369',
        'email': 'info@whitemeatcompany.zw'
    },
    {
        'name': 'Rabbit Hole - PaGomo',
        'slug': 'rabbit-hole-pagomo',
        'address': 'PaGomo, Harare, Zimbabwe',
        'phone': '+263 772 333 370',
        'email': 'pagomo@rabbitholerestaurant.com'
    }
]

# Create Menu Categories
categories_data = [
    {'name': 'Starters', 'slug': 'starters', 'description': 'Appetizers and light bites', 'order': 1},
    {'name': 'Mains', 'slug': 'goch-goch', 'description': 'Main course dishes', 'order': 2},
    {'name': 'Stews', 'slug': 'stews', 'description': 'Traditional stews and hearty dishes', 'order': 3},
    {'name': 'Breakfast', 'slug': 'breakfast', 'description': 'Morning breakfast options', 'order': 4},
    {'name': 'Desserts', 'slug': 'desserts', 'description': 'Sweet treats and desserts', 'order': 5},
    {'name': 'Drinks', 'slug': 'drinks', 'description': 'Beverages and refreshments', 'order': 6},
    {'name': 'Starches', 'slug': 'starch', 'description': 'Rice, sadza, and other starches', 'order': 7},
]

print("Creating restaurant branches...")
for branch_data in branches_data:
    branch, created = RestaurantBranch.objects.get_or_create(
        slug=branch_data['slug'],
        defaults=branch_data
    )
    if created:
        print(f"✓ Created branch: {branch.name}")
    else:
        print(f"→ Branch already exists: {branch.name}")

print("\nCreating menu categories...")
for category_data in categories_data:
    category, created = MenuCategory.objects.get_or_create(
        slug=category_data['slug'],
        defaults=category_data
    )
    if created:
        print(f"✓ Created category: {category.name}")
    else:
        print(f"→ Category already exists: {category.name}")

print("\n🎉 Setup complete!")
print("\nYou can now:")
print("1. Create a superuser: python manage.py createsuperuser")
print("2. Run the server: python manage.py runserver")
print("3. Visit /login/ to access the admin dashboard")
print("4. Start adding menu items to your restaurant branches!")
