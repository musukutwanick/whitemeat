from django.core.management.base import BaseCommand
from frontend.models import RestaurantBranch, MenuCategory, MenuItem

class Command(BaseCommand):
    help = 'Check database content for debugging'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DATABASE DEBUG INFO ==='))
        
        # Check branches
        self.stdout.write(self.style.SUCCESS('\n📍 BRANCHES:'))
        branches = RestaurantBranch.objects.all()
        if branches:
            for branch in branches:
                self.stdout.write(f"  ID: {branch.id}, Name: {branch.name}, Slug: {branch.slug}, Active: {branch.is_active}")
        else:
            self.stdout.write(self.style.ERROR("  No branches found!"))
        
        # Check categories
        self.stdout.write(self.style.SUCCESS('\n📂 CATEGORIES:'))
        categories = MenuCategory.objects.all()
        if categories:
            for cat in categories:
                self.stdout.write(f"  ID: {cat.id}, Name: {cat.name}, Slug: {cat.slug}, Order: {cat.order}")
        else:
            self.stdout.write(self.style.ERROR("  No categories found!"))
        
        # Check menu items
        self.stdout.write(self.style.SUCCESS('\n🍽️ ALL MENU ITEMS:'))
        items = MenuItem.objects.select_related('branch', 'category').all()
        if items:
            for item in items:
                self.stdout.write(f"  ID: {item.id}, Name: {item.name}, Branch: {item.branch.name} (ID: {item.branch.id}), Category: {item.category.name}, Available: {item.is_available}, Price: ${item.price}")
        else:
            self.stdout.write(self.style.ERROR("  No menu items found!"))
        
        # Check Pagomo specific
        self.stdout.write(self.style.SUCCESS('\n🏪 PAGOMO BRANCH ANALYSIS:'))
        try:
            pagomo_branch = RestaurantBranch.objects.get(slug='pagomo')
            self.stdout.write(f"  ✅ Pagomo branch found: ID {pagomo_branch.id}, Active: {pagomo_branch.is_active}")
            
            pagomo_items = MenuItem.objects.filter(branch=pagomo_branch)
            self.stdout.write(f"  📊 Total items for Pagomo: {pagomo_items.count()}")
            
            available_items = pagomo_items.filter(is_available=True)
            self.stdout.write(f"  📊 Available items for Pagomo: {available_items.count()}")
            
            if available_items:
                self.stdout.write("  📋 Available items:")
                for item in available_items:
                    self.stdout.write(f"    - {item.name} (${item.price}) - {item.category.name}")
            
        except RestaurantBranch.DoesNotExist:
            self.stdout.write(self.style.ERROR("  ❌ Pagomo branch not found!"))
        
        self.stdout.write(self.style.SUCCESS('\n=== END DEBUG INFO ==='))
