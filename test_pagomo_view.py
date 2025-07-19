#!/usr/bin/env python
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

def test_pagomo_view():
    """Test the Pagomo view directly"""
    try:
        # Create a request factory
        factory = RequestFactory()
        
        # Create a GET request to the pagomo page
        request = factory.get('/pagomo/')
        request.user = AnonymousUser()
        
        print("Testing Pagomo view...")
        
        # Call the view
        response = pagomo(request)
        
        print(f"Response status: {response.status_code}")
        
        # Check the context
        if hasattr(response, 'context_data'):
            context = response.context_data
            print(f"Branch in context: {context.get('branch')}")
            print(f"Menu items count: {len(context.get('menu_items', []))}")
            print(f"Categories count: {len(context.get('categories', []))}")
        
        # Check database directly
        print("\nDatabase check:")
        try:
            branch = RestaurantBranch.objects.get(slug='rabbit-hole-pagomo', is_active=True)
            print(f"Found branch: {branch.name} (ID: {branch.id})")
            
            items = MenuItem.objects.filter(branch=branch, is_available=True)
            print(f"Menu items for branch: {items.count()}")
            for item in items:
                print(f"  - {item.name} ({item.category.name}) - ${item.price}")
                
        except RestaurantBranch.DoesNotExist:
            print("ERROR: Pagomo branch not found in database!")
            
        print("\nAll branches in database:")
        branches = RestaurantBranch.objects.all()
        for branch in branches:
            print(f"  - {branch.name} (slug: {branch.slug}, active: {branch.is_active})")
            
        return True
        
    except Exception as e:
        print(f"Error testing view: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_pagomo_view()
