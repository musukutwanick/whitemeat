#!/usr/bin/env python3
"""
Script to set up Pagomo branch and sample menu items for testing dynamic menu functionality.
Run this script to ensure the restaurant has menu items that can be managed by the admin.
"""
import os
import sys
import django
from decimal import Decimal

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from frontend.models import RestaurantBranch, MenuCategory, MenuItem

def setup_branch_and_menu():
    """Set up Pagomo branch and sample menu items"""
    
    # Create or get Pagomo branch
    pagomo_branch, created = RestaurantBranch.objects.get_or_create(
        slug='pagomo',
        defaults={
            'name': 'Rabbit Hole Pagomo',
            'address': 'Pagomo, Harare, Zimbabwe',
            'phone': '+263 772 333 369',
            'email': 'pagomo@rabbithole.zw',
            'is_active': True,
        }
    )
    
    if created:
        print(f"✅ Created new branch: {pagomo_branch.name}")
    else:
        print(f"✅ Branch already exists: {pagomo_branch.name}")
    
    # Create categories if they don't exist
    categories_data = [
        {'name': 'Grills', 'slug': 'grills', 'order': 1},
        {'name': 'Stews+Sides', 'slug': 'stews-sides', 'order': 2},
        {'name': 'Snacks', 'slug': 'snacks', 'order': 3},
        {'name': 'Sides', 'slug': 'sides', 'order': 4},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = MenuCategory.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        categories[cat_data['slug']] = category
        if created:
            print(f"✅ Created category: {category.name}")
        else:
            print(f"✅ Category already exists: {category.name}")
    
    # Sample menu items to create
    menu_items_data = [
        {
            'name': 'Grilled Full Rabbit',
            'description': 'Our signature grilled rabbit prepared to perfection with special herbs and spices.',
            'price': Decimal('12.00'),
            'category': 'grills',
            'image_filename': 'full-rabbit.jpg',
            'is_available': True,
            'is_featured': True,
        },
        {
            'name': 'Grilled Half Rabbit',
            'description': 'Half portion of our delicious grilled rabbit, perfect for lighter appetites.',
            'price': Decimal('6.00'),
            'category': 'grills',
            'image_filename': 'half-rabbit.jpg',
            'is_available': True,
            'is_featured': False,
        },
        {
            'name': 'Traditional Rabbit Stew',
            'description': 'Traditional rabbit stew served with sadza and fresh vegetables.',
            'price': Decimal('8.00'),
            'category': 'stews-sides',
            'image_filename': 'rabbit-stew.jpg',
            'is_available': True,
            'is_featured': False,
        },
        {
            'name': 'Rabbit Curry',
            'description': 'Spicy rabbit curry with coconut rice and traditional spices.',
            'price': Decimal('9.00'),
            'category': 'stews-sides',
            'image_filename': 'rabbit-curry.jpg',
            'is_available': True,
            'is_featured': False,
        },
        {
            'name': 'Mini Rabbit Pies',
            'description': 'Perfect for sharing - delicious mini pies filled with seasoned rabbit meat.',
            'price': Decimal('5.00'),
            'category': 'snacks',
            'image_filename': 'rabbit-pies.jpg',
            'is_available': True,
            'is_featured': False,
        },
        {
            'name': 'Spiced Rabbit Wings',
            'description': 'Crispy rabbit wings with our special spice blend and dipping sauce.',
            'price': Decimal('4.00'),
            'category': 'snacks',
            'image_filename': 'rabbit-wings.jpg',
            'is_available': True,
            'is_featured': False,
        },
        {
            'name': 'Traditional Sadza',
            'description': 'Traditional Zimbabwean staple made from corn meal.',
            'price': Decimal('2.00'),
            'category': 'sides',
            'image_filename': 'sadza.jpg',
            'is_available': True,
            'is_featured': False,
        },
        {
            'name': 'Fresh Vegetable Mix',
            'description': 'Seasonal fresh vegetables steamed to perfection.',
            'price': Decimal('3.00'),
            'category': 'sides',
            'image_filename': 'vegetables.jpg',
            'is_available': True,
            'is_featured': False,
        },
    ]
    
    # Create menu items
    created_count = 0
    for item_data in menu_items_data:
        category_slug = item_data.pop('category')
        category = categories[category_slug]
        
        menu_item, created = MenuItem.objects.get_or_create(
            branch=pagomo_branch,
            name=item_data['name'],
            defaults={
                **item_data,
                'category': category,
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Created menu item: {menu_item.name} (${menu_item.price})")
        else:
            print(f"✅ Menu item already exists: {menu_item.name}")
    
    print(f"\n🎉 Setup complete!")
    print(f"📊 Branch: {pagomo_branch.name}")
    print(f"📊 Categories: {MenuCategory.objects.count()}")
    print(f"📊 Total menu items for Pagomo: {MenuItem.objects.filter(branch=pagomo_branch).count()}")
    print(f"📊 New items created: {created_count}")
    print(f"\n🔧 Admin can now manage these items at: /admin/dashboard/")
    print(f"🍽️ Users can view the menu at: /pagomo/ and /rabbithole/")

if __name__ == '__main__':
    setup_branch_and_menu()
