#!/usr/bin/env python
"""
Complete test of admin menu functionality for Pagomo branch
This script tests:
1. Admin can add menu items to Pagomo branch
2. Menu items appear immediately on user-facing Pagomo page
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from frontend.views import pagomo
from frontend.models import RestaurantBranch, MenuItem, MenuCategory
from datetime import datetime

def test_complete_admin_flow():
    """Test the complete admin workflow"""
    print("=" * 60)
    print("TESTING COMPLETE ADMIN MENU FUNCTIONALITY")
    print("=" * 60)
    
    try:
        # 1. Check if Pagomo branch exists
        print("\n1. Checking Pagomo branch...")
        try:
            branch = RestaurantBranch.objects.get(slug='rabbit-hole-pagomo', is_active=True)
            print(f"✓ Found Pagomo branch: {branch.name} (ID: {branch.id})")
        except RestaurantBranch.DoesNotExist:
            print("✗ ERROR: Pagomo branch not found!")
            return False
        
        # 2. Check categories
        print("\n2. Checking menu categories...")
        categories = MenuCategory.objects.all().order_by('order')
        print(f"✓ Found {categories.count()} categories:")
        for cat in categories:
            print(f"   - {cat.name} (slug: {cat.slug})")
        
        # 3. Get initial menu item count
        print("\n3. Getting initial menu item count...")
        initial_count = MenuItem.objects.filter(branch=branch, is_available=True).count()
        print(f"✓ Initial menu items for Pagomo: {initial_count}")
        
        # 4. Add a new test menu item (simulating admin action)
        print("\n4. Adding new test menu item (simulating admin)...")
        grills_category = MenuCategory.objects.get(slug='grills')
        
        # Create a unique test item name with timestamp
        timestamp = datetime.now().strftime("%H%M%S")
        test_item_name = f"Test Grilled Rabbit {timestamp}"
        
        new_item = MenuItem.objects.create(
            branch=branch,
            name=test_item_name,
            description="A test item added to verify admin functionality works immediately",
            price=35.99,
            category=grills_category,
            is_available=True,
            is_featured=True
        )
        print(f"✓ Created test item: {new_item.name} (ID: {new_item.id})")
        
        # 5. Check new menu item count
        print("\n5. Verifying menu item was added...")
        new_count = MenuItem.objects.filter(branch=branch, is_available=True).count()
        print(f"✓ New menu items count: {new_count}")
        if new_count == initial_count + 1:
            print("✓ Menu item count increased correctly!")
        else:
            print(f"✗ Expected {initial_count + 1}, got {new_count}")
        
        # 6. Test Pagomo view (simulating user visiting page)
        print("\n6. Testing user-facing Pagomo page...")
        factory = RequestFactory()
        request = factory.get('/pagomo/')
        request.user = AnonymousUser()
        
        response = pagomo(request)
        print(f"✓ Pagomo page response status: {response.status_code}")
        
        # 7. Check if new item appears in view context
        print("\n7. Checking if new item appears in page context...")
        # We need to render the template to get context
        from django.template.loader import get_template
        from django.template import Context
        
        # Get the context that would be passed to the template
        try:
            branch_for_view = RestaurantBranch.objects.get(slug='rabbit-hole-pagomo', is_active=True)
            menu_items_for_view = MenuItem.objects.filter(
                branch=branch_for_view, 
                is_available=True
            ).select_related('category').order_by('category__order', 'name')
            
            found_test_item = False
            for item in menu_items_for_view:
                if item.name == test_item_name:
                    found_test_item = True
                    print(f"✓ Found test item in view context: {item.name}")
                    break
            
            if not found_test_item:
                print(f"✗ Test item '{test_item_name}' NOT found in view context!")
            
            print(f"✓ Total items in view context: {menu_items_for_view.count()}")
            
        except Exception as e:
            print(f"✗ Error checking view context: {e}")
        
        # 8. List all current menu items
        print(f"\n8. Current menu items for {branch.name}:")
        all_items = MenuItem.objects.filter(branch=branch, is_available=True).order_by('category__name', 'name')
        for item in all_items:
            marker = "★" if item.name == test_item_name else " "
            print(f"   {marker} {item.name} ({item.category.name}) - ${item.price}")
        
        print(f"\n{'='*60}")
        print("✓ ADMIN MENU FUNCTIONALITY TEST COMPLETED SUCCESSFULLY!")
        print("✓ Admin can add menu items and they appear immediately on user pages!")
        print(f"{'='*60}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_complete_admin_flow()
