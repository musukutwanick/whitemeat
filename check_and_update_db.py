#!/usr/bin/env python
import os
import sys
import django
import sqlite3

def check_database():
    """Check what's currently in the database"""
    try:
        # Connect to the SQLite database
        db_path = 'db.sqlite3'
        
        # Check if database file exists
        if not os.path.exists(db_path):
            print("✗ Database file 'db.sqlite3' not found!")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='frontend_restaurantbranch'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("✗ Table 'frontend_restaurantbranch' does not exist!")
            print("You may need to run migrations first.")
            conn.close()
            return False
        
        # Check current branches
        cursor.execute("SELECT id, name, slug, is_active FROM frontend_restaurantbranch")
        branches = cursor.fetchall()
        
        print(f"Found {len(branches)} branches in database:")
        for branch in branches:
            print(f"  ID: {branch[0]}, Name: '{branch[1]}', Slug: '{branch[2]}', Active: {branch[3]}")
        
        # If we found the main branch, update it
        if branches:
            for branch in branches:
                if branch[2] == 'rabbit-hole-main':  # slug
                    print(f"\nUpdating branch '{branch[1]}' to 'Rabbit Hole Premium'...")
                    cursor.execute(
                        "UPDATE frontend_restaurantbranch SET name = ? WHERE id = ?",
                        ("Rabbit Hole Premium", branch[0])
                    )
                    conn.commit()
                    print("✓ Branch name updated successfully!")
                    break
            else:
                print("\n✗ No branch with slug 'rabbit-hole-main' found!")
        else:
            print("\n✗ No branches found in database!")
            print("You may need to run the setup script first.")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    check_database()
