from django.core.management.base import BaseCommand
from frontend.models import RestaurantBranch, MenuItem, MenuCategory

class Command(BaseCommand):
    help = 'Add a test menu item to verify admin functionality'

    def handle(self, *args, **options):
        try:
            # Get the Pagomo branch
            branch = RestaurantBranch.objects.get(slug='rabbit-hole-pagomo')
            self.stdout.write(f"Found branch: {branch.name} (ID: {branch.id})")
            
            # Get a category (e.g., Grills)
            category = MenuCategory.objects.get(slug='grills')
            self.stdout.write(f"Found category: {category.name} (ID: {category.id})")
            
            # Check if test item already exists
            existing_item = MenuItem.objects.filter(
                branch=branch, 
                name="Admin Test Grilled Rabbit"
            ).first()
            
            if existing_item:
                self.stdout.write(f"Test item already exists: {existing_item.name}")
            else:
                # Create a new menu item
                new_item = MenuItem.objects.create(
                    branch=branch,
                    name="Admin Test Grilled Rabbit",
                    description="A test item added via admin to verify functionality",
                    price=29.99,
                    category=category,
                    is_available=True,
                    is_featured=True
                )
                self.stdout.write(f"Created new test menu item: {new_item.name} (ID: {new_item.id})")
            
            # List all menu items for this branch
            items = MenuItem.objects.filter(branch=branch, is_available=True)
            self.stdout.write(f"\nAll menu items for {branch.name} ({items.count()} total):")
            for item in items:
                self.stdout.write(f"  - {item.name} ({item.category.name}) - ${item.price}")
                
            self.stdout.write(self.style.SUCCESS('\nTest completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
