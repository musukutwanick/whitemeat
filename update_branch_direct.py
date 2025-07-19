#!/usr/bin/env python
import os
import sys
import django
import sqlite3

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

def update_branch_directly():
    """Update branch name directly in SQLite database"""
    try:
        # Connect to the SQLite database
        db_path = 'db.sqlite3'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current branches
        cursor.execute("SELECT id, name, slug, is_active FROM frontend_restaurantbranch")
        branches = cursor.fetchall()
        
        print("Current branches in database:")
        for branch in branches:
            print(f"  ID: {branch[0]}, Name: {branch[1]}, Slug: {branch[2]}, Active: {branch[3]}")
        
        # Update the main branch name
        cursor.execute(
            "UPDATE frontend_restaurantbranch SET name = ? WHERE slug = ?",
            ("Rabbit Hole Premium", "rabbit-hole-main")
        )
        
        # Check if update was successful
        if cursor.rowcount > 0:
            print(f"\n✓ Successfully updated {cursor.rowcount} branch(es)")
        else:
            print("\n✗ No branches were updated (slug 'rabbit-hole-main' not found)")
        
        # Commit the changes
        conn.commit()
        
        # Verify the update
        cursor.execute("SELECT id, name, slug FROM frontend_restaurantbranch WHERE slug = ?", ("rabbit-hole-main",))
        updated_branch = cursor.fetchone()
        
        if updated_branch:
            print(f"✓ Verified update: {updated_branch[1]} (slug: {updated_branch[2]})")
        else:
            print("✗ Could not verify update")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def verify_with_django():
    """Verify the update using Django ORM"""
    try:
        from frontend.models import RestaurantBranch
        
        print("\nVerifying with Django ORM:")
        branches = RestaurantBranch.objects.all()
        for branch in branches:
            print(f"  - {branch.name} (slug: {branch.slug}, active: {branch.is_active})")
        
        return True
    except Exception as e:
        print(f"✗ Django verification error: {e}")
        return False

if __name__ == '__main__':
    print("Updating Rabbit Hole branch name to 'Rabbit Hole Premium'...")
    if update_branch_directly():
        verify_with_django()
    else:
        print("Update failed!")
