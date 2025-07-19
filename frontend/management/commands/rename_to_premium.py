from django.core.management.base import BaseCommand
from frontend.models import RestaurantBranch

class Command(BaseCommand):
    help = 'Update branch name to Rabbit Hole Premium'

    def handle(self, *args, **options):
        try:
            # Try to find and update the main branch
            branch = RestaurantBranch.objects.get(slug='rabbit-hole-main')
            old_name = branch.name
            branch.name = "Rabbit Hole Premium"
            branch.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated branch name from "{old_name}" to "{branch.name}"'
                )
            )
            
        except RestaurantBranch.DoesNotExist:
            # Create the branch if it doesn't exist
            branch = RestaurantBranch.objects.create(
                name="Rabbit Hole Premium",
                slug="rabbit-hole-main",
                address="Belvedere, Harare, Zimbabwe",
                phone="+263 123 456 789",
                email="premium@rabbithole.co.zw",
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created new branch: "{branch.name}" with slug "{branch.slug}"'
                )
            )
        
        # Display all branches
        self.stdout.write('\nAll restaurant branches:')
        branches = RestaurantBranch.objects.all()
        for b in branches:
            self.stdout.write(f'  - {b.name} (slug: {b.slug})')
            
        self.stdout.write(
            self.style.SUCCESS('\nBranch update completed!')
        )
