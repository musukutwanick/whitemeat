#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from frontend.models import RestaurantBranch, MenuItem

def show_admin_summary():
    """Show current branches and menu items for admin reference"""
    
    print("🏪 RESTAURANT BRANCHES:")
    print("=" * 50)
    
    branches = RestaurantBranch.objects.filter(is_active=True)
    
    if not branches.exists():
        print("❌ No active branches found!")
        print("\nCreating sample branches...")
        
        # Create sample branches
        branches_data = [
            {
                'name': 'The Rabbit Hole PaGomo',
                'slug': 'pagomo',
                'address': 'PaGomo Shopping Center, Harare',
                'phone': '+263 772 333 369',
                'email': 'pagomo@rabbitholeharare.zw'
            },
            {
                'name': 'The Rabbit Hole Belvedere',
                'slug': 'belvedere',
                'address': 'Belvedere, Harare',
                'phone': '+263 779 521 665',
                'email': 'belvedere@rabbitholeharare.zw'
            }
        ]
        
        for branch_data in branches_data:
            branch, created = RestaurantBranch.objects.get_or_create(
                slug=branch_data['slug'],
                defaults=branch_data
            )
            if created:
                print(f"✓ Created: {branch.name}")
            else:
                print(f"✓ Found: {branch.name}")
        
        branches = RestaurantBranch.objects.filter(is_active=True)
    
    for branch in branches:
        menu_count = MenuItem.objects.filter(branch=branch).count()
        featured_count = MenuItem.objects.filter(branch=branch, is_featured=True).count()
        
        print(f"\n📍 {branch.name}")
        print(f"   Address: {branch.address}")
        print(f"   Phone: {branch.phone}")
        print(f"   Email: {branch.email}")
        print(f"   Menu Items: {menu_count} total, {featured_count} featured")
        
        if menu_count > 0:
            print("   Recent Items:")
            recent_items = MenuItem.objects.filter(branch=branch).order_by('-created_at')[:3]
            for item in recent_items:
                status = "⭐ FEATURED" if item.is_featured else "📝 Standard"
                availability = "✅ Available" if item.is_available else "❌ Unavailable"
                print(f"   - {item.name} (${item.price}) - {status} - {availability}")
    
    print(f"\n📊 ADMIN SUMMARY:")
    print("=" * 50)
    print(f"Total Active Branches: {branches.count()}")
    print(f"Total Menu Items: {MenuItem.objects.count()}")
    print(f"Featured Items: {MenuItem.objects.filter(is_featured=True).count()}")
    print(f"Available Items: {MenuItem.objects.filter(is_available=True).count()}")
    
    print(f"\n🔗 ADMIN ACCESS:")
    print("=" * 50)
    print("1. Login: http://127.0.0.1:8000/login/")
    print("   Username: admin")
    print("   Password: admin123")
    print("")
    print("2. Dashboard: http://127.0.0.1:8000/dashboard/")
    print("3. Menu Management: http://127.0.0.1:8000/dashboard/branch-selection/")
    print("")
    print("4. Direct Branch Access:")
    for branch in branches:
        print(f"   - {branch.name}: http://127.0.0.1:8000/dashboard/branch/{branch.id}/menu/")

if __name__ == "__main__":
    show_admin_summary()
