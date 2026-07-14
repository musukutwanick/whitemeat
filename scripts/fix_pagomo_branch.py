import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from frontend.models import RestaurantBranch, MenuCategory, MenuItem

# Check existing branches
print("=== EXISTING BRANCHES ===")
branches = RestaurantBranch.objects.all()
for branch in branches:
    print(f"ID: {branch.id}, Name: {branch.name}, Slug: '{branch.slug}', Active: {branch.is_active}")

print("\n=== MENU ITEMS BY BRANCH ===")
for branch in branches:
    items = MenuItem.objects.filter(branch=branch)
    print(f"\nBranch: {branch.name} (ID: {branch.id})")
    print(f"Total items: {items.count()}")
    for item in items:
        print(f"  - {item.name} (Available: {item.is_available})")

# If there's a branch but it doesn't have slug 'pagomo', let's fix it
if branches.exists():
    first_branch = branches.first()
    if first_branch.slug != 'pagomo':
        print(f"\n=== FIXING BRANCH SLUG ===")
        print(f"Changing branch '{first_branch.name}' slug from '{first_branch.slug}' to 'pagomo'")
        first_branch.slug = 'pagomo'
        first_branch.save()
        print("✅ Branch slug updated!")
        
        # Also update the name if needed
        if 'pagomo' not in first_branch.name.lower():
            first_branch.name = 'Rabbit Hole Pagomo'
            first_branch.save()
            print("✅ Branch name updated!")
else:
    print("\n=== CREATING PAGOMO BRANCH ===")
    branch = RestaurantBranch.objects.create(
        name='Rabbit Hole Pagomo',
        slug='pagomo',
        address='Pagomo, Harare, Zimbabwe',
        phone='+263 772 333 369',
        email='pagomo@rabbithole.zw',
        is_active=True
    )
    print(f"✅ Created branch: {branch.name} (ID: {branch.id})")

print("\n=== FINAL STATUS ===")
try:
    pagomo_branch = RestaurantBranch.objects.get(slug='pagomo')
    print(f"✅ Pagomo branch found: {pagomo_branch.name} (ID: {pagomo_branch.id})")
    
    available_items = MenuItem.objects.filter(branch=pagomo_branch, is_available=True)
    print(f"Available menu items: {available_items.count()}")
    
    for item in available_items:
        print(f"  - {item.name} (${item.price}) - {item.category.name}")
        
except RestaurantBranch.DoesNotExist:
    print("❌ Still no Pagomo branch found!")
