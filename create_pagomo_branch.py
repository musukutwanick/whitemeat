import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from frontend.models import RestaurantBranch, MenuCategory, MenuItem
from decimal import Decimal

def create_pagomo_branch():
    """Create Pagomo branch if it doesn't exist"""
    print("Creating Pagomo branch...")
    
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
        print(f"✅ Created new branch: {pagomo_branch.name} (ID: {pagomo_branch.id})")
    else:
        print(f"✅ Branch already exists: {pagomo_branch.name} (ID: {pagomo_branch.id})")
    
    return pagomo_branch

def check_existing_data():
    """Check what data currently exists"""
    print("\n=== CURRENT DATABASE STATUS ===")
    
    print("\n📍 Branches:")
    branches = RestaurantBranch.objects.all()
    if branches:
        for branch in branches:
            print(f"  ID: {branch.id}, Name: {branch.name}, Slug: {branch.slug}, Active: {branch.is_active}")
    else:
        print("  No branches found")
    
    print("\n📂 Categories:")
    categories = MenuCategory.objects.all()
    if categories:
        for cat in categories:
            print(f"  ID: {cat.id}, Name: {cat.name}, Slug: {cat.slug}")
    else:
        print("  No categories found")
    
    print("\n🍽️ Menu Items:")
    items = MenuItem.objects.all()
    if items:
        for item in items:
            print(f"  ID: {item.id}, Name: {item.name}, Branch: {item.branch.name} (ID: {item.branch.id}), Available: {item.is_available}")
    else:
        print("  No menu items found")

if __name__ == '__main__':
    check_existing_data()
    
    # Create Pagomo branch
    pagomo_branch = create_pagomo_branch()
    
    print("\n=== AFTER SETUP ===")
    check_existing_data()
    
    # Show specific Pagomo data
    try:
        pagomo = RestaurantBranch.objects.get(slug='pagomo')
        pagomo_items = MenuItem.objects.filter(branch=pagomo, is_available=True)
        print(f"\n🏪 Pagomo Branch Analysis:")
        print(f"  Branch: {pagomo.name} (ID: {pagomo.id})")
        print(f"  Active: {pagomo.is_active}")
        print(f"  Available menu items: {pagomo_items.count()}")
        
        if pagomo_items:
            print("  Items:")
            for item in pagomo_items:
                print(f"    - {item.name} (${item.price})")
    except RestaurantBranch.DoesNotExist:
        print("❌ Still no Pagomo branch found!")
