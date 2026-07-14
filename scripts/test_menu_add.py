#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from frontend.models import RestaurantBranch, MenuItem, MenuCategory

def test_add_menu_item():
    try:
        # Get the Pagomo branch
        branch = RestaurantBranch.objects.get(slug='rabbit-hole-pagomo')
        print(f"Found branch: {branch.name} (ID: {branch.id})")
        
        # Get a category (e.g., Grills)
        category = MenuCategory.objects.get(slug='grills')
        print(f"Found category: {category.name} (ID: {category.id})")
        
        # Create a new menu item
        new_item = MenuItem.objects.create(
            branch=branch,
            name="Test Grilled Rabbit",
            description="A delicious test item",
            price=25.99,
            category=category,
            is_available=True,
            is_featured=False
        )
        print(f"Created new menu item: {new_item.name} (ID: {new_item.id})")
        
        # List all menu items for this branch
        items = MenuItem.objects.filter(branch=branch, is_available=True)
        print(f"\nAll menu items for {branch.name}:")
        for item in items:
            print(f"  - {item.name} ({item.category.name}) - ${item.price}")
            
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    test_add_menu_item()
