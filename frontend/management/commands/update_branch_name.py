from django.core.management.base import BaseCommand
from frontend.models import RestaurantBranch

class Command(BaseCommand):
    help = 'Update Rabbit Hole Main Branch name to Rabbit Hole Premium'

    def handle(self, *args, **options):
        try:
            # Find the main branch
            branch = RestaurantBranch.objects.get(slug='rabbit-hole-main')
            self.stdout.write(f"Found branch: {branch.name} (slug: {branch.slug})")
            
            # Update the name
            old_name = branch.name
            branch.name = "Rabbit Hole Premium"
            branch.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated branch name from "{old_name}" to "{branch.name}"')
            )
            
            # Verify the change
            updated_branch = RestaurantBranch.objects.get(slug='rabbit-hole-main')
            self.stdout.write(f"Verified: {updated_branch.name}")
            
            # List all branches
            self.stdout.write("\nAll restaurant branches:")
            branches = RestaurantBranch.objects.all()
            for b in branches:
                self.stdout.write(f"  - {b.name} (slug: {b.slug}, active: {b.is_active})")
                
        except RestaurantBranch.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Rabbit Hole Main Branch not found!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {e}')
            )
