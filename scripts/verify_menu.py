import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from django.test import RequestFactory
from frontend.models import RestaurantBranch, MenuCategory, MenuItem
from frontend.views import rabbithole, pagomo

def test_system():
    print("=" * 60)
    print("RUNNING MENU SYSTEM VERIFICATION")
    print("=" * 60)
    
    # 1. Check Branches & Categories
    branches = RestaurantBranch.objects.filter(is_active=True)
    print(f"[OK] Active branches found: {branches.count()}")
    for b in branches:
        print(f"   - Branch: {b.name} (slug: {b.slug})")
        
    categories = MenuCategory.objects.all()
    print(f"[OK] Categories found: {categories.count()}")
    for c in categories:
        print(f"   - Category: {c.name} (slug: {c.slug})")

    # 2. Check Menu Items
    total_items = MenuItem.objects.count()
    print(f"[OK] Total existing menu items in DB: {total_items}")
    
    # 3. Test creating a new menu item via model
    branch = branches.first()
    category = categories.first()
    test_item = MenuItem.objects.create(
        branch=branch,
        category=category,
        name="Verification Dish",
        description="Juicy rabbit grilled with secret herbs",
        price=18.50,
        is_available=True,
        is_featured=True,
    )
    print(f"[OK] Created temporary item: {test_item.name} (ID: {test_item.id})")
    
    # 4. Test rabbithole and pagomo views
    rf = RequestFactory()
    
    req_rabbithole = rf.get('/rabbithole/')
    resp_rabbithole = rabbithole(req_rabbithole)
    assert resp_rabbithole.status_code == 200, f"rabbithole status was {resp_rabbithole.status_code}"
    print(f"[OK] rabbithole view rendered successfully (Status 200)")
    
    req_pagomo = rf.get('/pagomo/')
    resp_pagomo = pagomo(req_pagomo)
    assert resp_pagomo.status_code == 200, f"pagomo view rendered successfully (Status 200)"
    print(f"[OK] pagomo view rendered successfully (Status 200)")
    
    # 5. Clean up test item
    test_item.delete()
    print(f"[OK] Cleaned up temporary test item")
    
    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    test_system()
