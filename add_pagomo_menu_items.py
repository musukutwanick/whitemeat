#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whitemeat_backend.settings')
django.setup()

from frontend.models import MenuItem, MenuCategory, RestaurantBranch
from decimal import Decimal

def add_sample_menu_items():
    """Add sample menu items to Pagomo branch"""
    
    # Get Pagomo branch
    pagomo_branch = RestaurantBranch.objects.filter(name__icontains='pagomo').first()
    if not pagomo_branch:
        print("Pagomo branch not found. Creating it...")
        pagomo_branch = RestaurantBranch.objects.create(
            name="The Rabbit Hole PaGomo",
            slug="pagomo",
            address="PaGomo Shopping Center, Harare",
            phone="+263 772 333 369",
            email="pagomo@rabbitholeharare.zw",
            is_active=True
        )
        print(f"✓ Created branch: {pagomo_branch.name}")
    
    # Get categories
    categories = {
        'grills': MenuCategory.objects.filter(slug='grills').first(),
        'stews': MenuCategory.objects.filter(slug='stews').first(), 
        'sides': MenuCategory.objects.filter(slug='sides').first(),
        'snacks': MenuCategory.objects.filter(slug='snacks').first(),
    }
    
    # Create missing categories if needed
    if not categories['grills']:
        categories['grills'] = MenuCategory.objects.create(name='Grills', slug='grills', order=1)
    if not categories['stews']:
        categories['stews'] = MenuCategory.objects.create(name='Stews', slug='stews', order=2)
    if not categories['sides']:
        categories['sides'] = MenuCategory.objects.create(name='Sides', slug='sides', order=3)
    if not categories['snacks']:
        categories['snacks'] = MenuCategory.objects.create(name='Snacks', slug='snacks', order=4)
    
    # Sample menu items
    sample_items = [
        {
            'name': 'Grilled Rabbit with Herbs',
            'description': 'Tender rabbit meat grilled to perfection with fresh herbs and spices. Served with roasted vegetables.',
            'price': Decimal('18.50'),
            'category': categories['grills'],
            'is_featured': True,
            'preparation_time': 25,
            'calories': 320,
            'ingredients': 'Rabbit meat, rosemary, thyme, garlic, olive oil, roasted vegetables',
            'allergens': 'None'
        },
        {
            'name': 'BBQ Rabbit Ribs',
            'description': 'Succulent rabbit ribs marinated in our signature BBQ sauce and grilled over open flame.',
            'price': Decimal('22.00'),
            'category': categories['grills'],
            'is_featured': False,
            'preparation_time': 30,
            'calories': 410,
            'ingredients': 'Rabbit ribs, BBQ sauce, paprika, brown sugar, vinegar',
            'allergens': 'Contains gluten'
        },
        {
            'name': 'Traditional Rabbit Stew',
            'description': 'Hearty rabbit stew cooked with local vegetables and traditional Zimbabwean spices.',
            'price': Decimal('16.75'),
            'category': categories['stews'],
            'is_featured': True,
            'preparation_time': 45,
            'calories': 380,
            'ingredients': 'Rabbit meat, potatoes, carrots, onions, traditional spices',
            'allergens': 'None'
        },
        {
            'name': 'Rabbit Curry',
            'description': 'Aromatic rabbit curry with coconut milk and curry spices. Served with rice.',
            'price': Decimal('19.25'),
            'category': categories['stews'],
            'is_featured': False,
            'preparation_time': 35,
            'calories': 450,
            'ingredients': 'Rabbit meat, coconut milk, curry powder, onions, rice',
            'allergens': 'None'
        },
        {
            'name': 'Rabbit Sadza',
            'description': 'Traditional Zimbabwean staple served as a perfect complement to our rabbit dishes.',
            'price': Decimal('4.50'),
            'category': categories['sides'],
            'is_featured': False,
            'preparation_time': 15,
            'calories': 180,
            'ingredients': 'Maize meal, salt, water',
            'allergens': 'Gluten-free'
        },
        {
            'name': 'Grilled Vegetables',
            'description': 'Fresh seasonal vegetables grilled and seasoned with herbs.',
            'price': Decimal('8.75'),
            'category': categories['sides'],
            'is_featured': False,
            'preparation_time': 12,
            'calories': 120,
            'ingredients': 'Mixed vegetables, olive oil, herbs, salt',
            'allergens': 'None'
        },
        {
            'name': 'Mini Rabbit Pies',
            'description': 'Bite-sized rabbit pies perfect for sharing. Served with dipping sauce.',
            'price': Decimal('12.50'),
            'category': categories['snacks'],
            'is_featured': True,
            'preparation_time': 20,
            'calories': 280,
            'ingredients': 'Rabbit meat, pastry, herbs, vegetables',
            'allergens': 'Contains gluten, eggs'
        },
        {
            'name': 'Rabbit Biltong',
            'description': 'Traditional dried rabbit meat, a perfect snack with local flavor.',
            'price': Decimal('9.00'),
            'category': categories['snacks'],
            'is_featured': False,
            'preparation_time': 5,
            'calories': 150,
            'ingredients': 'Rabbit meat, salt, spices',
            'allergens': 'None'
        }
    ]
    
    # Clear existing menu items for this branch
    MenuItem.objects.filter(branch=pagomo_branch).delete()
    
    # Create menu items
    created_count = 0
    for item_data in sample_items:
        menu_item = MenuItem.objects.create(
            branch=pagomo_branch,
            name=item_data['name'],
            description=item_data['description'],
            price=item_data['price'],
            category=item_data['category'],
            is_featured=item_data['is_featured'],
            is_available=True,
            preparation_time=item_data['preparation_time'],
            calories=item_data['calories'],
            ingredients=item_data['ingredients'],
            allergens=item_data['allergens']
        )
        created_count += 1
        print(f"✓ Created: {menu_item.name} - ${menu_item.price}")
    
    print(f"\n🎉 Successfully added {created_count} menu items to {pagomo_branch.name}!")
    
    # Show summary
    print(f"\n📊 Branch Summary:")
    print(f"Branch: {pagomo_branch.name}")
    print(f"Address: {pagomo_branch.address}")
    print(f"Total Menu Items: {MenuItem.objects.filter(branch=pagomo_branch).count()}")
    
    for category in categories.values():
        if category:
            count = MenuItem.objects.filter(branch=pagomo_branch, category=category).count()
            print(f"- {category.name}: {count} items")

if __name__ == "__main__":
    add_sample_menu_items()
