#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from frontend.models import MenuCategory

def update_menu_categories():
    """Update menu categories to match the required ones"""
    
    # Delete existing categories
    MenuCategory.objects.all().delete()
    print("Deleted existing categories")
    
    # Create the new categories
    categories = [
        {'name': 'All', 'slug': 'all', 'description': 'All menu items', 'order': 0},
        {'name': 'Grills', 'slug': 'grills', 'description': 'Grilled dishes', 'order': 1},
        {'name': 'Stews+Sides', 'slug': 'stews-sides', 'description': 'Stews and side dishes', 'order': 2},
        {'name': 'Snacks', 'slug': 'snacks', 'description': 'Light snacks and appetizers', 'order': 3},
        {'name': 'Sides', 'slug': 'sides', 'description': 'Side dishes', 'order': 4},
    ]
    
    for cat_data in categories:
        category = MenuCategory.objects.create(
            name=cat_data['name'],
            slug=cat_data['slug'],
            description=cat_data['description'],
            order=cat_data['order']
        )
        print(f"Created category: {category.name}")
    
    print(f"\nTotal categories created: {MenuCategory.objects.count()}")

if __name__ == "__main__":
    update_menu_categories()
