import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from frontend.models import RestaurantBranch, MenuItem, MenuCategory

# Check and update branch name
try:
    print("Checking existing branches...")
    branches = RestaurantBranch.objects.all()
    
    if not branches.exists():
        print("No branches found. Creating branches...")
        
        # Create Rabbit Hole Premium branch
        premium_branch = RestaurantBranch.objects.create(
            name="Rabbit Hole Premium",
            slug="rabbit-hole-main",
            address="Belvedere, Harare, Zimbabwe",
            phone="+263 123 456 789",
            email="premium@rabbithole.co.zw",
            is_active=True
        )
        print(f"✓ Created: {premium_branch.name}")
        
        # Create Rabbit Hole PaGomo branch if it doesn't exist
        pagomo_branch, created = RestaurantBranch.objects.get_or_create(
            slug="rabbit-hole-pagomo",
            defaults={
                'name': "Rabbit Hole - PaGomo",
                'address': "PaGomo, Harare, Zimbabwe",
                'phone': "+263 987 654 321",
                'email': "pagomo@rabbithole.co.zw",
                'is_active': True
            }
        )
        if created:
            print(f"✓ Created: {pagomo_branch.name}")
        else:
            print(f"✓ Already exists: {pagomo_branch.name}")
    
    else:
        print(f"Found {branches.count()} existing branches:")
        for branch in branches:
            print(f"  - {branch.name} (slug: {branch.slug})")
        
        # Update main branch to Premium
        try:
            main_branch = RestaurantBranch.objects.get(slug="rabbit-hole-main")
            old_name = main_branch.name
            main_branch.name = "Rabbit Hole Premium"
            main_branch.save()
            print(f"✓ Updated '{old_name}' to '{main_branch.name}'")
        except RestaurantBranch.DoesNotExist:
            print("Main branch not found, creating it...")
            premium_branch = RestaurantBranch.objects.create(
                name="Rabbit Hole Premium",
                slug="rabbit-hole-main",
                address="Belvedere, Harare, Zimbabwe",
                phone="+263 123 456 789",
                email="premium@rabbithole.co.zw",
                is_active=True
            )
            print(f"✓ Created: {premium_branch.name}")
    
    # Show final state
    print("\nFinal branch list:")
    all_branches = RestaurantBranch.objects.all()
    for branch in all_branches:
        menu_count = MenuItem.objects.filter(branch=branch).count()
        print(f"  - {branch.name} (slug: {branch.slug}, menu items: {menu_count})")
    
    print("\n✅ Branch name update completed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
