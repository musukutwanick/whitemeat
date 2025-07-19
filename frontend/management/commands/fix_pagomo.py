from django.core.management.base import BaseCommand
from frontend.models import RestaurantBranch, MenuCategory, MenuItem

class Command(BaseCommand):
    help = 'Fix Pagomo branch slug and show debug info'

    def handle(self, *args, **options):
        self.stdout.write('=== CURRENT BRANCHES ===')
        branches = RestaurantBranch.objects.all()
        
        if not branches.exists():
            self.stdout.write(self.style.WARNING('No branches found! Creating Pagomo branch...'))
            branch = RestaurantBranch.objects.create(
                name='Rabbit Hole Pagomo',
                slug='pagomo',
                address='Pagomo, Harare, Zimbabwe',
                phone='+263 772 333 369',
                email='pagomo@rabbithole.zw',
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Created branch: {branch.name} (ID: {branch.id})'))
        else:
            for branch in branches:
                self.stdout.write(f'ID: {branch.id}, Name: {branch.name}, Slug: "{branch.slug}", Active: {branch.is_active}')
                
                # Fix slug if needed
                if branch.slug != 'pagomo':
                    self.stdout.write(self.style.WARNING(f'Fixing slug for branch {branch.name}...'))
                    branch.slug = 'pagomo'
                    if 'pagomo' not in branch.name.lower():
                        branch.name = 'Rabbit Hole Pagomo'
                    branch.save()
                    self.stdout.write(self.style.SUCCESS(f'✅ Updated branch: {branch.name}'))
        
        self.stdout.write('\n=== MENU ITEMS ===')
        items = MenuItem.objects.select_related('branch', 'category').all()
        if items:
            for item in items:
                self.stdout.write(f'ID: {item.id}, Name: {item.name}, Branch: {item.branch.name} (ID: {item.branch.id}), Available: {item.is_available}')
        else:
            self.stdout.write(self.style.WARNING('No menu items found'))
        
        # Check Pagomo specifically
        self.stdout.write('\n=== PAGOMO ANALYSIS ===')
        try:
            pagomo_branch = RestaurantBranch.objects.get(slug='pagomo')
            self.stdout.write(self.style.SUCCESS(f'✅ Pagomo branch: {pagomo_branch.name} (ID: {pagomo_branch.id})'))
            
            available_items = MenuItem.objects.filter(branch=pagomo_branch, is_available=True)
            self.stdout.write(f'Available items: {available_items.count()}')
            
            for item in available_items:
                self.stdout.write(f'  - {item.name} (${item.price}) - {item.category.name}')
                
        except RestaurantBranch.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Pagomo branch still not found!'))
