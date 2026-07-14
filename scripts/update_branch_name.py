#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from frontend.models import RestaurantBranch

def update_branch_name():
    """Update the Rabbit Hole Main Branch to Rabbit Hole Premium"""
    try:
        # Find the main branch
        branch = RestaurantBranch.objects.get(slug='rabbit-hole-main')
        print(f"Found branch: {branch.name} (slug: {branch.slug})")
        
        # Update the name
        old_name = branch.name
        branch.name = "Rabbit Hole Premium"
        branch.save()
        
        print(f"✓ Updated branch name from '{old_name}' to '{branch.name}'")
        
        # Verify the change
        updated_branch = RestaurantBranch.objects.get(slug='rabbit-hole-main')
        print(f"✓ Verified: {updated_branch.name}")
        
        # List all branches
        print("\nAll restaurant branches:")
        branches = RestaurantBranch.objects.all()
        for b in branches:
            print(f"  - {b.name} (slug: {b.slug}, active: {b.is_active})")
            
        return True
        
    except RestaurantBranch.DoesNotExist:
        print("✗ Error: Rabbit Hole Main Branch not found!")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    update_branch_name()
